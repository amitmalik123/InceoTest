#!/usr/bin/env python3
"""
Azure Log Analytics Reporter: Parses Allure JSON results and pushes metrics to Azure Log Analytics
"""

import base64
import glob
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


def load_azure_analytics_config():
    """Load Azure Log Analytics configuration from config file or environment variables"""
    app = os.getenv("TEST_APP", "")
    config_path = Path(__file__).parent.parent / "config" / app / "azure_analytics_config.json"

    # Try to load from config file first
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Error loading Azure Analytics config file: {e}")

    # Build final config: config file values → environment variable overrides → defaults
    default_project = os.getenv(
        "BUILD_REPOSITORY_NAME", os.getenv("SYSTEM_TEAMPROJECT", "unknown")
    )
    return {
        "workspace_id": os.getenv("AZURE_LOG_WORKSPACE_ID", config.get("workspace_id", "")),
        "shared_key": os.getenv("AZURE_LOG_SHARED_KEY", ""),
        "log_type": os.getenv("AZURE_LOG_TYPE", config.get("log_type", "TestExecution")),
        "project_name": config.get("project_name", "") or os.getenv("PROJECT_NAME", default_project),
        "auto_push": os.getenv("AZURE_ANALYTICS_AUTO_PUSH", str(config.get("auto_push", False))).lower()
        in ("true", "1"),
    }


class AllureToAzureAnalytics:
    """Convert Allure test results to Azure Log Analytics custom logs"""

    @staticmethod
    def _derive_trigger_type(build_reason: str) -> str:
        """Normalize Azure DevOps build reasons into stable trigger categories."""
        reason = (build_reason or "").strip().lower()

        reason_to_trigger = {
            "schedule": "Scheduled",
            "manual": "Manual",
            "individualci": "CI",
            "batchedci": "CI",
            "pullrequest": "PR",
            "resourcetrigger": "ResourceTrigger",
            "buildcompletion": "BuildCompletion",
            "validateshelveset": "ValidateShelveset",
            "checkinshelveset": "CheckinShelveset",
        }

        return reason_to_trigger.get(reason, build_reason or "Unknown")

    @staticmethod
    def _derive_feature_tag() -> str:
        """Extract one or more feature tags from matching .feature files."""
        features_root = Path(__file__).parent.parent / "tests" / "features"
        if not features_root.exists():
            return "unknown"

        # Marker can be passed from pipeline/env. Use it to identify the relevant feature file.
        marker = (
            os.getenv("MARKER")
            or os.getenv("PYTEST_MARKER")
            or os.getenv("TEST_MARKER")
            or ""
        ).strip()

        def read_file_tags(feature_file: Path) -> tuple[list[str], list[str]]:
            """Return (top_level_tags, all_tags_before_first_feature_block)."""
            top_level_tags: list[str] = []
            all_tags: list[str] = []
            before_feature = True

            with open(feature_file, "r", encoding="utf-8") as f:
                for raw_line in f:
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
                            top_level_tags.extend(tags)

            return top_level_tags, all_tags

        feature_files = sorted(features_root.rglob("*.feature"))
        if not feature_files:
            return "unknown"

        selected_files: list[Path] = []
        normalized_marker = marker.lstrip("@").lower()

        if normalized_marker:
            for feature_file in feature_files:
                try:
                    _, all_tags = read_file_tags(feature_file)
                    if normalized_marker in all_tags:
                        selected_files.append(feature_file)
                except Exception as e:
                    print(f"Warning: Could not read feature file {feature_file}: {e}")

        # If marker doesn't map to any file tags, include all feature files for broader suites.
        if not selected_files:
            selected_files = feature_files

        feature_tags: list[str] = []
        for selected_file in selected_files:
            try:
                top_level_tags, all_tags = read_file_tags(selected_file)
                chosen_tag = top_level_tags[0] if top_level_tags else (all_tags[0] if all_tags else "")
                if chosen_tag and chosen_tag not in feature_tags:
                    feature_tags.append(chosen_tag)
            except Exception as e:
                print(f"Warning: Could not read feature file {selected_file}: {e}")

        if feature_tags:
            return ",".join(feature_tags)

        return "unknown"

    def __init__(self):
        analytics_config = load_azure_analytics_config()
        self.workspace_id = analytics_config["workspace_id"]
        self.shared_key = analytics_config["shared_key"]
        self.log_type = analytics_config["log_type"]
        self.project_name = analytics_config.get("project_name", "unknown")
        self.auto_push = analytics_config.get("auto_push", False)
        self.allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "./target/allure-results")
        self.build_id = os.getenv("BUILD_ID", "local")
        self.build_reason = os.getenv("BUILD_REASON", "Manual")
        self.trigger_type = self._derive_trigger_type(self.build_reason)
        self.feature = self._derive_feature_tag()
        self.project_name = f"{self.project_name}_{self.trigger_type}"
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
            print(f"Warning: Allure results directory not found: {self.allure_results_dir}")
            return results

        # Read test results - track by test name to use only the latest result
        json_files = glob.glob(os.path.join(self.allure_results_dir, "*-result.json"))
        print(f"Found {len(json_files)} total test result files")

        # Dictionary to store latest result for each test (by test name)
        latest_results = {}

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
                    test_name = test_data.get("name", "")

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
            f"Deduplicated to {len(results['tests'])} unique test(s) by name (skipped {duplicate_count} duplicates/retries)"
        )

        # Print unique tests
        for test_data in results["tests"]:
            test_name = test_data.get("name", "unknown")
            status = test_data.get("status", "unknown")
            print(f"  - {status.upper()}: {test_name}")

        # Read containers
        for json_file in glob.glob(os.path.join(self.allure_results_dir, "*-container.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    results["containers"].append(json.load(f))
            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        # Read groups
        for json_file in glob.glob(os.path.join(self.allure_results_dir, "groups.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
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
            "pass_rate": 0.0,
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
                    test_details.append(f"  [OK] {test_name} [PASSED - FLAKY]")
                else:
                    test_details.append(f"  [OK] {test_name} [PASSED]")
            elif status in ("failed", "broken"):
                metrics["failed"] += 1
                test_details.append(f"  [X] {test_name} [{status.upper()}]")
            elif status == "skipped":
                metrics["skipped"] += 1
                test_details.append(f"  [-] {test_name} [SKIPPED]")
            else:
                # Unknown status
                test_details.append(f"  [?] {test_name} [{status.upper()}]")

            # Check for retried tests (tests that were retried)
            history = test.get("historyId", "")
            if history:
                metrics["retried"] += 1

            # Track duration (ms from Allure, convert to seconds)
            duration = test.get("stop", 0) - test.get("start", 0)
            metrics["total_duration"] += duration

        # Convert total duration from ms to seconds (integer)
        metrics["total_duration"] = int(metrics["total_duration"] / 1000)

        # Calculate pass rate (excluding skipped tests from calculation)
        testable_total = metrics["total"] - metrics["skipped"]
        if testable_total > 0:
            metrics["pass_rate"] = round((metrics["passed"] / testable_total) * 100, 2)

        # Debug: Show status distribution
        print(f"\nRaw Status Distribution: {status_counts}")
        print("\nTest Details:")
        for detail in test_details:
            print(detail)

        return metrics

    @staticmethod
    def _extract_feature_from_test(test: Dict[str, Any]) -> str:
        """Extract feature name from Allure test metadata."""
        description = test.get("description", "")

        # Example: ...\tests\features\naw\NAW.feature: Scenario Name
        match = re.search(
            r"[/\\]tests[/\\]features(?:[/\\][^/\\:]+)*[/\\]([^/\\:]+)\.feature",
            description,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).lower()

        return "unknown"

    def calculate_metrics_by_feature(self, results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate test metrics grouped by feature file."""
        tests = results.get("tests", [])
        metrics_by_feature: Dict[str, Dict[str, Any]] = {}

        for test in tests:
            feature_name = self._extract_feature_from_test(test)

            if feature_name not in metrics_by_feature:
                metrics_by_feature[feature_name] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "flaky": 0,
                    "retried": 0,
                    "total_duration": 0,
                    "pass_rate": 0.0,
                }

            feature_metrics = metrics_by_feature[feature_name]
            feature_metrics["total"] += 1

            status = test.get("status", "unknown")
            status_details = test.get("statusDetails", {})

            if status == "passed":
                feature_metrics["passed"] += 1
                if status_details.get("flaky", False):
                    feature_metrics["flaky"] += 1
            elif status in ("failed", "broken"):
                feature_metrics["failed"] += 1
            elif status == "skipped":
                feature_metrics["skipped"] += 1

            if test.get("historyId", ""):
                feature_metrics["retried"] += 1

            duration = test.get("stop", 0) - test.get("start", 0)
            feature_metrics["total_duration"] += duration

        for feature_metrics in metrics_by_feature.values():
            feature_metrics["total_duration"] = int(feature_metrics["total_duration"] / 1000)
            testable_total = feature_metrics["total"] - feature_metrics["skipped"]
            if testable_total > 0:
                feature_metrics["pass_rate"] = round(
                    (feature_metrics["passed"] / testable_total) * 100, 2
                )

        return metrics_by_feature

    def create_log_entries(
        self,
        metrics: Dict[str, Any],
        metrics_by_feature: Dict[str, Dict[str, Any]],
        artifact_urls: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Create Azure Log Analytics log entries from metrics"""
        timestamp = datetime.now(timezone.utc).isoformat()

        entries: List[Dict[str, Any]] = []

        grouped_metrics = metrics_by_feature or {self.feature: metrics}

        for feature_name, feature_metrics in grouped_metrics.items():
            tags = {
                "build_id": self.build_id,
                "environment": self.environment,
                "build_reason": self.build_reason,
                "trigger_type": self.trigger_type,
                "feature": feature_name,
                "project_name": self.project_name,
            }

            execution_entry = {
                "TimeGenerated": timestamp,
                "log_type": "test_execution",
                **tags,
                "total": feature_metrics["total"],
                "passed": feature_metrics["passed"],
                "failed": feature_metrics["failed"],
                "skipped": feature_metrics["skipped"],
                "flaky": feature_metrics["flaky"],
                "retried": feature_metrics["retried"],
                "pass_rate": feature_metrics["pass_rate"],
                "total_duration": feature_metrics["total_duration"],
            }
            entries.append(execution_entry)

            if feature_metrics["total"] > 0:
                flaky_rate = round((feature_metrics["flaky"] / feature_metrics["total"]) * 100, 2)
                retry_rate = round((feature_metrics["retried"] / feature_metrics["total"]) * 100, 2)

                quality_entry = {
                    "TimeGenerated": timestamp,
                    "log_type": "test_quality",
                    **tags,
                    "flaky_count": feature_metrics["flaky"],
                    "flaky_rate": flaky_rate,
                    "retried_count": feature_metrics["retried"],
                    "retry_rate": retry_rate,
                }
                entries.append(quality_entry)

        # Artifact URLs entry
        if artifact_urls:
            artifact_entry = {
                "TimeGenerated": timestamp,
                "log_type": "test_artifacts",
                "build_id": self.build_id,
                "environment": self.environment,
                "build_reason": self.build_reason,
                "trigger_type": self.trigger_type,
                "feature": self.feature,
                "project_name": self.project_name,
            }
            for name, url in artifact_urls.items():
                artifact_entry[name] = url
            entries.append(artifact_entry)

        return entries

    def _build_signature(self, date: str, content_length: int) -> str:
        """Build the authorization signature for Azure Log Analytics API"""
        string_to_hash = f"POST\n{content_length}\napplication/json\nx-ms-date:{date}\n/api/logs"
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, hashlib.sha256).digest()
        ).decode()
        return f"SharedKey {self.workspace_id}:{encoded_hash}"

    def push_to_azure_analytics(self, entries: List[Dict[str, Any]]) -> bool:
        """Push log entries to Azure Log Analytics"""
        if not self.workspace_id or not self.shared_key:
            print("Warning: Azure Log Analytics workspace_id or shared_key not set. Skipping push.")
            return False

        try:
            body = json.dumps(entries)
            content_length = len(body)
            date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

            signature = self._build_signature(date, content_length)

            headers = {
                "Content-Type": "application/json",
                "Log-Type": self.log_type,
                "x-ms-date": date,
                "Authorization": signature,
                "time-generated-field": "TimeGenerated",
            }

            url = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

            print(f"Pushing {len(entries)} log entry(ies) to Azure Log Analytics...")
            response = requests.post(url, data=body, headers=headers, timeout=30)

            if response.status_code in (200, 202):
                print(f"Successfully pushed to Azure Log Analytics (HTTP {response.status_code})")
                return True
            else:
                print(
                    f"Error pushing to Azure Log Analytics: HTTP {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error pushing to Azure Log Analytics: {e}")
            return False

    def run(self):
        """Main execution"""
        print("=" * 70)
        print("Allure to Azure Log Analytics Reporter")
        print("=" * 70)
        print(f"Workspace ID: {self.workspace_id}")
        print(f"Log Type: {self.log_type}")
        print(f"Trigger Type: {self.trigger_type}")
        print(f"Feature: {self.feature}")
        print(f"Allure Results Dir: {self.allure_results_dir}")
        print(f"Environment: {self.environment}")
        print(f"Build ID: {self.build_id}")
        print()

        # Read Allure results
        results = self.read_allure_results()
        if not results["tests"]:
            print("Warning: No test results found. Skipping Azure Analytics push.")
            return

        print(f"Found {len(results['tests'])} test result(s)")

        # Calculate metrics
        metrics = self.calculate_metrics(results)
        metrics_by_feature = self.calculate_metrics_by_feature(results)
        print("\nTest Execution Metrics:")
        print(f"  Total Tests: {metrics['total']}")
        print(f"  Passed: {metrics['passed']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Skipped: {metrics['skipped']}")
        print(f"  Flaky Tests: {metrics['flaky']}")
        print(f"  Pass Rate: {metrics['pass_rate']:.2f}%")
        print(f"  Total Duration: {metrics['total_duration']}s")

        if metrics_by_feature:
            print("\nFeature-wise Metrics:")
            for feature_name, feature_metrics in metrics_by_feature.items():
                print(
                    f"  {feature_name}: total={feature_metrics['total']}, "
                    f"passed={feature_metrics['passed']}, failed={feature_metrics['failed']}, "
                    f"skipped={feature_metrics['skipped']}"
                )

        print("\nTest Quality Metrics:")
        if metrics["total"] > 0:
            flaky_rate = (metrics["flaky"] / metrics["total"]) * 100
            print(f"  Flaky Rate: {flaky_rate:.2f}%")
            retry_rate = (metrics["retried"] / metrics["total"]) * 100
            print(f"  Retried Tests: {metrics['retried']}")
            print(f"  Retry Rate: {retry_rate:.2f}%")

        # Get artifact URLs
        artifact_urls = self.get_artifact_urls()
        if artifact_urls:
            print("\nPipeline Artifacts:")
            for name, url in artifact_urls.items():
                print(f"  {name}: {url[:80]}...")
        print()

        # Create and push entries
        entries = self.create_log_entries(metrics, metrics_by_feature, artifact_urls)
        self.push_to_azure_analytics(entries)
        print("=" * 70)


if __name__ == "__main__":
    reporter = AllureToAzureAnalytics()
    reporter.run()
