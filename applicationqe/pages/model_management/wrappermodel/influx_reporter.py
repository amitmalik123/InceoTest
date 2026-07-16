"""WrapperModel-specific Allure to InfluxDB reporter for Grafana metrics."""

from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.crypto_utils import decrypt_value


class AllureToInfluxDB:
    """Push WrapperModel execution metrics from Allure JSON to InfluxDB."""

    def __init__(self) -> None:
        config = self._load_config()

        self.url = os.getenv("INFLUXDB_URL", config.get("influxdb_url", ""))
        self.org = os.getenv("INFLUXDB_ORG", config.get("influxdb_org", ""))
        self.bucket = os.getenv("INFLUXDB_BUCKET", config.get("influxdb_bucket", ""))

        token_value = os.getenv("INFLUXDB_TOKEN", config.get("influxdb_token", ""))
        self.token = decrypt_value(token_value) if token_value else ""

        auto_push_env = os.getenv("INFLUXDB_AUTO_PUSH")
        if auto_push_env is not None:
            self.auto_push = auto_push_env.strip().lower() in ("1", "true", "yes", "on")
        else:
            self.auto_push = bool(config.get("auto_push", False))

        self.project_name = os.getenv("PROJECT_NAME", config.get("project_name", "MM_Wrapper_Model"))
        self.environment = os.getenv("ENVIRONMENT", os.getenv("TEST_ENV", "unknown"))
        self.build_id = os.getenv("BUILD_ID", os.getenv("BUILD_BUILDID", "local"))
        self.test_app = os.getenv("TEST_APP", config.get("test_app", "wrapper"))
        self.allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "reports/allure-results")

        # WrapperModel-specific Grafana/Influx customizations (backward compatible defaults).
        self.measurement = config.get("measurement", "test_execution")
        self.secondary_measurement = config.get("secondary_measurement", "test_execution")
        self.grafana_dashboard = config.get("grafana_dashboard", "WrapperModel")
        self.grafana_folder = config.get("grafana_folder", "QE/WrapperModel")
        self.team = config.get("team", "QA")
        self.module = config.get("module", "ModelManagement")
        self.submodule = config.get("submodule", "WrapperModel")

    def _build_point(self, measurement: str, metrics: dict[str, int | float]):
        """Create a standardized InfluxDB point for WrapperModel metrics."""
        from influxdb_client import Point, WritePrecision

        return (
            Point(measurement)
            # Keep existing tag names and add aliases for Grafana dashboard compatibility.
            .tag("project_name", self.project_name)
            .tag("project", self.project_name)
            .tag("environment", self.environment)
            .tag("env", self.environment)
            .tag("test_app", self.test_app)
            .tag("app", self.test_app)
            .tag("build_id", self.build_id)
            .tag("team", self.team)
            .tag("module", self.module)
            .tag("submodule", self.submodule)
            .tag("grafana_dashboard", self.grafana_dashboard)
            .tag("grafana_folder", self.grafana_folder)
            .field("total", int(metrics["total"]))
            .field("passed", int(metrics["passed"]))
            .field("failed", int(metrics["failed"]))
            .field("broken", int(metrics["broken"]))
            .field("skipped", int(metrics["skipped"]))
            .field("duration_seconds", int(metrics["duration_seconds"]))
            .field("pass_rate", float(metrics["pass_rate"]))
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )

    @staticmethod
    def _load_config() -> dict[str, Any]:
        root = Path(__file__).resolve().parents[3]
        cfg = root / "config" / "model-management" / "wrappermodel" / "influxdb_config.json"
        if not cfg.exists():
            return {}
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            print(f"Wrapper Influx reporter: could not read config {cfg}: {exc}")
            return {}

    def _read_allure_results(self) -> list[dict[str, Any]]:
        result_files = glob.glob(os.path.join(self.allure_results_dir, "*-result.json"))
        if not result_files:
            return []

        latest_by_name: dict[str, dict[str, Any]] = {}
        for file_path in result_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue

            name = data.get("name") or file_path
            previous = latest_by_name.get(name)
            if previous is None or data.get("stop", 0) > previous.get("stop", 0):
                latest_by_name[name] = data

        return list(latest_by_name.values())

    @staticmethod
    def _calculate_metrics(results: list[dict[str, Any]]) -> dict[str, int | float]:
        metrics: dict[str, int | float] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "broken": 0,
            "skipped": 0,
            "duration_seconds": 0,
            "pass_rate": 0.0,
        }

        duration_ms = 0
        for test in results:
            metrics["total"] += 1
            status = str(test.get("status", "unknown")).lower()
            if status == "passed":
                metrics["passed"] += 1
            elif status == "failed":
                metrics["failed"] += 1
            elif status == "broken":
                metrics["broken"] += 1
            elif status == "skipped":
                metrics["skipped"] += 1

            start = int(test.get("start") or 0)
            stop = int(test.get("stop") or 0)
            if stop > start:
                duration_ms += stop - start

        metrics["duration_seconds"] = int(duration_ms / 1000)

        testable_total = int(metrics["total"]) - int(metrics["skipped"])
        if testable_total > 0:
            pass_count = int(metrics["passed"])
            metrics["pass_rate"] = round((pass_count / testable_total) * 100, 2)

        return metrics

    def run(self) -> None:
        if not self.auto_push:
            print("Wrapper Influx reporter: auto_push is disabled")
            return

        if not (self.url and self.org and self.bucket and self.token):
            print("Wrapper Influx reporter: missing required config (url/org/bucket/token)")
            return

        results = self._read_allure_results()
        if not results:
            print("Wrapper Influx reporter: no Allure result files found")
            return

        metrics = self._calculate_metrics(results)

        try:
            from influxdb_client import InfluxDBClient, Point, WritePrecision
        except Exception as exc:
            print(f"Wrapper Influx reporter: influxdb-client import failed: {exc}")
            return

        points = [self._build_point(self.measurement, metrics)]
        if self.secondary_measurement and self.secondary_measurement != self.measurement:
            points.append(self._build_point(self.secondary_measurement, metrics))

        try:
            with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
                write_api = client.write_api()
                write_api.write(bucket=self.bucket, org=self.org, record=points)
            print(
                "Wrapper Influx reporter: pushed metrics "
                f"(measurement={self.measurement}, project={self.project_name}, "
                f"total={int(metrics['total'])}, passed={int(metrics['passed'])})"
            )
        except Exception as exc:
            print(f"Wrapper Influx reporter: push failed: {exc}")
