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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

from utils.crypto_utils import decrypt_value


def load_azure_analytics_config():
    """Load Azure Log Analytics configuration from config file or environment variables"""
    # CONFIG_MODULE determines the project subfolder under config/ (e.g., "oam", "naw", "crm")
    # Tries CONFIG_MODULE env var first, then falls back to checking available configs
    config_module = os.getenv("CONFIG_MODULE")
    
    # If CONFIG_MODULE not set, try multiple known modules in priority order
    if not config_module:
        config_dir = Path(__file__).parent.parent / "config"
        # Try these modules in order of preference for applicationqe
        for module in ["oam", "naw", "crm"]:
            potential_path = config_dir / module / "azure_analytics_config.json"
            if potential_path.exists():
                config_module = module
                break
    
    config_path = Path(__file__).parent.parent / "config" / config_module / "azure_analytics_config.json"

    # Try to load from config file first
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Error loading Azure Analytics config file: {e}")

    # Decrypt shared_key separately so a decryption failure doesn't lose other config values
    shared_key = ""
    if config.get("shared_key"):
        try:
            shared_key = decrypt_value(config["shared_key"])
        except Exception:
            print("Warning: Could not decrypt shared_key from config, falling back to env var")

    # Build final config: config file values → environment variable overrides → defaults
    default_project = os.getenv(
        "BUILD_REPOSITORY_NAME", os.getenv("SYSTEM_TEAMPROJECT", "unknown")
    )
    return {
        "workspace_id": os.getenv("AZURE_LOG_WORKSPACE_ID", config.get("workspace_id", "")),
        "shared_key": os.getenv("AZURE_LOG_SHARED_KEY", "") or shared_key,
        "log_type": os.getenv("AZURE_LOG_TYPE", config.get("log_type", "TestExecution")),
        "project_name": os.getenv("PROJECT_NAME", config.get("project_name", "")) or default_project,
        "auto_push": os.getenv("AZURE_ANALYTICS_AUTO_PUSH", str(config.get("auto_push", False))).lower()
        in ("true", "1"),
    }


class AllureToAzureAnalytics:
    """Convert Allure test results to Azure Log Analytics custom logs"""

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

    def create_log_entries(
        self, metrics: Dict[str, Any], artifact_urls: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Create Azure Log Analytics log entries from metrics"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Common tags/dimensions
        tags = {
            "build_id": self.build_id,
            "environment": self.environment,
            "build_reason": self.build_reason,
            "project_name": self.project_name,
        }

        # Main test execution entry
        execution_entry = {
            "TimeGenerated": timestamp,
            "log_type": "test_execution",
            **tags,
            "total": metrics["total"],
            "passed": metrics["passed"],
            "failed": metrics["failed"],
            "skipped": metrics["skipped"],
            "flaky": metrics["flaky"],
            "retried": metrics["retried"],
            "pass_rate": metrics["pass_rate"],
            "total_duration": metrics["total_duration"],
        }

        entries = [execution_entry]

        # Test quality entry
        if metrics["total"] > 0:
            flaky_rate = round((metrics["flaky"] / metrics["total"]) * 100, 2)
            retry_rate = round((metrics["retried"] / metrics["total"]) * 100, 2)

            quality_entry = {
                "TimeGenerated": timestamp,
                "log_type": "test_quality",
                **tags,
                "flaky_count": metrics["flaky"],
                "flaky_rate": flaky_rate,
                "retried_count": metrics["retried"],
                "retry_rate": retry_rate,
            }
            entries.append(quality_entry)

        # Artifact URLs entry
        if artifact_urls:
            artifact_entry = {
                "TimeGenerated": timestamp,
                "log_type": "test_artifacts",
                **tags,
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
        print("\nTest Execution Metrics:")
        print(f"  Total Tests: {metrics['total']}")
        print(f"  Passed: {metrics['passed']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Skipped: {metrics['skipped']}")
        print(f"  Flaky Tests: {metrics['flaky']}")
        print(f"  Pass Rate: {metrics['pass_rate']:.2f}%")
        print(f"  Total Duration: {metrics['total_duration']}s")

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
        entries = self.create_log_entries(metrics, artifact_urls)
        self.push_to_azure_analytics(entries)
        print("=" * 70)


if __name__ == "__main__":
    reporter = AllureToAzureAnalytics()
    reporter.run()
