"""
Alpha/Beta/Sharpe/Information Ratio Validator

Validator for analytics POST payloads using:
- analyticsApiServices/payloads/Payload_Alpha_Beta_InfoRatio_SarpeRatio_POST.txt

What this validator enforces:
1. Required payload inputs are present and structurally valid:
   - Model IDs (at least Model_1 and Model_2)
   - Benchmark ID
   - Risk-free rate ID (for alpha and sharpe ratio)
   - Blend weights are numeric and sum to 1.0
2. Monthly performance lists exist for required IDs and contain numeric values.
3. Payload date and time-horizon consistency checks:
   - startDate <= endDate
   - endDate is month-end
   - timeHorizon values are recognized
4. Response format checks for cumulative fields and horizon metric outputs.
5. Basic recomputation checks from monthly data for:
   - Alpha, Beta, Sharpe Ratio, Information Ratio

This script follows the framework's ScriptResult contract and can be attached via
"scripts": ["analyticsApiServices/validators/alpha_beta_info_sharpe_validator.py"]
"""

from __future__ import annotations

import json
import math
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from framework.clients.api_client import ApiClientFactory
from framework.common.logger import get_logger

logger = get_logger(__name__)


SUPPORTED_CALC_TYPES = {
    "alpha": "Alpha",
    "beta": "Beta",
    "sharpe ratio": "SharpeRatio",
    "sharperatio": "SharpeRatio",
    "information ratio": "InformationRatio",
    "informationratio": "InformationRatio",
}

SUPPORTED_HORIZONS = {
    "threeyear": 36,
    "fiveyear": 60,
    "tenyear": 120,
    "twentyyear": 240,
}


def _ci_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    if not isinstance(data, dict):
        return default
    if key in data:
        return data[key]
    key_lower = str(key).lower()
    for existing_key, value in data.items():
        if str(existing_key).lower() == key_lower:
            return value
    return default


def _normalize_calc_type(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace("_", " ").replace("-", " ")


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_month_end(date_obj: datetime) -> bool:
    next_day = date_obj.replace(day=min(28, date_obj.day))
    while True:
        try:
            next_day = next_day.replace(day=next_day.day + 1)
        except ValueError:
            break
    return date_obj.day == next_day.day


def _parse_date(date_text: str) -> Optional[datetime]:
    if not date_text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    return None


def _sample_variance(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)


def _sample_covariance(x_values: List[float], y_values: List[float]) -> float:
    n = min(len(x_values), len(y_values))
    if n < 2:
        return 0.0
    x = x_values[:n]
    y = y_values[:n]
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    return sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / (n - 1)


def _cumulative_return(returns: List[float]) -> float:
    cumulative = 1.0
    for value in returns:
        cumulative *= (1.0 + value)
    return cumulative - 1.0


def _blend_returns(model_returns: Dict[str, List[Tuple[str, float]]], blend: List[Dict[str, Any]]) -> Dict[str, float]:
    weighted_by_date: Dict[str, float] = defaultdict(float)
    for model in blend:
        model_id = _ci_get(model, "id")
        weight = _safe_float(_ci_get(model, "weight"))
        series = model_returns.get(str(model_id), [])
        if weight is None:
            continue
        for dt, r in series:
            weighted_by_date[dt] += r * weight
    return dict(weighted_by_date)


def _to_sorted_pairs(date_map: Dict[str, float]) -> List[Tuple[str, float]]:
    return sorted(date_map.items(), key=lambda x: x[0])


def _compute_metrics(blended: List[float], benchmark: List[float], risk_free: List[float]) -> Dict[str, float]:
    n = min(len(blended), len(benchmark), len(risk_free))
    if n < 2:
        return {"alpha": 0.0, "beta": 0.0, "sharpe_ratio": 0.0, "information_ratio": 0.0}

    b = blended[:n]
    m = benchmark[:n]
    rf = risk_free[:n]

    excess_blended = [b[i] - rf[i] for i in range(n)]
    excess_benchmark = [m[i] - rf[i] for i in range(n)]
    active = [b[i] - m[i] for i in range(n)]

    var_excess_benchmark = _sample_variance(excess_benchmark)
    beta = 0.0 if var_excess_benchmark == 0 else (_sample_covariance(excess_blended, excess_benchmark) / var_excess_benchmark)

    mean_excess_blended = sum(excess_blended) / n
    mean_excess_benchmark = sum(excess_benchmark) / n
    alpha_monthly = mean_excess_blended - (beta * mean_excess_benchmark)
    alpha_annualized = alpha_monthly * 12

    std_excess_blended = math.sqrt(_sample_variance(excess_blended))
    sharpe_ratio = 0.0 if std_excess_blended == 0 else (mean_excess_blended / std_excess_blended) * math.sqrt(12)

    mean_active = sum(active) / n
    std_active = math.sqrt(_sample_variance(active))
    information_ratio = 0.0 if std_active == 0 else (mean_active / std_active) * math.sqrt(12)

    return {
        "alpha": alpha_annualized,
        "beta": beta,
        "sharpe_ratio": sharpe_ratio,
        "information_ratio": information_ratio,
    }


class MonthlyPerformanceDataFetcher:
    """Fetch monthly performance values from strategies API for IDs."""

    def __init__(self):
        self._strategies_client = None
        self._token_client = None
        self.token = None

    def _get_strategies_client(self):
        if self._strategies_client is None:
            try:
                self._strategies_client = ApiClientFactory.get_client("strategies")
            except (ValueError, KeyError) as exc:
                logger.error(f"Could not get strategies client: {exc}")
        return self._strategies_client

    def _get_token_client(self):
        if self._token_client is None:
            try:
                self._token_client = ApiClientFactory.get_client("wrapToken")
            except (ValueError, KeyError) as exc:
                logger.warning(f"Could not get wrapToken client: {exc}")
        return self._token_client

    def _get_auth_token(self) -> Optional[str]:
        token_client = self._get_token_client()
        if not token_client:
            return None
        try:
            response = token_client.request("GET", "")
            if response.status_code != 200:
                return None
            try:
                data = response.json()
            except Exception:
                data = response.text

            if isinstance(data, dict):
                token = (
                    data.get("access_token")
                    or data.get("token")
                    or data.get("Token")
                    or data.get("userToken")
                    or data.get("UserToken")
                )
                if token:
                    return str(token)

            raw = str(data).strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            return raw.replace('\\"', '"')
        except Exception as exc:
            logger.warning(f"Failed to fetch auth token: {exc}")
            return None

    def fetch_monthly_performance(self, item_ids: List[str], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        client = self._get_strategies_client()
        if not client:
            return []

        if not self.token:
            self.token = self._get_auth_token()
            if self.token:
                client.auth_token = self.token

        endpoint = f"/models/monthlyperformancelist?fromMonth={start_date}&toMonth={end_date}"
        headers = {"Content-Type": "application/json", "accept": "application/json"}
        if self.token:
            headers["Authorization"] = self.token

        try:
            response = client.request("POST", endpoint, headers=headers, json=item_ids)
            if response.status_code != 200:
                logger.error(f"Monthly performance request failed: {response.status_code}")
                return []
            payload = response.json()
            if isinstance(payload, list):
                return payload
            return []
        except Exception as exc:
            logger.error(f"Monthly performance fetch failed: {exc}")
            return []


def _parse_payload(raw_payload: Any) -> Dict[str, Any]:
    if isinstance(raw_payload, dict):
        return raw_payload
    if isinstance(raw_payload, str):
        try:
            return json.loads(raw_payload)
        except json.JSONDecodeError:
            return {}
    return {}


def _extract_time_horizons(config: Dict[str, Any]) -> List[str]:
    value = _ci_get(config, "timeHorizon")
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _extract_calc_result(api_response: Dict[str, Any], requested_type: str) -> Optional[Dict[str, Any]]:
    calc_results = _ci_get(api_response, "calculationResults", [])
    if not isinstance(calc_results, list):
        return None

    requested_normalized = _normalize_calc_type(requested_type)
    for calc in calc_results:
        calc_type = _normalize_calc_type(_ci_get(calc, "calculationType", ""))
        if calc_type == requested_normalized:
            return calc
    return calc_results[0] if calc_results else None


def _build_model_series(rows: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, float]]]:
    grouped: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for row in rows:
        model_id = row.get("modelId") or row.get("id")
        date_value = row.get("monthEndDate") or row.get("date")
        perf_value = row.get("monthEndPerformance")
        if perf_value is None:
            perf_value = row.get("return")
        numeric = _safe_float(perf_value)
        if model_id and date_value and numeric is not None:
            grouped[str(model_id)].append((str(date_value), numeric))

    for model_id in list(grouped.keys()):
        grouped[model_id] = sorted(grouped[model_id], key=lambda x: x[0])
    return grouped


def validate(context: Any) -> Dict[str, Any]:
    try:
        if hasattr(context, "to_dict"):
            ctx = context.to_dict()
        elif isinstance(context, dict):
            ctx = context
        else:
            return {
                "success": False,
                "errors": [f"Invalid context type: {type(context)}"],
                "extracted_values": {},
                "computed_values": {},
            }

        errors: List[str] = []

        request_ctx = ctx.get("request", {}) if isinstance(ctx, dict) else {}
        response_ctx = ctx.get("response", {}) if isinstance(ctx, dict) else {}
        extracted_vars = ctx.get("extracted_vars", {}) if isinstance(ctx, dict) else {}

        request_payload = _parse_payload(request_ctx.get("payload"))
        if not request_payload:
            request_payload = _parse_payload(extracted_vars.get("api_request"))

        api_response = response_ctx.get("body", {}) if isinstance(response_ctx, dict) else {}

        if not request_payload:
            return {
                "success": False,
                "errors": ["No rendered request payload found in context"],
                "extracted_values": {},
                "computed_values": {},
            }

        if not api_response:
            return {
                "success": False,
                "errors": ["No API response body found in context"],
                "extracted_values": {},
                "computed_values": {},
            }

        calc_request = _ci_get(request_payload, "calculationRequest", {})
        inputs = _ci_get(calc_request, "inputs", {})
        calculations = _ci_get(calc_request, "calculations", [])

        if not isinstance(calculations, list) or not calculations:
            errors.append("Payload must include at least one calculation definition")
            calculations = [{}]

        first_calc = calculations[0] if isinstance(calculations[0], dict) else {}
        calc_type_raw = _ci_get(first_calc, "calculationType", "")
        calc_type = _normalize_calc_type(calc_type_raw)
        calc_metric_key = SUPPORTED_CALC_TYPES.get(calc_type)
        if not calc_metric_key:
            errors.append(f"Unsupported calculationType '{calc_type_raw}' for this validator")

        configurations = _ci_get(first_calc, "configurations", {})
        start_date_text = str(_ci_get(configurations, "startDate", "") or "").strip()
        end_date_text = str(_ci_get(configurations, "endDate", "") or "").strip()
        start_date = _parse_date(start_date_text)
        end_date = _parse_date(end_date_text)

        if not start_date:
            errors.append("configurations.startDate is missing or not a valid date")
        if not end_date:
            errors.append("configurations.endDate is missing or not a valid date")
        if start_date and end_date and start_date > end_date:
            errors.append("configurations.startDate must be <= configurations.endDate")
        if end_date and not _is_month_end(end_date):
            errors.append("configurations.endDate must be a month-end date")

        time_horizons = _extract_time_horizons(configurations)
        if not time_horizons:
            errors.append("configurations.timeHorizon is required and must contain at least one value")

        invalid_horizons = [h for h in time_horizons if str(h).strip().lower() not in SUPPORTED_HORIZONS]
        if invalid_horizons:
            errors.append(f"Unsupported timeHorizon value(s): {invalid_horizons}")

        blend = _ci_get(inputs, "blend", [])
        if not isinstance(blend, list) or len(blend) < 2:
            errors.append("inputs.blend must contain at least two models (Model_1 and Model_2)")
            blend = blend if isinstance(blend, list) else []

        benchmark = _ci_get(inputs, "benchmark", [])
        benchmark_ids: List[str] = []
        if isinstance(benchmark, list):
            benchmark_ids = [str(x).strip() for x in benchmark if str(x).strip()]
        elif isinstance(benchmark, str) and benchmark.strip():
            benchmark_ids = [benchmark.strip()]

        if not benchmark_ids:
            errors.append("inputs.benchmark must include at least one benchmark ID")

        risk_free_rate_id = str(_ci_get(configurations, "riskFreeRate", "") or "").strip()
        if calc_type in ("alpha", "sharpe ratio", "sharperatio") and not risk_free_rate_id:
            errors.append("configurations.riskFreeRate is required for alpha/sharpe ratio")

        weight_values: List[float] = []
        model_ids: List[str] = []
        for idx, model in enumerate(blend):
            if not isinstance(model, dict):
                errors.append(f"inputs.blend[{idx}] must be an object")
                continue
            model_id = str(_ci_get(model, "id", "") or "").strip()
            entity_type = str(_ci_get(model, "entityType", "") or "").strip().lower()
            weight = _safe_float(_ci_get(model, "weight"))

            if not model_id:
                errors.append(f"inputs.blend[{idx}].id is required")
            else:
                model_ids.append(model_id)

            if entity_type != "model":
                errors.append(f"inputs.blend[{idx}].entityType must be 'model'")

            if weight is None:
                errors.append(f"inputs.blend[{idx}].weight must be numeric")
            elif weight < 0:
                errors.append(f"inputs.blend[{idx}].weight must be non-negative")
            else:
                weight_values.append(weight)

        if len(weight_values) >= 2:
            total_weight = sum(weight_values)
            if abs(total_weight - 1.0) > 0.0001:
                errors.append(f"Blend weights must sum to 1.0 (actual={total_weight:.8f})")

        required_ids = list(dict.fromkeys(model_ids + benchmark_ids + ([risk_free_rate_id] if risk_free_rate_id else [])))

        monthly_rows: List[Dict[str, Any]] = []
        model_series: Dict[str, List[Tuple[str, float]]] = {}

        if start_date_text and end_date_text and required_ids:
            fetcher = MonthlyPerformanceDataFetcher()
            monthly_rows = fetcher.fetch_monthly_performance(required_ids, start_date_text, end_date_text)
            model_series = _build_model_series(monthly_rows)

            for req_id in required_ids:
                if req_id not in model_series:
                    errors.append(f"Monthly performance data not found for ID '{req_id}'")
                    continue
                if not model_series[req_id]:
                    errors.append(f"Monthly performance list is empty for ID '{req_id}'")

        # Build blended / benchmark / risk-free aligned returns for computations.
        blended_by_date = _blend_returns(model_series, blend) if model_series and blend else {}
        benchmark_by_date = dict(model_series.get(benchmark_ids[0], [])) if benchmark_ids else {}
        risk_free_by_date = dict(model_series.get(risk_free_rate_id, [])) if risk_free_rate_id else {}

        common_dates = sorted(set(blended_by_date.keys()) & set(benchmark_by_date.keys()))
        if risk_free_by_date:
            common_dates = [d for d in common_dates if d in risk_free_by_date]

        blended_returns = [blended_by_date[d] for d in common_dates]
        benchmark_returns = [benchmark_by_date[d] for d in common_dates]
        risk_free_returns = [risk_free_by_date[d] for d in common_dates] if risk_free_by_date else [0.0 for _ in common_dates]

        if common_dates and len(common_dates) < 12:
            errors.append("Insufficient overlapping monthly data (<12 months) for robust ratio metrics")

        computed_blend_cumulative = _cumulative_return(blended_returns) if blended_returns else None
        computed_benchmark_cumulative = _cumulative_return(benchmark_returns) if benchmark_returns else None
        computed_risk_free_cumulative = _cumulative_return(risk_free_returns) if risk_free_returns else None

        # Validate response structure and metric values.
        calc_result = _extract_calc_result(api_response, calc_type_raw)
        if not calc_result:
            errors.append("No calculation result found in API response")
            calc_result = {}

        result_body = _ci_get(calc_result, "result", {})
        time_horizons_obj = _ci_get(result_body, "TimeHorizons") or _ci_get(result_body, "timeHorizons") or {}

        if not isinstance(time_horizons_obj, dict) or not time_horizons_obj:
            errors.append("Response Result.TimeHorizons is missing or empty")

        # Build computed metric windows for each horizon in response.
        computed_horizon_metrics: Dict[str, Dict[str, float]] = {}
        if common_dates:
            for horizon_name, response_item in (time_horizons_obj.items() if isinstance(time_horizons_obj, dict) else []):
                horizon_key = str(horizon_name).strip().lower()
                window_dates = common_dates

                if horizon_key in ("custom",):
                    custom_start = _parse_date(str(_ci_get(response_item, "StartDate", "") or ""))
                    custom_end = _parse_date(str(_ci_get(response_item, "EndDate", "") or ""))
                    if custom_start and custom_end:
                        if custom_start > custom_end:
                            errors.append("Response custom horizon StartDate must be <= EndDate")
                        if end_date and custom_end > end_date:
                            errors.append("Response custom horizon EndDate cannot exceed payload endDate")
                        window_dates = [d for d in common_dates if custom_start <= _parse_date(d) <= custom_end and _parse_date(d)]
                else:
                    months = SUPPORTED_HORIZONS.get(horizon_key)
                    if months:
                        if len(common_dates) < months:
                            errors.append(f"Not enough data points for {horizon_name}: need {months}, found {len(common_dates)}")
                        window_dates = common_dates[-months:] if len(common_dates) >= months else common_dates

                b_vals = [blended_by_date[d] for d in window_dates if d in blended_by_date]
                m_vals = [benchmark_by_date[d] for d in window_dates if d in benchmark_by_date]
                rf_vals = [risk_free_by_date[d] for d in window_dates if d in risk_free_by_date] if risk_free_by_date else [0.0 for _ in window_dates]

                metrics = _compute_metrics(b_vals, m_vals, rf_vals)
                computed_horizon_metrics[horizon_name] = metrics

                # Output formatting and observation checks.
                observations = _ci_get(response_item, "NumberOfObservations")
                if not isinstance(observations, int) or observations <= 0:
                    errors.append(f"{horizon_name}.NumberOfObservations must be a positive integer")

                if calc_type in ("alpha", "beta"):
                    beta_val = _safe_float(_ci_get(response_item, "Beta"))
                    if beta_val is None:
                        errors.append(f"{horizon_name}.Beta must be present and numeric")

                if calc_type == "alpha":
                    alpha_val = _safe_float(_ci_get(response_item, "Alpha"))
                    if alpha_val is None:
                        errors.append(f"{horizon_name}.Alpha must be present and numeric")
                    elif abs(alpha_val - metrics["alpha"]) > 0.03:
                        errors.append(
                            f"{horizon_name}.Alpha differs from recomputed value beyond tolerance "
                            f"(actual={alpha_val:.10f}, computed={metrics['alpha']:.10f})"
                        )

                if calc_type == "beta":
                    beta_val = _safe_float(_ci_get(response_item, "Beta"))
                    if beta_val is not None and abs(beta_val - metrics["beta"]) > 0.25:
                        errors.append(
                            f"{horizon_name}.Beta differs from recomputed value beyond tolerance "
                            f"(actual={beta_val:.10f}, computed={metrics['beta']:.10f})"
                        )

                if calc_type in ("sharpe ratio", "sharperatio"):
                    sharpe_val = _safe_float(_ci_get(response_item, "SharpeRatio"))
                    if sharpe_val is None:
                        errors.append(f"{horizon_name}.SharpeRatio must be present and numeric")
                    elif abs(sharpe_val - metrics["sharpe_ratio"]) > 0.35:
                        errors.append(
                            f"{horizon_name}.SharpeRatio differs from recomputed value beyond tolerance "
                            f"(actual={sharpe_val:.10f}, computed={metrics['sharpe_ratio']:.10f})"
                        )

                if calc_type in ("information ratio", "informationratio"):
                    info_val = _safe_float(_ci_get(response_item, "InformationRatio"))
                    if info_val is None:
                        errors.append(f"{horizon_name}.InformationRatio must be present and numeric")
                    elif abs(info_val - metrics["information_ratio"]) > 0.35:
                        errors.append(
                            f"{horizon_name}.InformationRatio differs from recomputed value beyond tolerance "
                            f"(actual={info_val:.10f}, computed={metrics['information_ratio']:.10f})"
                        )

        # General response field format checks from request context requirements.
        for field_name, value in (
            ("blended_return", _ci_get(result_body, "blendedReturn")),
            ("cumulative_return", _ci_get(result_body, "cumulativeReturn")),
            ("risk_free_cumulative_return", _ci_get(result_body, "riskFreeCumulativeReturn")),
            ("benchmark_cumulative_return", _ci_get(result_body, "benchmarkCumulativeReturn")),
        ):
            if value is not None and _safe_float(value) is None:
                errors.append(f"Response field '{field_name}' must be numeric when present")

        # Excel cell mapping placeholders requested by business sheet references.
        excel_output_cells = {
            "D55": computed_blend_cumulative,
            "D56": computed_benchmark_cumulative,
            "D57": computed_risk_free_cumulative,
            "D58": None,
            "D59": None,
            "D60": None,
            "B63": None,
            "B64": None,
        }

        # Populate from first available horizon metrics for downstream assertions.
        if computed_horizon_metrics:
            first_horizon = next(iter(computed_horizon_metrics.keys()))
            first_metrics = computed_horizon_metrics[first_horizon]
            excel_output_cells["D58"] = first_metrics.get("alpha")
            excel_output_cells["D59"] = first_metrics.get("beta")
            excel_output_cells["D60"] = first_metrics.get("sharpe_ratio")
            excel_output_cells["B63"] = first_metrics.get("information_ratio")

            first_response_item = _ci_get(time_horizons_obj, first_horizon, {}) if isinstance(time_horizons_obj, dict) else {}
            excel_output_cells["B64"] = _ci_get(first_response_item, "NumberOfObservations")

        computed_values = {
            "calculation_type": calc_type_raw,
            "blend_model_ids": model_ids,
            "benchmark_ids": benchmark_ids,
            "risk_free_rate_id": risk_free_rate_id,
            "time_horizons": time_horizons,
            "monthly_common_dates_count": len(common_dates),
            "computed_blended_cumulative_return": computed_blend_cumulative,
            "computed_benchmark_cumulative_return": computed_benchmark_cumulative,
            "computed_risk_free_cumulative_return": computed_risk_free_cumulative,
            "computed_horizon_metrics": computed_horizon_metrics,
            "excel_output_cells": excel_output_cells,
        }

        extracted_values = {
            "computed_blended_cumulative_return": computed_blend_cumulative,
            "computed_benchmark_cumulative_return": computed_benchmark_cumulative,
            "computed_risk_free_cumulative_return": computed_risk_free_cumulative,
            "excel_D55": excel_output_cells["D55"],
            "excel_D56": excel_output_cells["D56"],
            "excel_D57": excel_output_cells["D57"],
            "excel_D58": excel_output_cells["D58"],
            "excel_D59": excel_output_cells["D59"],
            "excel_D60": excel_output_cells["D60"],
            "excel_B63": excel_output_cells["B63"],
            "excel_B64": excel_output_cells["B64"],
        }

        return {
            "success": len(errors) == 0,
            "errors": errors,
            "extracted_values": extracted_values,
            "computed_values": computed_values,
            "metadata": {
                "validator": "alpha_beta_info_sharpe_validator",
                "supported_calculation_types": list(SUPPORTED_CALC_TYPES.keys()),
            },
        }

    except Exception as exc:
        logger.error(f"Alpha/Beta/Sharpe/InfoRatio validator failed: {exc}")
        logger.debug(traceback.format_exc())
        return {
            "success": False,
            "errors": [f"Validator exception: {str(exc)}"],
            "extracted_values": {},
            "computed_values": {},
        }


run = validate
