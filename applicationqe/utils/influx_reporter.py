"""Push UI test summary metrics to InfluxDB for Grafana dashboards.

The reporter reads test outputs from:
1) Allure result JSON files (`*-result.json`) when available
2) JUnit XML as fallback

Expected environment variables (for push):
  INFLUXDB_URL
  INFLUXDB_TOKEN
  INFLUXDB_ORG
  INFLUXDB_BUCKET

Optional environment variables (tags/metadata):
  ALLURE_RESULTS_DIR
  JUNIT_XML_PATH
  ENVIRONMENT
  BUILD_ID
  BUILD_REASON
  BUILD_SOURCEBRANCHNAME
  TEAM_NAME
  STAGE_NAME
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


def _to_int(value, default: int = 0) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		return default


def _to_float(value, default: float = 0.0) -> float:
	try:
		return float(value)
	except (TypeError, ValueError):
		return default


def parse_allure_summary(allure_dir: Path) -> Dict[str, float]:
	"""Parse Allure result files and return a normalized summary."""
	if not allure_dir.exists() or not allure_dir.is_dir():
		return {}

	result_files = list(allure_dir.glob("*-result.json"))
	if not result_files:
		return {}

	counts = {
		"passed": 0,
		"failed": 0,
		"broken": 0,
		"skipped": 0,
		"unknown": 0,
	}
	duration_ms = 0

	for result_file in result_files:
		try:
			data = json.loads(result_file.read_text(encoding="utf-8"))
		except (json.JSONDecodeError, OSError):
			continue

		status = str(data.get("status", "unknown")).lower()
		if status not in counts:
			status = "unknown"
		counts[status] += 1

		time_block = data.get("time") or {}
		start_ms = _to_int(time_block.get("start"), 0)
		stop_ms = _to_int(time_block.get("stop"), 0)
		if stop_ms > start_ms > 0:
			duration_ms += stop_ms - start_ms

	total = sum(counts.values())
	failed_total = counts["failed"] + counts["broken"]

	return {
		"total": total,
		"passed": counts["passed"],
		"failed": failed_total,
		"errors": counts["broken"],
		"skipped": counts["skipped"],
		"unknown": counts["unknown"],
		"duration_seconds": duration_ms / 1000.0,
		"source": "allure",
	}


def parse_junit_summary(junit_path: Path) -> Dict[str, float]:
	"""Parse JUnit XML summary and return a normalized summary."""
	if not junit_path.exists():
		return {}

	root = ET.parse(junit_path).getroot()

	# Handle both <testsuite> and <testsuites>
	if root.tag == "testsuite":
		tests = _to_int(root.attrib.get("tests"), 0)
		failures = _to_int(root.attrib.get("failures"), 0)
		errors = _to_int(root.attrib.get("errors"), 0)
		skipped = _to_int(root.attrib.get("skipped"), 0)
		duration = _to_float(root.attrib.get("time"), 0.0)
	else:
		tests = failures = errors = skipped = 0
		duration = 0.0
		for suite in root.findall("testsuite"):
			tests += _to_int(suite.attrib.get("tests"), 0)
			failures += _to_int(suite.attrib.get("failures"), 0)
			errors += _to_int(suite.attrib.get("errors"), 0)
			skipped += _to_int(suite.attrib.get("skipped"), 0)
			duration += _to_float(suite.attrib.get("time"), 0.0)

	passed = max(tests - failures - errors - skipped, 0)
	return {
		"total": tests,
		"passed": passed,
		"failed": failures,
		"errors": errors,
		"skipped": skipped,
		"unknown": 0,
		"duration_seconds": duration,
		"source": "junit",
	}


def _build_tags(suite: str) -> Dict[str, str]:
	return {
		"suite": suite,
		"environment": os.getenv("ENVIRONMENT", "unknown"),
		"team": os.getenv("TEAM_NAME", "unknown"),
		"stage": os.getenv("STAGE_NAME", "unknown"),
		"build_id": os.getenv("BUILD_ID", "unknown"),
		"build_reason": os.getenv("BUILD_REASON", "unknown"),
		"branch": os.getenv("BUILD_SOURCEBRANCHNAME", "unknown"),
		"host": socket.gethostname(),
	}


def push_summary(summary: Dict[str, float], measurement: str, suite: str) -> int:
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

	total = int(summary.get("total", 0))
	passed = int(summary.get("passed", 0))
	failed = int(summary.get("failed", 0))
	errors = int(summary.get("errors", 0))
	skipped = int(summary.get("skipped", 0))
	unknown = int(summary.get("unknown", 0))
	duration_seconds = float(summary.get("duration_seconds", 0.0))
	pass_rate = (passed / total * 100.0) if total else 0.0

	point = Point(measurement)
	for key, value in _build_tags(suite).items():
		point = point.tag(key, value)

	point = (
		point
		.tag("source", str(summary.get("source", "unknown")))
		.field("total", total)
		.field("passed", passed)
		.field("failed", failed)
		.field("errors", errors)
		.field("skipped", skipped)
		.field("unknown", unknown)
		.field("duration_seconds", duration_seconds)
		.field("pass_rate", pass_rate)
		.time(datetime.now(timezone.utc))
	)

	try:
		with InfluxDBClient(url=url, token=token, org=org) as client:
			write_api = client.write_api(write_options=SYNCHRONOUS)
			write_api.write(bucket=bucket, org=org, record=point)
	except Exception as exc:
		print(f"[influx] Failed to push metrics: {exc}")
		return 1

	print(
		"[influx] Metrics pushed "
		f"(measurement={measurement}, suite={suite}, total={total}, passed={passed}, "
		f"failed={failed}, skipped={skipped}, pass_rate={pass_rate:.2f}%)."
	)
	return 0


def _find_default_junit_path() -> Path:
	preferred = os.getenv("JUNIT_XML_PATH")
	if preferred:
		return Path(preferred)

	candidates = [
		Path("reports/junit.xml"),
		Path("reports/junit/junit-report.xml"),
	]
	for candidate in candidates:
		if candidate.exists():
			return candidate

	return Path("reports/junit.xml")


def _default_suite_name() -> str:
	stage = os.getenv("STAGE_NAME")
	team = os.getenv("TEAM_NAME")
	if stage and team:
		return f"{team}:{stage}"
	if stage:
		return stage
	if team:
		return team
	return "applicationqe-ui"


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--allure-dir",
		default=os.getenv("ALLURE_RESULTS_DIR", "reports/allure"),
		help="Path to Allure results directory",
	)
	parser.add_argument(
		"--junit",
		default=str(_find_default_junit_path()),
		help="Path to pytest JUnit XML report",
	)
	parser.add_argument(
		"--measurement",
		default="ui_test_summary",
		help="Influx measurement name (default: ui_test_summary)",
	)
	parser.add_argument(
		"--run-name",
		default=_default_suite_name(),
		help="Logical test run/suite name tag",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Parse metrics and print summary without pushing to InfluxDB",
	)
	args = parser.parse_args()

	allure_summary = parse_allure_summary(Path(args.allure_dir))
	junit_summary = parse_junit_summary(Path(args.junit))

	# Prefer Allure summary when available because it captures final statuses from BDD flows.
	summary = allure_summary if allure_summary.get("total", 0) > 0 else junit_summary
	if summary.get("total", 0) <= 0:
		print(
			"[influx] No test result data found. "
			f"Checked Allure dir='{args.allure_dir}' and JUnit='{args.junit}'."
		)
		return 0

	print(
		"[influx] Summary prepared "
		f"(source={summary.get('source')}, total={summary.get('total')}, "
		f"passed={summary.get('passed')}, failed={summary.get('failed')}, "
		f"skipped={summary.get('skipped')})."
	)

	if args.dry_run:
		print("[influx] Dry-run enabled; skipping write.")
		return 0

	return push_summary(summary, args.measurement, args.run_name)


if __name__ == "__main__":
	sys.exit(main())
