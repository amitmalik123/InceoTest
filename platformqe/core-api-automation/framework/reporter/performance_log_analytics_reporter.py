"""
Performance Log Analytics Reporter

Parses Locust performance artifacts and pushes run, endpoint, time-series,
failure, and baseline records to Azure Log Analytics custom tables.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from framework.common.logger import get_logger
from framework.loaders.path_loader import get_project_path

logger = get_logger(__name__)

LOG_TYPE_RUN = "PerfRun"
LOG_TYPE_ENDPOINT = "PerfEndpointSummary"
LOG_TYPE_TIMESERIES = "PerfTimeSeries"
LOG_TYPE_FAILURE = "PerfFailure"
LOG_TYPE_BASELINE = "PerfBaseline"

STATUS_NO_BASELINE = "NO_BASELINE"


class PerformanceLogAnalyticsClient:
    """Minimal Azure Log Analytics HTTP Data Collector client."""

    def __init__(self, workspace_id: str, shared_key: str) -> None:
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.api_version = "2016-04-01"

    def _build_signature(
        self,
        date: str,
        content_length: int,
        method: str,
        content_type: str,
        resource: str,
    ) -> str:
        x_headers = f"x-ms-date:{date}"
        string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, string_to_hash.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")
        return f"SharedKey {self.workspace_id}:{encoded_hash}"

    def post_records(self, log_type: str, records: List[Dict[str, Any]], batch_size: int = 500) -> bool:
        if not records:
            logger.info("[Performance Log Analytics] No %s records to push", log_type)
            return True

        success = True
        for batch in _chunks(records, batch_size):
            body = json.dumps(batch, separators=(",", ":"), default=str)
            method = "POST"
            content_type = "application/json"
            resource = "/api/logs"
            rfc1123date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            content_length = len(body)
            signature = self._build_signature(rfc1123date, content_length, method, content_type, resource)
            uri = f"https://{self.workspace_id}.ods.opinsights.azure.com{resource}?api-version={self.api_version}"
            headers = {
                "content-type": content_type,
                "Authorization": signature,
                "Log-Type": log_type,
                "x-ms-date": rfc1123date,
            }
            try:
                response = requests.post(uri, data=body, headers=headers, timeout=30)
                if 200 <= response.status_code <= 299:
                    logger.info(
                        "[Performance Log Analytics] Accepted %d %s records into %s_CL",
                        len(batch),
                        log_type,
                        log_type,
                    )
                else:
                    logger.error(
                        "[Performance Log Analytics] Failed posting %s records: %s - %s",
                        log_type,
                        response.status_code,
                        response.text,
                    )
                    success = False
            except requests.exceptions.RequestException as exc:
                logger.error("[Performance Log Analytics] Request failed for %s: %s", log_type, exc)
                success = False
        return success


class LocustPerformanceArtifacts:
    """Loads Locust CSV and metadata artifacts from a report directory."""

    def __init__(self, report_dir: Path, csv_base: Optional[Path] = None) -> None:
        self.report_dir = report_dir
        self.csv_base = csv_base or report_dir / "performance_report"
        self.stats_path = self.csv_base.with_name(self.csv_base.name + "_stats.csv")
        self.history_path = self.csv_base.with_name(self.csv_base.name + "_stats_history.csv")
        self.failures_path = self.csv_base.with_name(self.csv_base.name + "_failures.csv")
        self.exceptions_path = self.csv_base.with_name(self.csv_base.name + "_exceptions.csv")
        self.metadata_path = self.csv_base.with_name(self.csv_base.name + "_metadata.txt")
        self.html_path = self.csv_base.with_suffix(".html")
        self.executive_summary_path = self.csv_base.with_name(self.csv_base.name + "_executive_summary.html")

    def load(self) -> Dict[str, Any]:
        return {
            "stats": _read_csv(self.stats_path),
            "history": _read_csv(self.history_path),
            "failures": _read_csv(self.failures_path),
            "exceptions": _read_csv(self.exceptions_path),
            "metadata": _parse_metadata(self.metadata_path),
        }


def find_report_dir(reports_path: Optional[str] = None) -> Path:
    if reports_path:
        path = Path(reports_path)
        if not path.is_absolute():
            path = get_project_path(reports_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"Reports path not found: {path}")

    reports_dir = get_project_path("reports")
    folders = [
        path for path in reports_dir.iterdir()
        if path.is_dir() and path.name != "archive" and not path.name.startswith(".")
    ]
    if not folders:
        raise FileNotFoundError(f"No timestamped report folders found under {reports_dir}")
    return max(folders, key=lambda path: path.stat().st_mtime)


def build_records(
    artifacts: LocustPerformanceArtifacts,
    service_name: Optional[str] = None,
    environment_name: Optional[str] = None,
    load_profile: Optional[str] = None,
    load_multiplier: Optional[float] = None,
    include_timeseries: bool = True,
) -> Dict[str, List[Dict[str, Any]]]:
    loaded = artifacts.load()
    stats_rows = loaded["stats"]
    history_rows = loaded["history"]
    metadata = loaded["metadata"]

    test_params = metadata.get("Test Parameters", {})
    command_args = metadata.get("Command Line Arguments", {})
    system_metrics = metadata.get("System Monitoring", {})

    service = service_name or _optional_env("SERVICE_NAME") or _infer_service_from_file(test_params.get("file")) or "unknown"
    env_name = environment_name or _optional_env("ENV_NAME") or test_params.get("env") or "unknown"
    load = load_profile or _optional_env("PERF_LOAD_PROFILE") or _infer_load_profile(command_args, test_params)
    multiplier = _safe_float(load_multiplier if load_multiplier is not None else _optional_env("PERF_LOAD_MULTIPLIER"), None)
    if multiplier is None:
        multiplier = _load_multiplier_from_profile(load)

    generated_at = _utc_now()
    timestamp_label = _compact_timestamp(generated_at)
    build_id = _optional_env("BUILD_BUILDID") or "local"
    run_id = _clean_id(f"{service}_{env_name}_{load}_{build_id}_{timestamp_label}")

    common = _build_common_fields(
        run_id=run_id,
        service_name=service,
        environment_name=env_name,
        load_profile=load,
        load_multiplier=multiplier,
        test_params=test_params,
        command_args=command_args,
        generated_at=generated_at,
    )

    aggregate_row = _find_aggregate_row(stats_rows)
    run_records = [_build_run_record(common, aggregate_row, system_metrics, artifacts)]
    endpoint_records = [
        _build_endpoint_record(common, row)
        for row in stats_rows
        if not _is_blank_csv_row(row) and not _is_aggregate_row(row)
    ]
    timeseries_records = (
        [_build_timeseries_record(common, row) for row in history_rows if not _is_blank_csv_row(row)]
        if include_timeseries
        else []
    )
    failure_records = _build_failure_records(common, loaded["failures"], loaded["exceptions"])

    return {
        LOG_TYPE_RUN: run_records,
        LOG_TYPE_ENDPOINT: endpoint_records,
        LOG_TYPE_TIMESERIES: timeseries_records,
        LOG_TYPE_FAILURE: failure_records,
        LOG_TYPE_BASELINE: [],
    }


def build_baseline_records(
    records: Dict[str, List[Dict[str, Any]]],
    approved_by: Optional[str] = None,
    reason: Optional[str] = None,
) -> List[Dict[str, Any]]:
    approved_on = _utc_now()
    baseline_records: List[Dict[str, Any]] = []
    endpoints = records.get(LOG_TYPE_ENDPOINT, [])
    if endpoints:
        source_records = endpoints
    else:
        source_records = records.get(LOG_TYPE_RUN, [])

    for record in source_records:
        baseline_id = _baseline_id(record)
        baseline_records.append({
            "BaselineId": baseline_id,
            "BaselineRunId": record.get("RunId", "unknown"),
            "BaselineBuildId": record.get("BuildId", "local"),
            "BaselineBuildNumber": record.get("BuildNumber", "local"),
            "Environment": record.get("Environment", "unknown"),
            "ServiceName": record.get("ServiceName", "unknown"),
            "ScenarioName": record.get("ScenarioName", "unknown"),
            "Endpoint": record.get("Endpoint", "Aggregated"),
            "Method": record.get("Method", ""),
            "RequestName": record.get("RequestName", record.get("ScenarioName", "Aggregated")),
            "LoadProfile": record.get("LoadProfile", "1x"),
            "LoadMultiplier": _safe_float(record.get("LoadMultiplier"), 1.0),
            "Users": _safe_float(record.get("Users"), 0.0),
            "SpawnRate": _safe_float(record.get("SpawnRate"), 0.0),
            "RunTimeSeconds": _safe_float(record.get("RunTimeSeconds"), 0.0),
            "TargetRps": _safe_float(record.get("TargetRps"), 0.0),
            "BaselineAvgMs": _safe_float(record.get("AvgResponseTimeMs"), 0.0),
            "BaselineP50Ms": _safe_float(record.get("P50ResponseTimeMs"), 0.0),
            "BaselineP90Ms": _safe_float(record.get("P90ResponseTimeMs"), 0.0),
            "BaselineP95Ms": _safe_float(record.get("P95ResponseTimeMs"), 0.0),
            "BaselineP99Ms": _safe_float(record.get("P99ResponseTimeMs"), 0.0),
            "BaselineRps": _safe_float(record.get("RequestsPerSecond"), 0.0),
            "BaselineFailureRate": _safe_float(record.get("FailureRate"), 0.0),
            "ApprovedBy": approved_by or _optional_env("BUILD_REQUESTEDFOR") or _optional_env("USERNAME") or "unknown",
            "ApprovedOn": approved_on,
            "Reason": reason or _optional_env("BASELINE_REASON") or "Approved performance baseline",
            "IsActive": True,
        })
    return baseline_records


def push_performance_results(
    reports_path: Optional[str] = None,
    csv_base: Optional[str] = None,
    dry_run: bool = False,
    promote_baseline: bool = False,
    baseline_reason: Optional[str] = None,
    approved_by: Optional[str] = None,
    service_name: Optional[str] = None,
    environment_name: Optional[str] = None,
    load_profile: Optional[str] = None,
    load_multiplier: Optional[float] = None,
    include_timeseries: Optional[bool] = None,
) -> bool:
    enabled = os.environ.get("LOG_ANALYTICS_ENABLED", "true").strip().lower()
    if enabled not in {"true", "1", "yes", "y"}:
        logger.info("[Performance Log Analytics] Disabled by LOG_ANALYTICS_ENABLED")
        return True

    report_dir = find_report_dir(reports_path)
    csv_base_path = Path(csv_base) if csv_base else None
    if csv_base_path and not csv_base_path.is_absolute():
        csv_base_path = get_project_path(str(csv_base_path))

    if include_timeseries is None:
        include_timeseries = os.environ.get("PERF_LOG_ANALYTICS_TIMESERIES_ENABLED", "true").strip().lower() in {
            "true", "1", "yes", "y"
        }

    artifacts = LocustPerformanceArtifacts(report_dir, csv_base_path)
    records = build_records(
        artifacts,
        service_name=service_name,
        environment_name=environment_name,
        load_profile=load_profile,
        load_multiplier=load_multiplier,
        include_timeseries=include_timeseries,
    )

    if promote_baseline:
        records[LOG_TYPE_BASELINE] = build_baseline_records(records, approved_by=approved_by, reason=baseline_reason)

    if dry_run:
        print(json.dumps(records, indent=2, default=str))
        return True

    workspace_id = os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")
    shared_key = os.environ.get("LOG_ANALYTICS_SHARED_KEY")
    if not workspace_id or not shared_key:
        logger.error("[Performance Log Analytics] Missing LOG_ANALYTICS_WORKSPACE_ID or LOG_ANALYTICS_SHARED_KEY")
        return False

    client = PerformanceLogAnalyticsClient(workspace_id, shared_key)
    ok = True
    for log_type in [LOG_TYPE_RUN, LOG_TYPE_ENDPOINT, LOG_TYPE_TIMESERIES, LOG_TYPE_FAILURE, LOG_TYPE_BASELINE]:
        ok = client.post_records(log_type, records.get(log_type, [])) and ok

    if ok:
        logger.info("[Performance Log Analytics] Performance records pushed successfully")
        logger.info("[Performance Log Analytics] Custom tables may take 5-15 minutes to appear after first ingestion")
    return ok


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        logger.warning("[Performance Log Analytics] CSV file not found: %s", path)
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file_handle:
        return [row for row in csv.DictReader(file_handle) if row and any((value or "").strip() for value in row.values())]


def _parse_metadata(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        logger.warning("[Performance Log Analytics] Metadata file not found: %s", path)
        return {}
    sections: Dict[str, Dict[str, str]] = {}
    current_section = "General"
    sections[current_section] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections.setdefault(current_section, {})
            continue
        if line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            sections.setdefault(current_section, {})[key.strip()] = value.strip()
    return sections


def _build_common_fields(
    run_id: str,
    service_name: str,
    environment_name: str,
    load_profile: str,
    load_multiplier: float,
    test_params: Dict[str, str],
    command_args: Dict[str, str],
    generated_at: str,
) -> Dict[str, Any]:
    users = _first_number(command_args.get("users (-u)"), test_params.get("users"), _optional_env("LOCUST_USERS"))
    spawn_rate = _first_number(command_args.get("spawn_rate (-r)"), _optional_env("LOCUST_SPAWN_RATE"))
    run_time_seconds = _parse_duration_seconds(command_args.get("run_time (-t)") or _optional_env("LOCUST_RUN_TIME"))
    target_rps = _first_number(test_params.get("target_rps"), _optional_env("LOCUST_TARGET_RPS"))
    return {
        "RunId": run_id,
        "ExecutionTimestamp": generated_at,
        "Environment": environment_name,
        "ServiceName": service_name,
        "ScenarioName": test_params.get("test_type") or _optional_env("PERF_SCENARIO_NAME") or "Performance",
        "TestFile": test_params.get("file") or "",
        "LoadProfile": load_profile,
        "LoadMultiplier": float(load_multiplier or 1.0),
        "Users": users,
        "SpawnRate": spawn_rate,
        "RunTimeSeconds": run_time_seconds,
        "TargetRps": target_rps,
        "BuildId": _optional_env("BUILD_BUILDID") or "local",
        "BuildNumber": _optional_env("BUILD_BUILDNUMBER") or "local",
        "PipelineId": _optional_env("SYSTEM_DEFINITIONID") or "unknown",
        "PipelineName": _optional_env("BUILD_DEFINITIONNAME") or "unknown",
        "SourceBranch": _optional_env("BUILD_SOURCEBRANCHNAME") or _optional_env("BUILD_SOURCEBRANCH") or "unknown",
        "CommitSha": _optional_env("BUILD_SOURCEVERSION") or "unknown",
        "RequestedFor": _optional_env("BUILD_REQUESTEDFOR") or "unknown",
        "AzureDevOpsBuildUrl": _build_azure_devops_url(),
    }


def _build_run_record(
    common: Dict[str, Any],
    aggregate_row: Dict[str, str],
    system_metrics: Dict[str, str],
    artifacts: LocustPerformanceArtifacts,
) -> Dict[str, Any]:
    record = dict(common)
    record.update(_metrics_from_stats_row(aggregate_row))
    record.update({
        "Endpoint": "Aggregated",
        "Method": aggregate_row.get("Type", ""),
        "RequestName": aggregate_row.get("Name", "Aggregated") or "Aggregated",
        "BaselineStatus": STATUS_NO_BASELINE,
        "ReportHtmlPath": _path_to_string(artifacts.html_path),
        "ExecutiveSummaryPath": _path_to_string(artifacts.executive_summary_path),
        "CpuAvgPercent": _safe_float(system_metrics.get("cpu_avg_percent"), 0.0),
        "MemoryDeltaGb": _safe_float(system_metrics.get("memory_delta_gb"), 0.0),
        "NetworkSentMb": _safe_float(system_metrics.get("network_sent_mb"), 0.0),
        "NetworkRecvMb": _safe_float(system_metrics.get("network_recv_mb"), 0.0),
    })
    record["BaselineId"] = _baseline_id(record)
    duration = _safe_float(system_metrics.get("test_duration_sec"), None)
    if duration is not None:
        record["DurationSeconds"] = duration
    return record


def _build_endpoint_record(common: Dict[str, Any], row: Dict[str, str]) -> Dict[str, Any]:
    record = dict(common)
    record.update(_metrics_from_stats_row(row))
    record.update({
        "Endpoint": row.get("Name", "unknown") or "unknown",
        "Method": row.get("Type", ""),
        "RequestName": row.get("Name", "unknown") or "unknown",
        "BaselineStatus": STATUS_NO_BASELINE,
    })
    record["BaselineId"] = _baseline_id(record)
    return record


def _build_timeseries_record(common: Dict[str, Any], row: Dict[str, str]) -> Dict[str, Any]:
    record = {
        "RunId": common["RunId"],
        "Environment": common["Environment"],
        "ServiceName": common["ServiceName"],
        "LoadProfile": common["LoadProfile"],
        "LoadMultiplier": common["LoadMultiplier"],
        "BuildId": common["BuildId"],
        "BuildNumber": common["BuildNumber"],
        "Timestamp": _timestamp_from_epoch(row.get("Timestamp")),
        "Users": _safe_float(row.get("User Count"), 0.0),
        "Endpoint": row.get("Name", "Aggregated") or "Aggregated",
        "Method": row.get("Type", ""),
        "RequestName": row.get("Name", "Aggregated") or "Aggregated",
        "RequestsPerSecond": _safe_float(row.get("Requests/s"), 0.0),
        "FailuresPerSecond": _safe_float(row.get("Failures/s"), 0.0),
        "P50ResponseTimeMs": _safe_float(row.get("50%"), 0.0),
        "P90ResponseTimeMs": _safe_float(row.get("90%"), 0.0),
        "P95ResponseTimeMs": _safe_float(row.get("95%"), 0.0),
        "P99ResponseTimeMs": _safe_float(row.get("99%"), 0.0),
        "TotalRequests": _safe_float(row.get("Total Request Count"), 0.0),
        "TotalFailures": _safe_float(row.get("Total Failure Count"), 0.0),
        "AvgResponseTimeMs": _safe_float(row.get("Total Average Response Time"), 0.0),
        "MinResponseTimeMs": _safe_float(row.get("Total Min Response Time"), 0.0),
        "MaxResponseTimeMs": _safe_float(row.get("Total Max Response Time"), 0.0),
    }
    total_requests = record["TotalRequests"]
    total_failures = record["TotalFailures"]
    record["FailureRate"] = (total_failures / total_requests * 100.0) if total_requests else 0.0
    return record


def _build_failure_records(
    common: Dict[str, Any],
    failures: List[Dict[str, str]],
    exceptions: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for row in failures:
        if _is_blank_csv_row(row):
            continue
        records.append(_failure_record(common, row, "failure"))
    for row in exceptions:
        if _is_blank_csv_row(row):
            continue
        records.append(_failure_record(common, row, "exception"))
    return records


def _failure_record(common: Dict[str, Any], row: Dict[str, str], failure_type: str) -> Dict[str, Any]:
    name = row.get("Name") or row.get("Request Name") or "unknown"
    method = row.get("Method") or row.get("Type") or ""
    error = row.get("Error") or row.get("Exception") or row.get("Traceback") or ""
    return {
        "RunId": common["RunId"],
        "Environment": common["Environment"],
        "ServiceName": common["ServiceName"],
        "LoadProfile": common["LoadProfile"],
        "BuildId": common["BuildId"],
        "BuildNumber": common["BuildNumber"],
        "Endpoint": name,
        "Method": method,
        "RequestName": name,
        "FailureType": failure_type,
        "ErrorMessage": error[:1000],
        "Occurrences": _safe_float(row.get("Occurrences") or row.get("Count"), 0.0),
        "StackTrace": (row.get("Traceback") or row.get("Stack Trace") or "")[:4000],
    }


def _metrics_from_stats_row(row: Dict[str, str]) -> Dict[str, Any]:
    total_requests = _safe_float(row.get("Request Count"), 0.0)
    total_failures = _safe_float(row.get("Failure Count"), 0.0)
    return {
        "TotalRequests": total_requests,
        "TotalFailures": total_failures,
        "FailureRate": (total_failures / total_requests * 100.0) if total_requests else 0.0,
        "RequestsPerSecond": _safe_float(row.get("Requests/s"), 0.0),
        "FailuresPerSecond": _safe_float(row.get("Failures/s"), 0.0),
        "AvgResponseTimeMs": _safe_float(row.get("Average Response Time"), 0.0),
        "MinResponseTimeMs": _safe_float(row.get("Min Response Time"), 0.0),
        "MaxResponseTimeMs": _safe_float(row.get("Max Response Time"), 0.0),
        "MedianResponseTimeMs": _safe_float(row.get("Median Response Time"), 0.0),
        "P50ResponseTimeMs": _safe_float(row.get("50%"), 0.0),
        "P90ResponseTimeMs": _safe_float(row.get("90%"), 0.0),
        "P95ResponseTimeMs": _safe_float(row.get("95%"), 0.0),
        "P98ResponseTimeMs": _safe_float(row.get("98%"), 0.0),
        "P99ResponseTimeMs": _safe_float(row.get("99%"), 0.0),
        "P999ResponseTimeMs": _safe_float(row.get("99.9%"), 0.0),
        "AverageContentSize": _safe_float(row.get("Average Content Size"), 0.0),
    }


def _find_aggregate_row(rows: List[Dict[str, str]]) -> Dict[str, str]:
    for row in rows:
        if _is_aggregate_row(row):
            return row
    return rows[0] if rows else {}


def _is_aggregate_row(row: Dict[str, str]) -> bool:
    return (row.get("Name") or "").strip().lower() == "aggregated"


def _is_blank_csv_row(row: Dict[str, str]) -> bool:
    return not any((value or "").strip() for value in row.values())


def _safe_float(value: Any, default: Optional[float] = 0.0) -> Optional[float]:
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.strip()
            if value == "" or value.upper() == "N/A" or value.lower() == "none":
                return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _first_number(*values: Any) -> float:
    for value in values:
        parsed = _safe_float(value, None)
        if parsed is not None:
            return parsed
    return 0.0


def _parse_duration_seconds(value: Any) -> float:
    if value is None:
        return 0.0
    raw = str(value).strip().lower()
    if not raw or raw == "n/a":
        return 0.0
    if raw.endswith("ms"):
        return _safe_float(raw[:-2], 0.0) / 1000.0
    if raw.endswith("s"):
        return _safe_float(raw[:-1], 0.0)
    if raw.endswith("m"):
        return _safe_float(raw[:-1], 0.0) * 60.0
    if raw.endswith("h"):
        return _safe_float(raw[:-1], 0.0) * 3600.0
    return _safe_float(raw, 0.0)


def _timestamp_from_epoch(value: Any) -> str:
    parsed = _safe_float(value, None)
    if parsed is None:
        return _utc_now()
    try:
        return datetime.fromtimestamp(parsed, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return _utc_now()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compact_timestamp(iso_value: str) -> str:
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError:
        parsed = datetime.now(timezone.utc)
    return parsed.strftime("%Y%m%d_%H%M%S")


def _clean_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def _infer_service_from_file(file_value: Optional[str]) -> Optional[str]:
    if not file_value:
        return None
    parts = Path(file_value.replace("\\", "/")).parts
    if "testdata" in parts:
        index = parts.index("testdata")
        if len(parts) > index + 1:
            return parts[index + 1]
    return None


def _infer_load_profile(command_args: Dict[str, str], test_params: Dict[str, str]) -> str:
    explicit = _optional_env("PERF_LOAD_PROFILE")
    if explicit:
        return explicit
    users = _first_number(command_args.get("users (-u)"), test_params.get("users"))
    if users <= 0:
        return "1x"
    return f"{int(users)}u"


def _load_multiplier_from_profile(load_profile: str) -> float:
    match = re.match(r"^(\d+(?:\.\d+)?)x$", (load_profile or "").strip().lower())
    if match:
        return float(match.group(1))
    return 1.0


def _baseline_id(record: Dict[str, Any]) -> str:
    return _clean_id(
        "_".join([
            str(record.get("ServiceName", "unknown")),
            str(record.get("Environment", "unknown")),
            str(record.get("Method", "")),
            str(record.get("Endpoint", record.get("RequestName", "Aggregated"))),
            str(record.get("LoadProfile", "1x")),
        ])
    )


def _build_azure_devops_url() -> str:
    collection = (_optional_env("SYSTEM_COLLECTIONURI") or _optional_env("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI") or "").rstrip("/")
    project = _optional_env("SYSTEM_TEAMPROJECT") or ""
    build_id = _optional_env("BUILD_BUILDID") or ""
    if collection and project and build_id:
        return f"{collection}/{project}/_build/results?buildId={build_id}&view=results"
    return _optional_env("BUILD_BUILDURI") or ""


def _optional_env(name: str) -> Optional[str]:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    if not value or re.fullmatch(r"\$\([^)]+\)", value):
        return None
    return value


def _path_to_string(path: Path) -> str:
    return str(path) if path.exists() else ""


def _chunks(records: List[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    for index in range(0, len(records), size):
        yield records[index:index + size]


def main() -> int:
    parser = argparse.ArgumentParser(description="Push Locust performance results to Azure Log Analytics")
    parser.add_argument("--reports-path", help="Report directory. Defaults to latest reports/<timestamp> directory.")
    parser.add_argument("--csv-base", help="Locust CSV base path, for example reports/20260509/performance_report")
    parser.add_argument("--dry-run", action="store_true", help="Print records instead of posting to Log Analytics")
    parser.add_argument("--promote-baseline", action="store_true", help="Promote the current run as an active baseline")
    parser.add_argument("--baseline-reason", help="Reason stored on promoted baseline records")
    parser.add_argument("--approved-by", help="Approver stored on promoted baseline records")
    parser.add_argument("--service-name", help="Override service name")
    parser.add_argument("--environment", help="Override environment name")
    parser.add_argument("--load-profile", help="Override load profile, for example 1x, 2x, 50u")
    parser.add_argument("--load-multiplier", type=float, help="Override numeric load multiplier")
    parser.add_argument("--skip-timeseries", action="store_true", help="Do not push PerfTimeSeries records")
    args = parser.parse_args()

    success = push_performance_results(
        reports_path=args.reports_path,
        csv_base=args.csv_base,
        dry_run=args.dry_run,
        promote_baseline=args.promote_baseline,
        baseline_reason=args.baseline_reason,
        approved_by=args.approved_by,
        service_name=args.service_name,
        environment_name=args.environment,
        load_profile=args.load_profile,
        load_multiplier=args.load_multiplier,
        include_timeseries=not args.skip_timeseries,
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
