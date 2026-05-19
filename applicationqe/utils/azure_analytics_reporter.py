"""
Azure Log Analytics Reporter

Pushes test execution metrics to Azure Log Analytics workspace
for Grafana dashboard visualization.

Usage:
    Set the following environment variables:
        AZURE_LOG_WORKSPACE_ID  - Log Analytics Workspace ID
        AZURE_LOG_SHARED_KEY    - Log Analytics Shared Key (Primary or Secondary)
        ALLURE_RESULTS_DIR      - Path to allure-results directory
        ENVIRONMENT             - Test environment (qa, test11, etc.)
        BUILD_ID                - Azure DevOps Build ID
        BUILD_REASON            - Build trigger reason (Manual, Schedule, etc.)

    Then run:
        python utils/azure_analytics_reporter.py
"""

import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Log Analytics configuration
WORKSPACE_ID = os.getenv("AZURE_LOG_WORKSPACE_ID", "")
SHARED_KEY = os.getenv("AZURE_LOG_SHARED_KEY", "")

# Load config from azure_analytics_config.json
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "billing" / "platformrevenuedashboard" / "strategistgroupmodel" / "azure_analytics_config.json"
_config = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as _f:
        _config = json.load(_f)

LOG_TYPE = _config.get("log_type", "Application_testExecution")
PROJECT_NAME = _config.get("project_name", "Billing_Platform_revenue_Dashboard")
AUTO_PUSH = _config.get("auto_push", True)


def build_signature(workspace_id: str, shared_key: str, date: str, content_length: int, method: str, content_type: str, resource: str) -> str:
    """Build the authorization signature for Azure Log Analytics API."""
    x_headers = f"x-ms-date:{date}"
    string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = string_to_hash.encode("utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    return f"SharedKey {workspace_id}:{encoded_hash}"


def post_data(workspace_id: str, shared_key: str, body: str, log_type: str) -> int:
    """Post data to Azure Log Analytics Data Collector API."""
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)

    signature = build_signature(
        workspace_id, shared_key, rfc1123date, content_length, method, content_type, resource
    )

    uri = f"https://{workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"

    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }

    response = requests.post(uri, data=body, headers=headers, timeout=30)
    if response.status_code >= 200 and response.status_code <= 299:
        logger.info(f"✓ Data posted to Azure Log Analytics (HTTP {response.status_code})")
    else:
        logger.error(f"✗ Failed to post data (HTTP {response.status_code}): {response.text}")
    return response.status_code


def parse_allure_results(results_dir: str) -> dict:
    """Parse Allure results directory and extract test metrics."""
    results_path = Path(results_dir)

    if not results_path.exists():
        logger.warning(f"Allure results directory not found: {results_dir}")
        return {}

    total = 0
    passed = 0
    failed = 0
    broken = 0
    skipped = 0
    total_duration_ms = 0

    # Parse individual test result JSON files
    for result_file in results_path.glob("*-result.json"):
        try:
            with open(result_file) as f:
                result = json.load(f)

            total += 1
            status = result.get("status", "unknown")

            if status == "passed":
                passed += 1
            elif status == "failed":
                failed += 1
            elif status == "broken":
                broken += 1
            elif status == "skipped":
                skipped += 1

            # Calculate duration
            start = result.get("start", 0)
            stop = result.get("stop", 0)
            if start and stop:
                total_duration_ms += (stop - start)

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Skipping malformed result file {result_file}: {e}")
            continue

    pass_rate = (passed / total * 100) if total > 0 else 0
    total_duration_sec = total_duration_ms / 1000

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "broken": broken,
        "skipped": skipped,
        "pass_rate": round(pass_rate, 2),
        "total_duration_seconds": round(total_duration_sec, 2),
    }


def main():
    """Main entry point for Azure Log Analytics reporting."""
    # Check auto_push setting from config
    if not AUTO_PUSH:
        logger.info("auto_push is disabled in azure_analytics_config.json. Skipping.")
        sys.exit(0)

    # Validate configuration
    if not WORKSPACE_ID or not SHARED_KEY:
        logger.warning("Azure Log Analytics credentials not configured. Skipping metric push.")
        logger.info("Set AZURE_LOG_WORKSPACE_ID and AZURE_LOG_SHARED_KEY environment variables.")
        sys.exit(0)

    allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "reports/billing/platformrevenuedashboard/strategistgroupmodel/allure-results")
    environment = os.getenv("ENVIRONMENT", "unknown")
    build_id = os.getenv("BUILD_ID", "local")
    build_reason = os.getenv("BUILD_REASON", "Manual")

    logger.info(f"Parsing Allure results from: {allure_results_dir}")
    metrics = parse_allure_results(allure_results_dir)

    if not metrics:
        logger.warning("No test metrics found. Skipping Azure Log Analytics push.")
        sys.exit(0)

    # Build the log entry
    # Field names map to Azure Log Analytics _CL table columns.
    # String fields get _s suffix, numeric get _d, datetime get _t.
    # Grafana dashboard filters on project_name_s, so the field must be "project_name".
    log_entry = [
        {
            "team": "Billing",
            "project_name": PROJECT_NAME,
            "feature": "Strategist Group Model",
            "environment": environment,
            "build_id": build_id,
            "build_reason": build_reason,
            "total_tests": metrics["total_tests"],
            "passed": metrics["passed"],
            "failed": metrics["failed"],
            "broken": metrics["broken"],
            "skipped": metrics["skipped"],
            "pass_rate": metrics["pass_rate"],
            "total_duration_seconds": metrics["total_duration_seconds"],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
    ]

    body = json.dumps(log_entry)
    logger.info(f"Pushing metrics to Azure Log Analytics...")
    logger.info(f"  Project: {PROJECT_NAME}")
    logger.info(f"  Log Type: {LOG_TYPE}")
    logger.info(f"  Environment: {environment}")
    logger.info(f"  Total: {metrics['total_tests']} | Passed: {metrics['passed']} | Failed: {metrics['failed']} | Skipped: {metrics['skipped']}")
    logger.info(f"  Pass Rate: {metrics['pass_rate']}%")
    logger.info(f"  Duration: {metrics['total_duration_seconds']}s")

    status_code = post_data(WORKSPACE_ID, SHARED_KEY, body, LOG_TYPE)

    if 200 <= status_code <= 299:
        logger.info("✓ Successfully pushed metrics to Azure Log Analytics")
        logger.info(f"  Log Type: {LOG_TYPE}_CL")
        logger.info(f"  Workspace ID: {WORKSPACE_ID[:8]}...")
        logger.info(f"  Query in Grafana: {LOG_TYPE}_CL | order by TimeGenerated desc")
    else:
        logger.error(f"✗ Failed to push metrics (HTTP {status_code})")
        sys.exit(1)


if __name__ == "__main__":
    main()
