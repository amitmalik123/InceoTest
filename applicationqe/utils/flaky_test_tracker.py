"""
Flaky Test Tracker - Detects and reports flaky tests to InfluxDB

Tracks:
- Tests that pass after retries (flaky)
- Tests with inconsistent failures
- Retry counts and patterns
- Flaky test history
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


def load_influxdb_config():
    """Load InfluxDB configuration from config file or environment variables"""
    config_path = Path(__file__).parent.parent / "config" / "influxdb_config.json"

    # Try to load from config file first
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                return {
                    "url": config.get("influxdb_url", "http://localhost:8086"),
                    "token": config.get("influxdb_token", ""),
                    "org": config.get("influxdb_org", "default"),
                    "bucket": config.get("influxdb_bucket", "test-results"),
                }
        except Exception as e:
            print(f"⚠️  Error loading InfluxDB config file: {e}")

    # Fall back to environment variables
    return {
        "url": os.getenv("INFLUXDB_URL", "http://localhost:8086"),
        "token": os.getenv("INFLUXDB_TOKEN", ""),
        "org": os.getenv("INFLUXDB_ORG", "default"),
        "bucket": os.getenv("INFLUXDB_BUCKET", "test-results"),
    }


class FlakyTestTracker:
    """Track and report flaky tests to InfluxDB"""

    def __init__(self):
        influx_config = load_influxdb_config()
        self.influx_url = influx_config["url"]
        self.influx_token = influx_config["token"]
        self.influx_org = influx_config["org"]
        self.influx_bucket = influx_config["bucket"]
        from config.oam.settings import get_settings

        self.environment = os.getenv("ENVIRONMENT", get_settings().env)
        self.build_id = os.getenv("BUILD_ID", "local")

        # Track flaky tests during session
        self.flaky_tests: Dict[str, Dict] = {}

    def record_flaky_test(
        self,
        test_name: str,
        test_id: str,
        total_attempts: int,
        failed_attempts: int,
        final_status: str,
        duration_ms: int,
        error_message: Optional[str] = None,
    ):
        """Record a flaky test occurrence"""
        self.flaky_tests[test_id] = {
            "test_name": test_name,
            "test_id": test_id,
            "total_attempts": total_attempts,
            "failed_attempts": failed_attempts,
            "final_status": final_status,
            "duration_ms": duration_ms,
            "error_message": error_message or "",
            "timestamp": datetime.now(),
            "environment": self.environment,
            "build_id": self.build_id,
        }

        print("\n⚠️  FLAKY TEST DETECTED:")
        print(f"   Test: {test_name}")
        print(f"   Attempts: {total_attempts} (failed: {failed_attempts})")
        print(f"   Final Status: {final_status}")
        print(f"   Duration: {duration_ms}ms")
        if error_message:
            print(f"   Error: {error_message[:100]}...")

    def create_influx_points(self) -> List[str]:
        """Create InfluxDB line protocol points for flaky tests"""
        points = []
        timestamp = int(datetime.now().timestamp() * 1e9)  # nanoseconds

        for test_id, test_data in self.flaky_tests.items():
            # Escape special characters in tag values
            test_name_escaped = test_data["test_name"].replace(",", "\\,").replace(" ", "\\ ")
            test_id_escaped = test_id.replace(",", "\\,").replace(" ", "\\ ")
            env_escaped = test_data["environment"].replace(",", "\\,").replace(" ", "\\ ")

            tags = (
                f"test_name={test_name_escaped},"
                f"test_id={test_id_escaped},"
                f"environment={env_escaped},"
                f'build_id="{test_data["build_id"]}",'
                f'final_status={test_data["final_status"]}'
            )

            # Escape special characters in field values
            error_msg = test_data["error_message"].replace('"', '\\"')[:200]  # Limit length

            fields = (
                f'total_attempts={test_data["total_attempts"]}i,'
                f'failed_attempts={test_data["failed_attempts"]}i,'
                f'success_attempts={test_data["total_attempts"] - test_data["failed_attempts"]}i,'
                f'duration_ms={test_data["duration_ms"]}i,'
                f'flaky_rate={(test_data["failed_attempts"] / test_data["total_attempts"]) * 100:.2f},'
                f'error_message="{error_msg}"'
            )

            point = f"flaky_tests,{tags} {fields} {timestamp}"
            points.append(point)

        return points

    def push_to_influxdb(self) -> bool:
        """Push flaky test metrics to InfluxDB"""
        if not self.flaky_tests:
            print("✓ No flaky tests detected in this run")
            return True

        if not self.influx_token:
            print("⚠️  INFLUXDB_TOKEN not set. Skipping flaky test tracking.")
            return False

        try:
            client = InfluxDBClient(
                url=self.influx_url, token=self.influx_token, org=self.influx_org
            )

            write_api = client.write_api(write_options=SYNCHRONOUS)
            points = self.create_influx_points()

            print(f"\n📊 Pushing {len(points)} flaky test metric(s) to InfluxDB...")
            for point in points:
                write_api.write(bucket=self.influx_bucket, record=point)

            client.close()
            print("✓ Successfully pushed flaky test metrics to InfluxDB")
            return True

        except Exception as e:
            print(f"❌ Error pushing flaky tests to InfluxDB: {e}")
            return False

    def get_flaky_summary(self) -> Dict:
        """Get summary of flaky tests in current session"""
        return {
            "total_flaky_tests": len(self.flaky_tests),
            "flaky_tests": [
                {
                    "name": data["test_name"],
                    "attempts": data["total_attempts"],
                    "failed": data["failed_attempts"],
                    "status": data["final_status"],
                }
                for data in self.flaky_tests.values()
            ],
        }


# Global tracker instance
_tracker = None


def get_tracker() -> FlakyTestTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = FlakyTestTracker()
    return _tracker
