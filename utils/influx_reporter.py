#!/usr/bin/env python3
"""
InfluxDB Reporter: Parses Allure JSON results and pushes metrics to InfluxDB
"""

import glob
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from utils.crypto_utils import decrypt_value


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
                    "token": decrypt_value(config.get("influxdb_token", "")),
                    "org": config.get("influxdb_org", "default"),
                    "bucket": config.get("influxdb_bucket", "test-results"),
                    "project_name": config.get("project_name", "unknown"),
                    "auto_push": config.get("auto_push", False),
                }
        except Exception as e:
            print(f"⚠️  Error loading InfluxDB config file: {e}")

    # Fall back to environment variables
    return {
        "url": os.getenv("INFLUXDB_URL", "http://localhost:8086"),
        "token": os.getenv("INFLUXDB_TOKEN", ""),
        "org": os.getenv("INFLUXDB_ORG", "default"),
        "bucket": os.getenv("INFLUXDB_BUCKET", "test-results"),
        "project_name": os.getenv("PROJECT_NAME", "unknown"),
        "auto_push": os.getenv("INFLUXDB_AUTO_PUSH", "false").lower() == "true",
    }


class AllureToInfluxDB:
    """Convert Allure test results to InfluxDB metrics"""

    def __init__(self):
        influx_config = load_influxdb_config()
        self.influx_url = influx_config["url"]
        self.influx_token = influx_config["token"]
        self.influx_org = influx_config["org"]
        self.influx_bucket = influx_config["bucket"]
        self.project_name = influx_config.get("project_name", "unknown")
        self.auto_push = influx_config.get("auto_push", False)
        self.allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "./target/allure-results")
        self.build_id = os.getenv("BUILD_ID", "local")
        self.build_reason = os.getenv("BUILD_REASON", "Manual")
        self.environment = os.getenv("ENVIRONMENT", "test11")

        # Azure Pipelines variables for artifact links
        self.system_team_foundation_collection_uri = os.getenv(
            "SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", ""
        )
        self.system_team_project = os.getenv("SYSTEM_TEAMPROJECT", "")
        self.build_buildid = os.getenv("BUILD_BUILDID", self.build_id)

    def get_artifact_urls(self) -> Dict[str, str]:
        """Generate artifact download URLs for Azure Pipelines"""
        urls = {}

        if not self.system_team_foundation_collection_uri or not self.system_team_project:
            return urls

        base_url = f"{self.system_team_foundation_collection_uri.rstrip('/')}/{self.system_team_project}/_build/results"

        urls["AllureReport"] = f"{base_url}?buildId={self.build_buildid}&artifactName=AllureReport"

        return urls

    def read_allure_results(self) -> Dict[str, Any]:
        """Read Allure results from JSON files"""
        results = {"tests": [], "containers": [], "groups": []}

        if not os.path.exists(self.allure_results_dir):
            print(f"⚠️  Allure results directory not found: {self.allure_results_dir}")
            return results

        # Read test results - track by test name to use only the latest result
        json_files = glob.glob(os.path.join(self.allure_results_dir, "*-result.json"))
        print(f"📂 Found {len(json_files)} total test result files")

        # Dictionary to store latest result for each test (by test name)
        latest_results = {}

        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    test_data = json.load(f)
                    test_name = test_data.get("name", "")
                    test_data.get("uuid", "")

                    if test_name:
                        # Keep the latest result (by timestamp/stop time)
                        if test_name not in latest_results:
                            latest_results[test_name] = test_data
                        else:
                            # Compare stop times to keep the latest
                            current_stop = latest_results[test_name].get("stop", 0)
                            new_stop = test_data.get("stop", 0)
                            if new_stop > current_stop:
                                latest_results[test_name] = test_data
            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        # Add unique results to output
        results["tests"] = list(latest_results.values())
        duplicate_count = len(json_files) - len(results["tests"])
        print(
            f"⚠️  Deduplicated to {len(results['tests'])} unique test(s) by name (skipped {duplicate_count} duplicates/retries)"
        )

        # Print unique tests
        for test_data in results["tests"]:
            test_name = test_data.get("name", "unknown")
            status = test_data.get("status", "unknown")
            print(f"  - {status.upper()}: {test_name}")

        # Read containers
        for json_file in glob.glob(os.path.join(self.allure_results_dir, "*-container.json")):
            try:
                with open(json_file, "r") as f:
                    results["containers"].append(json.load(f))
            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        # Read groups
        for json_file in glob.glob(os.path.join(self.allure_results_dir, "groups.json")):
            try:
                with open(json_file, "r") as f:
                    results["groups"].append(json.load(f))
            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        return results

    def calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test metrics from Allure results"""
        tests = results.get("tests", [])

        metrics = {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "flaky": 0,
            "retried": 0,
            "total_duration": 0,
            "pass_rate": 0,
        }

        status_counts = {}
        test_details = []

        for test in tests:
            status = test.get("status", "unknown")
            status_details = test.get("statusDetails", {})
            test_name = test.get("name", "unknown")

            # Track raw statuses for debugging
            status_counts[status] = status_counts.get(status, 0) + 1

            # Check if test is flaky
            is_flaky = status_details.get("flaky", False)

            # Count based on final status
            if status == "passed":
                metrics["passed"] += 1
                if is_flaky:
                    metrics["flaky"] += 1
                    test_details.append(f"  ✓ {test_name} [PASSED - FLAKY]")
                else:
                    test_details.append(f"  ✓ {test_name} [PASSED]")
            elif status in ("failed", "broken"):
                metrics["failed"] += 1
                test_details.append(f"  ✗ {test_name} [{status.upper()}]")
            elif status == "skipped":
                metrics["skipped"] += 1
                test_details.append(f"  - {test_name} [SKIPPED]")
            else:
                # Unknown status
                test_details.append(f"  ? {test_name} [{status.upper()}]")

            # Check for retried tests (tests that were retried)
            history = test.get("historyId", "")
            if history:
                # Test has history - indicates retries
                metrics["retried"] += 1

            # Track duration (ms from Allure, convert to seconds)
            duration = test.get("stop", 0) - test.get("start", 0)
            metrics["total_duration"] += duration

        # Convert total duration from ms to seconds
        metrics["total_duration"] = round(metrics["total_duration"] / 1000, 2)

        # Calculate pass rate (excluding skipped tests from calculation)
        testable_total = metrics["total"] - metrics["skipped"]
        if testable_total > 0:
            metrics["pass_rate"] = (metrics["passed"] / testable_total) * 100

        # Debug: Show status distribution
        print(f"\n🔍 Raw Status Distribution: {status_counts}")
        print("\n📋 Test Details:")
        for detail in test_details:
            print(detail)

        return metrics

    def create_influx_points(
        self, metrics: Dict[str, Any], artifact_urls: Dict[str, str]
    ) -> List[str]:
        """Create InfluxDB line protocol points from metrics"""
        timestamp = int(datetime.now().timestamp() * 1e9)  # nanoseconds

        tags = f'build_id="{self.build_id}",environment="{self.environment}",build_reason="{self.build_reason}",project_name="{self.project_name}"'

        # Main test execution metrics
        points = [
            f"test_execution1,{tags} "
            f'total={metrics["total"]}i,'
            f'passed={metrics["passed"]}i,'
            f'failed={metrics["failed"]}i,'
            f'skipped={metrics["skipped"]}i,'
            f'flaky={metrics["flaky"]}i,'
            f'retried={metrics["retried"]}i,'
            f'pass_rate={metrics["pass_rate"]:.2f},'
            f'total_duration={metrics["total_duration"]} '
            f"{timestamp}"
        ]

        # Flaky test quality metric
        if metrics["total"] > 0:
            flaky_rate = (metrics["flaky"] / metrics["total"]) * 100
            retry_rate = (metrics["retried"] / metrics["total"]) * 100

            points.append(
                f"test_quality,{tags} "
                f'flaky_count={metrics["flaky"]}i,'
                f"flaky_rate={flaky_rate:.2f},"
                f'retried_count={metrics["retried"]}i,'
                f"retry_rate={retry_rate:.2f} "
                f"{timestamp}"
            )

        # Artifact URLs as a separate measurement
        if artifact_urls:
            artifact_tags = tags
            artifact_data = ",".join([f'{name}="{url}"' for name, url in artifact_urls.items()])
            points.append(f"test_artifacts,{artifact_tags} " f"{artifact_data} " f"{timestamp}")

        return points

    def push_to_influxdb(self, points: List[str]) -> bool:
        """Push metrics to InfluxDB"""
        if not self.influx_token:
            print("⚠️  INFLUXDB_TOKEN not set. Skipping InfluxDB push.")
            return False

        try:
            client = InfluxDBClient(
                url=self.influx_url, token=self.influx_token, org=self.influx_org
            )

            write_api = client.write_api(write_options=SYNCHRONOUS)

            print(f"📊 Pushing {len(points)} metric(s) to InfluxDB ({self.influx_url})...")
            for point in points:
                print(f"  - {point[:80]}...")
                write_api.write(bucket=self.influx_bucket, record=point)

            client.close()
            print("✓ Successfully pushed metrics to InfluxDB")
            return True

        except Exception as e:
            print(f"❌ Error pushing to InfluxDB: {e}")
            return False

    def run(self):
        """Main execution"""
        print("=" * 70)
        print("🚀 Allure to InfluxDB Reporter")
        print("=" * 70)
        print(f"InfluxDB URL: {self.influx_url}")
        print(f"Allure Results Dir: {self.allure_results_dir}")
        print(f"Environment: {self.environment}")
        print(f"Build ID: {self.build_id}")
        print()

        # Read Allure results
        results = self.read_allure_results()
        if not results["tests"]:
            print("⚠️  No test results found. Skipping InfluxDB push.")
            return

        print(f"📂 Found {len(results['tests'])} test result(s)")

        # Calculate metrics
        metrics = self.calculate_metrics(results)
        print("\n📈 Test Execution Metrics:")
        print(f"  Total Tests: {metrics['total']}")
        print(f"  Passed: {metrics['passed']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Skipped: {metrics['skipped']}")
        print(f"  Flaky Tests: {metrics['flaky']}")
        print(f"  Pass Rate: {metrics['pass_rate']:.2f}%")
        print(f"  Total Duration: {metrics['total_duration']}s")

        print("\n⚠️  Test Quality Metrics:")
        if metrics["total"] > 0:
            flaky_rate = (metrics["flaky"] / metrics["total"]) * 100
            print(f"  Flaky Rate: {flaky_rate:.2f}%")
            retry_rate = (metrics["retried"] / metrics["total"]) * 100
            print(f"  Retried Tests: {metrics['retried']}")
            print(f"  Retry Rate: {retry_rate:.2f}%")

        # Get artifact URLs
        artifact_urls = self.get_artifact_urls()
        if artifact_urls:
            print("\n🔗 Pipeline Artifacts:")
            for name, url in artifact_urls.items():
                print(f"  {name}: {url[:80]}...")
        print()

        # Create and push points
        points = self.create_influx_points(metrics, artifact_urls)
        self.push_to_influxdb(points)
        print("=" * 70)


if __name__ == "__main__":
    reporter = AllureToInfluxDB()
    reporter.run()
