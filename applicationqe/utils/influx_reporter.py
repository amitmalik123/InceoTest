#!/usr/bin/env python3
"""
InfluxDB Reporter — applicationqe

Reads Allure JSON result files produced by pytest-allure and pushes test
execution metrics to InfluxDB so they appear in the Grafana dashboard.

Data flow
---------
  Azure Pipeline
    → pytest + allure-pytest  →  allure-results/*.json
    → python utils/influx_reporter.py
    → InfluxDB (measurement: test_execution1)
    → Grafana

Configuration priority (highest → lowest)
------------------------------------------
  1. Environment variables   (set by the "Push Metrics to InfluxDB" pipeline step)
  2. config/<TEST_APP>/influxdb_config.json  (for local / module-specific runs)

Usage
-----
  # CI (env vars already set by pipeline):
  python utils/influx_reporter.py

  # Local (module-specific config):
  TEST_APP=model-management/smi python utils/influx_reporter.py

Safety contract
---------------
  * This file is ONLY executed when called as __main__.
  * It has NO import-time side effects on the test suite.
  * All failures are caught and printed; they never raise to the caller.
"""

import glob
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Optional dependencies — fail gracefully so pipeline step can continue
# ---------------------------------------------------------------------------
try:
    from influxdb_client import InfluxDBClient
    from influxdb_client.client.write_api import SYNCHRONOUS
    _INFLUX_AVAILABLE = True
except ImportError:
    _INFLUX_AVAILABLE = False
    print("⚠️  influxdb-client not installed — InfluxDB reporting disabled.")

# Decrypt ENC:-prefixed tokens stored in local config files.
# Works whether this script is run as a top-level script or as part of the
# applicationqe package (both import paths are tried).
try:
    from utils.crypto_utils import decrypt_value as _decrypt
except ImportError:
    try:
        from crypto_utils import decrypt_value as _decrypt  # type: ignore[no-redef]
    except ImportError:
        def _decrypt(value: str) -> str:  # type: ignore[misc]
            """No-op fallback: return plain-text values unchanged."""
            return value


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def _load_config() -> Dict[str, str]:
    """
    Return a unified config dict.

    Reads ``config/<TEST_APP>/influxdb_config.json`` when ``TEST_APP`` is set
    (useful for local runs).  All keys can be overridden by environment
    variables, which is how the Azure Pipeline supplies values.
    """
    app = os.getenv("TEST_APP", "")
    file_cfg: Dict[str, Any] = {}

    if app:
        config_path = Path(__file__).parent.parent / "config" / app / "influxdb_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as fh:
                    file_cfg = json.load(fh)
                print(f"📄 Loaded InfluxDB config: {config_path}")
            except Exception as exc:
                print(f"⚠️  Could not read InfluxDB config file: {exc}")

    raw_token = os.getenv("INFLUXDB_TOKEN") or file_cfg.get("influxdb_token", "")

    return {
        "url":          os.getenv("INFLUXDB_URL")    or file_cfg.get("influxdb_url",    "http://localhost:8086"),
        "token":        _decrypt(raw_token) if raw_token else "",
        "org":          os.getenv("INFLUXDB_ORG")    or file_cfg.get("influxdb_org",    "default"),
        "bucket":       os.getenv("INFLUXDB_BUCKET") or file_cfg.get("influxdb_bucket", "test-results"),
        "project_name": (
            os.getenv("PROJECT_NAME")
            or file_cfg.get("project_name", "")
            or os.getenv("BUILD_REPOSITORY_NAME", "unknown")
        ),
    }


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _derive_trigger_type(build_reason: str) -> str:
    """Normalise Azure DevOps build reasons into stable Grafana-friendly labels."""
    mapping = {
        "schedule":          "Scheduled",
        "manual":            "Manual",
        "individualci":      "CI",
        "batchedci":         "CI",
        "pullrequest":       "PR",
        "resourcetrigger":   "ResourceTrigger",
        "buildcompletion":   "BuildCompletion",
        "validateshelveset": "ValidateShelveset",
        "checkinshelveset":  "CheckinShelveset",
    }
    return mapping.get((build_reason or "").strip().lower(), build_reason or "Unknown")


def _derive_feature_tag() -> str:
    """
    Return a comma-separated string of top-level @tags from the feature files
    that match the active pytest marker (MARKER env var).

    Falls back to 'unknown' when no matching files are found.
    """
    marker = (
        os.getenv("MARKER")
        or os.getenv("PYTEST_MARKER")
        or os.getenv("TEST_MARKER")
        or ""
    ).strip()

    features_root = Path(__file__).parent.parent / "tests" / "features"
    if not features_root.exists():
        return "unknown"

    def _read_tags(feature_file: Path):
        top_level, all_tags = [], []
        before_feature = True
        try:
            with open(feature_file, "r", encoding="utf-8") as fh:
                for raw_line in fh:
                    stripped = raw_line.strip()
                    if not stripped:
                        continue
                    if stripped.lower().startswith("feature:"):
                        before_feature = False
                        continue
                    if stripped.startswith("@"):
                        tags = [t.lstrip("@").lower() for t in stripped.split() if t.startswith("@")]
                        all_tags.extend(tags)
                        if before_feature:
                            top_level.extend(tags)
        except Exception:
            pass
        return top_level, all_tags

    feature_files = sorted(features_root.rglob("*.feature"))
    normalized_marker = marker.lstrip("@").lower()
    selected: List[Path] = []

    if normalized_marker:
        for ff in feature_files:
            _, all_tags = _read_tags(ff)
            if normalized_marker in all_tags:
                selected.append(ff)

    if not selected:
        selected = feature_files

    collected: List[str] = []
    for ff in selected:
        top, all_tags = _read_tags(ff)
        tag = top[0] if top else (all_tags[0] if all_tags else "")
        if tag and tag not in collected:
            collected.append(tag)

    return ",".join(collected) if collected else "unknown"


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class AllureToInfluxDB:
    """Parse Allure JSON results and push execution metrics to InfluxDB."""

    def __init__(self) -> None:
        cfg = _load_config()
        self.influx_url    = cfg["url"]
        self.influx_token  = cfg["token"]
        self.influx_org    = cfg["org"]
        self.influx_bucket = cfg["bucket"]
        self.project_name  = cfg["project_name"]

        self.allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "./reports/allure-results")
        self.build_id           = os.getenv("BUILD_ID", os.getenv("BUILD_BUILDID", "local"))
        self.build_reason       = _derive_trigger_type(os.getenv("BUILD_REASON", "Manual"))
        self.environment        = os.getenv("ENVIRONMENT", os.getenv("TEST_ENV", "unknown"))
        self.feature_tag        = _derive_feature_tag()

        # Azure Pipelines — used to generate artifact deep-links
        self._collection_uri = os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", "")
        self._team_project   = os.getenv("SYSTEM_TEAMPROJECT", "")
        self._build_id_full  = os.getenv("BUILD_BUILDID", self.build_id)

    # ------------------------------------------------------------------
    # Artifact URLs
    # ------------------------------------------------------------------

    def get_artifact_urls(self) -> Dict[str, str]:
        """Build Azure Pipelines artifact deep-link URLs (empty dict if not in CI)."""
        if not (self._collection_uri and self._team_project):
            return {}
        base = (
            f"{self._collection_uri.rstrip('/')}/{self._team_project}"
            f"/_build/results?buildId={self._build_id_full}&artifactName="
        )
        return {name: base + name for name in ("AllureReport", "AllureResults", "TestResults")}

    # ------------------------------------------------------------------
    # Read Allure results
    # ------------------------------------------------------------------

    def read_allure_results(self) -> Dict[str, Any]:
        """Read and deduplicate Allure *-result.json files."""
        out: Dict[str, Any] = {"tests": []}

        if not os.path.exists(self.allure_results_dir):
            print(f"⚠️  Allure results directory not found: {self.allure_results_dir}")
            return out

        json_files = glob.glob(os.path.join(self.allure_results_dir, "*-result.json"))
        print(f"📂 Found {len(json_files)} result file(s) in {self.allure_results_dir}")

        # Keep only the latest result per test name (handles retries)
        latest: Dict[str, Any] = {}
        for path in json_files:
            try:
                with open(path, "r") as fh:
                    data = json.load(fh)
                name = data.get("name", "")
                if not name:
                    continue
                existing = latest.get(name)
                if existing is None or data.get("stop", 0) > existing.get("stop", 0):
                    latest[name] = data
            except Exception as exc:
                print(f"  ⚠️  Skipped {path}: {exc}")

        out["tests"] = list(latest.values())
        dropped = len(json_files) - len(out["tests"])
        if dropped:
            print(f"  ℹ️  Deduplicated to {len(out['tests'])} unique test(s) ({dropped} duplicate(s) dropped)")

        for test in out["tests"]:
            icon = "✓" if test.get("status") == "passed" else "✗"
            print(f"  {icon} [{test.get('status', 'unknown').upper()}] {test.get('name', 'unknown')}")

        return out

    # ------------------------------------------------------------------
    # Calculate metrics
    # ------------------------------------------------------------------

    def calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        tests = results.get("tests", [])
        m: Dict[str, Any] = {
            "total": len(tests), "passed": 0, "failed": 0,
            "skipped": 0, "broken": 0, "flaky": 0, "retried": 0,
            "total_duration": 0, "avg_duration": 0,
            "max_duration": 0, "min_duration": 0, "pass_rate": 0.0,
        }
        durations: List[int] = []

        for test in tests:
            status   = test.get("status", "unknown")
            is_flaky = test.get("statusDetails", {}).get("flaky", False)

            if status == "passed":
                m["passed"] += 1
                if is_flaky:
                    m["flaky"] += 1
            elif status == "failed":
                m["failed"] += 1
            elif status == "broken":
                m["broken"] += 1
            elif status == "skipped":
                m["skipped"] += 1

            if test.get("historyId"):
                m["retried"] += 1

            dur = test.get("stop", 0) - test.get("start", 0)
            m["total_duration"] += dur
            if dur > 0:
                durations.append(dur)

        if durations:
            m["avg_duration"] = int(m["total_duration"] / len(durations))
            m["max_duration"] = max(durations)
            m["min_duration"] = min(durations)

        testable = m["total"] - m["skipped"]
        if testable > 0:
            m["pass_rate"] = (m["passed"] / testable) * 100

        return m

    # ------------------------------------------------------------------
    # Build InfluxDB line-protocol points
    # ------------------------------------------------------------------

    def _make_tags(self) -> str:
        """Return the common tag set used on every measurement."""
        return (
            f'project="{self.project_name}",'
            f'environment="{self.environment}",'
            f'build_id="{self.build_id}",'
            f'build_reason="{self.build_reason}",'
            f'feature="{self.feature_tag}"'
        )

    def create_influx_points(
        self, metrics: Dict[str, Any], artifact_urls: Dict[str, str]
    ) -> List[str]:
        ts   = int(datetime.now().timestamp() * 1e9)  # nanoseconds
        tags = self._make_tags()

        points = [
            f"test_execution1,{tags} "
            f'total={metrics["total"]}i,'
            f'passed={metrics["passed"]}i,'
            f'failed={metrics["failed"]}i,'
            f'skipped={metrics["skipped"]}i,'
            f'broken={metrics["broken"]}i,'
            f'flaky={metrics["flaky"]}i,'
            f'retried={metrics["retried"]}i,'
            f'pass_rate={metrics["pass_rate"]:.2f},'
            f'total_duration={metrics["total_duration"]}i,'
            f'avg_duration={metrics["avg_duration"]}i,'
            f'max_duration={metrics["max_duration"]}i,'
            f'min_duration={metrics["min_duration"]}i '
            f"{ts}"
        ]

        if metrics["total"] > 0:
            flaky_rate = (metrics["flaky"] / metrics["total"]) * 100
            retry_rate = (metrics["retried"] / metrics["total"]) * 100
            points.append(
                f"test_quality,{tags} "
                f'flaky_count={metrics["flaky"]}i,'
                f"flaky_rate={flaky_rate:.2f},"
                f'retried_count={metrics["retried"]}i,'
                f"retry_rate={retry_rate:.2f} "
                f"{ts}"
            )

        if artifact_urls:
            fields = ",".join(f'{k}="{v}"' for k, v in artifact_urls.items())
            points.append(f"test_artifacts,{tags} {fields} {ts}")

        return points

    # ------------------------------------------------------------------
    # Push
    # ------------------------------------------------------------------

    def push_to_influxdb(self, points: List[str]) -> bool:
        """Write all line-protocol points to InfluxDB. Returns True on success."""
        if not _INFLUX_AVAILABLE:
            print("❌ influxdb-client package not available — cannot push metrics.")
            return False

        if not self.influx_token:
            print("⚠️  INFLUXDB_TOKEN not set — skipping InfluxDB push.")
            return False

        try:
            client    = InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_org)
            write_api = client.write_api(write_options=SYNCHRONOUS)

            print(f"📊 Pushing {len(points)} point(s) → {self.influx_url} / bucket={self.influx_bucket}")
            for point in points:
                write_api.write(bucket=self.influx_bucket, record=point)
                print(f"  ✓ {point[:120]}...")

            client.close()
            print("✓ Metrics successfully pushed to InfluxDB")
            return True

        except Exception as exc:
            print(f"❌ InfluxDB push failed: {exc}")
            return False

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run(self) -> None:
        """End-to-end execution: read → calculate → push."""
        sep = "=" * 70
        print(sep)
        print("🚀 Allure → InfluxDB Reporter  (applicationqe)")
        print(sep)
        print(f"  Project      : {self.project_name}")
        print(f"  Environment  : {self.environment}")
        print(f"  Build ID     : {self.build_id}")
        print(f"  Trigger      : {self.build_reason}")
        print(f"  Feature tag  : {self.feature_tag}")
        print(f"  InfluxDB URL : {self.influx_url}")
        print(f"  Bucket       : {self.influx_bucket}")
        print(f"  Allure dir   : {self.allure_results_dir}")
        print()

        results = self.read_allure_results()
        if not results["tests"]:
            print("⚠️  No test results found — nothing to push.")
            print(sep)
            return

        metrics = self.calculate_metrics(results)
        print("\n📈 Metrics summary:")
        print(f"  Total    : {metrics['total']}")
        print(f"  Passed   : {metrics['passed']}")
        print(f"  Failed   : {metrics['failed']}")
        print(f"  Broken   : {metrics['broken']}")
        print(f"  Skipped  : {metrics['skipped']}")
        print(f"  Flaky    : {metrics['flaky']}")
        print(f"  Pass rate: {metrics['pass_rate']:.2f}%")
        print(f"  Duration : {metrics['total_duration']}ms total / {metrics['avg_duration']}ms avg")
        print()

        artifact_urls = self.get_artifact_urls()
        points = self.create_influx_points(metrics, artifact_urls)
        self.push_to_influxdb(points)
        print(sep)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        AllureToInfluxDB().run()
    except Exception as exc:
        # Top-level safety net — pipeline step has continueOnError:true
        # but we still print the traceback for diagnostics.
        import traceback
        print(f"\n❌ Unhandled error in influx_reporter: {exc}")
        traceback.print_exc()
