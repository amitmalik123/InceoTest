"""Push pytest JUnit summary metrics to InfluxDB for Grafana dashboards.

Expected environment variables:
  INFLUXDB_URL
  INFLUXDB_TOKEN
  INFLUXDB_ORG
  INFLUXDB_BUCKET
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def parse_junit_summary(junit_path: str) -> dict:
    root = ET.parse(junit_path).getroot()

    # Handle both <testsuite> and <testsuites>
    if root.tag == "testsuite":
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        skipped = int(root.attrib.get("skipped", 0))
        duration = float(root.attrib.get("time", 0.0))
    else:
        tests = failures = errors = skipped = 0
        duration = 0.0
        for suite in root.findall("testsuite"):
            tests += int(suite.attrib.get("tests", 0))
            failures += int(suite.attrib.get("failures", 0))
            errors += int(suite.attrib.get("errors", 0))
            skipped += int(suite.attrib.get("skipped", 0))
            duration += float(suite.attrib.get("time", 0.0))

    passed = max(tests - failures - errors - skipped, 0)
    return {
        "total": tests,
        "passed": passed,
        "failed": failures,
        "errors": errors,
        "skipped": skipped,
        "duration_seconds": duration,
    }


def push_summary(summary: dict, measurement: str, run_name: str) -> int:
    url = os.getenv("INFLUXDB_URL")
    token = os.getenv("INFLUXDB_TOKEN")
    org = os.getenv("INFLUXDB_ORG")
    bucket = os.getenv("INFLUXDB_BUCKET")

    if not all([url, token, org, bucket]):
        print("[influx] Skipping push: missing one or more INFLUXDB_* environment variables.")
        return 0

    try:
        from influxdb_client import InfluxDBClient, Point
        from influxdb_client.client.write_api import SYNCHRONOUS
    except Exception as exc:
        print(f"[influx] Skipping push: influxdb-client unavailable ({exc}).")
        return 0

    point = (
        Point(measurement)
        .tag("suite", run_name)
        .tag("host", socket.gethostname())
        .field("total", int(summary["total"]))
        .field("passed", int(summary["passed"]))
        .field("failed", int(summary["failed"]))
        .field("errors", int(summary["errors"]))
        .field("skipped", int(summary["skipped"]))
        .field("duration_seconds", float(summary["duration_seconds"]))
        .time(datetime.now(timezone.utc))
    )

    with InfluxDBClient(url=url, token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=point)

    print(
        "[influx] Metrics pushed "
        f"(suite={run_name}, total={summary['total']}, passed={summary['passed']}, "
        f"failed={summary['failed']}, skipped={summary['skipped']})."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", required=True, help="Path to pytest JUnit XML report")
    parser.add_argument(
        "--measurement",
        default="ui_test_summary",
        help="Influx measurement name (default: ui_test_summary)",
    )
    parser.add_argument(
        "--run-name",
        default="model-management-add-model",
        help="Logical test run/suite name tag",
    )
    args = parser.parse_args()

    if not os.path.exists(args.junit):
        print(f"[influx] JUnit report not found: {args.junit}")
        return 1

    summary = parse_junit_summary(args.junit)
    return push_summary(summary, args.measurement, args.run_name)


if __name__ == "__main__":
    sys.exit(main())
