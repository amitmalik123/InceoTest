"""
Performance Executive Summary Reporter
======================================

Generates a custom executive-summary HTML next to Locust's native
``performance_report.html`` / ``*_stats.csv`` artifacts.

Charts are rendered with Apache ECharts (loaded from CDN) so they look
identical to (or better than) Locust's own report — interactive tooltips,
legend toggles, zoom, save-as-PNG.

No new Python dependencies — stdlib only.

Inputs (derived from the Locust ``--csv <base>`` prefix):
    <base>_stats.csv            (Locust per-endpoint stats)
    <base>_stats_history.csv    (Locust time-series)
    <base>_failures.csv         (Locust failure breakdown)
    <base>_exceptions.csv       (Locust exceptions, optional)
    <base>_metadata.txt         (written by locustfile.py: test params + sysinfo)

Output:
    <base>_executive_summary.html
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


# --------------------------------------------------------------------------- #
# Data loading helpers
# --------------------------------------------------------------------------- #

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "" or value == "N/A":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "" or value == "N/A":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return [row for row in csv.DictReader(f) if any((v or "").strip() for v in row.values())]


def _parse_metadata(path: Path) -> Tuple[Dict[str, Dict[str, str]], str]:
    """Parse metadata.txt into sectioned dicts and also return raw content."""
    sections: Dict[str, Dict[str, str]] = {}
    raw = ""
    if not path.exists():
        return sections, raw
    raw = path.read_text(encoding="utf-8")
    current = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("# "):
            continue
        if stripped.startswith("## "):
            current = stripped[3:].strip()
            sections[current] = {}
            continue
        if current and ":" in stripped:
            key, _, val = stripped.partition(":")
            sections[current][key.strip()] = val.strip()
    return sections, raw


def _aggregated_row(stats_rows: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    for row in stats_rows:
        if (row.get("Name") or "").strip().lower() == "aggregated":
            return row
    return stats_rows[-1] if stats_rows else None


def _format_seconds(ms: float) -> str:
    return f"{ms / 1000:.2f} sec"


def _max_rps_from_history(history_rows: List[Dict[str, str]]) -> float:
    max_rps = 0.0
    for row in history_rows:
        if (row.get("Name") or "").strip().lower() != "aggregated":
            continue
        rps = _safe_float(row.get("Requests/s"))
        if rps > max_rps:
            max_rps = rps
    return max_rps


# Industry-standard percentile columns exposed by Locust
_PCT_COLUMNS: List[Tuple[float, str]] = [
    (50.0, "50%"), (66.0, "66%"), (75.0, "75%"), (80.0, "80%"),
    (90.0, "90%"), (95.0, "95%"), (98.0, "98%"), (99.0, "99%"),
    (99.9, "99.9%"), (99.99, "99.99%"), (100.0, "100%"),
]


def _percentile_curve(row: Dict[str, str]) -> List[List[float]]:
    """Return [[percentile, response_time_ms], ...] for an aggregated stats row."""
    out: List[List[float]] = []
    for pct, col in _PCT_COLUMNS:
        v = _safe_float(row.get(col))
        if v > 0 or pct == 50.0:
            out.append([pct, v])
    return out


def _interp_percentile_at(curve: List[List[float]], target_ms: float) -> float:
    """Given a percentile curve, return the percentile (0-100) at which response
    time crosses target_ms. Used to approximate APDEX from Locust percentile cols."""
    if not curve:
        return 0.0
    if target_ms <= curve[0][1]:
        return 0.0
    if target_ms >= curve[-1][1]:
        return 100.0
    for i in range(1, len(curve)):
        p0, v0 = curve[i - 1]
        p1, v1 = curve[i]
        if v0 <= target_ms <= v1:
            if v1 == v0:
                return p1
            return p0 + (p1 - p0) * (target_ms - v0) / (v1 - v0)
    return 100.0


def _apdex(curve: List[List[float]], sla_seconds: float, fail_pct: float) -> Tuple[float, str, str]:
    """Compute APDEX score from percentile curve. Returns (score, rating, css_class).

    Industry standard (Apdex Alliance):
      Satisfied   : RT <= T
      Tolerating  : T < RT <= 4T
      Frustrated  : RT > 4T  OR  request failed

      score = (Satisfied + Tolerating/2) / Total
    """
    if not curve:
        return 0.0, "N/A", "warn"
    t_ms = sla_seconds * 1000.0
    pct_satisfied = _interp_percentile_at(curve, t_ms) / 100.0          # share <= T
    pct_tolerating_or_better = _interp_percentile_at(curve, 4 * t_ms) / 100.0  # share <= 4T
    satisfied = pct_satisfied
    tolerating = max(pct_tolerating_or_better - pct_satisfied, 0.0)
    # Failures are always Frustrated; reduce success-derived buckets accordingly.
    success_share = max(1.0 - fail_pct / 100.0, 0.0)
    score = (satisfied + tolerating / 2.0) * success_share
    score = max(0.0, min(1.0, score))
    if score >= 0.94:
        return score, "Excellent", "good"
    if score >= 0.85:
        return score, "Good", "good"
    if score >= 0.70:
        return score, "Fair", "warn"
    if score >= 0.50:
        return score, "Poor", "warn"
    return score, "Unacceptable", "bad"


# --------------------------------------------------------------------------- #
# Chart data preparation (consumed by ECharts on the client)
# --------------------------------------------------------------------------- #

def _build_chart_data(
    history_rows: List[Dict[str, str]],
    stats_rows: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Convert CSV rows into a JSON-serialisable structure for ECharts."""
    agg = [r for r in history_rows if (r.get("Name") or "").strip().lower() == "aggregated"]

    timestamps: List[str] = []
    for r in agg:
        ts = _safe_int(r.get("Timestamp"))
        if ts:
            try:
                timestamps.append(datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z"))
            except Exception:
                timestamps.append(str(ts))
        else:
            timestamps.append("")

    rps = [_safe_float(r.get("Requests/s")) for r in agg]
    fps = [_safe_float(r.get("Failures/s")) for r in agg]
    avg_ms = [_safe_float(r.get("Total Average Response Time")) for r in agg]
    median_ms = [_safe_float(r.get("Total Median Response Time")) for r in agg]
    p90 = [_safe_float(r.get("90%")) for r in agg]
    p95 = [_safe_float(r.get("95%")) for r in agg]
    p99 = [_safe_float(r.get("99%")) for r in agg]
    users = [_safe_int(r.get("User Count")) for r in agg]

    endpoint_names: List[str] = []
    endpoint_avg: List[float] = []
    endpoint_p95: List[float] = []
    endpoint_rps: List[float] = []
    endpoint_fail_pct: List[float] = []
    for r in stats_rows:
        name = (r.get("Name") or "").strip()
        if not name or name.lower() == "aggregated":
            continue
        endpoint_names.append(name)
        endpoint_avg.append(round(_safe_float(r.get("Average Response Time")), 2))
        endpoint_p95.append(round(_safe_float(r.get("95%")), 2))
        endpoint_rps.append(round(_safe_float(r.get("Requests/s")), 2))
        req = _safe_int(r.get("Request Count"))
        fail = _safe_int(r.get("Failure Count"))
        endpoint_fail_pct.append(round((fail / req * 100) if req else 0.0, 2))

    total_req = sum(_safe_int(r.get("Request Count")) for r in stats_rows
                    if (r.get("Name") or "").strip().lower() != "aggregated")
    total_fail = sum(_safe_int(r.get("Failure Count")) for r in stats_rows
                     if (r.get("Name") or "").strip().lower() != "aggregated")
    total_pass = max(total_req - total_fail, 0)

    # Aggregate percentile distribution curve (JMeter-style)
    agg_row = _aggregated_row(stats_rows) or {}
    agg_curve = _percentile_curve(agg_row)

    # Per-endpoint percentile curves (top 6 most-loaded endpoints)
    endpoint_curves: List[Dict[str, Any]] = []
    sorted_eps = sorted(
        [r for r in stats_rows if (r.get("Name") or "").strip().lower() != "aggregated"],
        key=lambda r: _safe_int(r.get("Request Count")), reverse=True
    )[:6]
    for r in sorted_eps:
        endpoint_curves.append({
            "name": (r.get("Name") or "").strip(),
            "curve": _percentile_curve(r),
        })

    # Top 10 slowest endpoints by P95
    slowest = sorted(
        [r for r in stats_rows if (r.get("Name") or "").strip().lower() != "aggregated"],
        key=lambda r: _safe_float(r.get("95%")), reverse=True
    )[:10]
    slowest_names = [(r.get("Name") or "").strip() for r in slowest]
    slowest_p95 = [round(_safe_float(r.get("95%")), 2) for r in slowest]
    slowest_p99 = [round(_safe_float(r.get("99%")), 2) for r in slowest]

    return {
        "timestamps": timestamps,
        "rps": rps,
        "failuresPerSec": fps,
        "avgMs": avg_ms,
        "medianMs": median_ms,
        "p90": p90,
        "p95": p95,
        "p99": p99,
        "users": users,
        "endpoints": {
            "names": endpoint_names,
            "avg": endpoint_avg,
            "p95": endpoint_p95,
            "rps": endpoint_rps,
            "failPct": endpoint_fail_pct,
        },
        "slowest": {
            "names": slowest_names,
            "p95": slowest_p95,
            "p99": slowest_p99,
        },
        "percentileCurve": agg_curve,
        "endpointCurves": endpoint_curves,
        "passFail": {"pass": total_pass, "fail": total_fail},
    }


# --------------------------------------------------------------------------- #
# Tables
# --------------------------------------------------------------------------- #

def _request_stats_table(stats_rows: List[Dict[str, str]]) -> str:
    if not stats_rows:
        return "<table><tr><td>No data available</td></tr></table>"
    head = (
        "<thead><tr><th>Type</th><th>Name</th><th>Requests</th><th>Failures</th>"
        "<th>RPS</th><th>Failure %</th><th>Avg Size (bytes)</th></tr></thead>"
    )
    body_rows = []
    for r in stats_rows:
        req = _safe_int(r.get("Request Count"))
        fail = _safe_int(r.get("Failure Count"))
        fpct = (fail / req * 100) if req else 0.0
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(r.get('Type') or '')}</td>"
            f"<td>{html.escape(r.get('Name') or '')}</td>"
            f"<td>{req}</td><td>{fail}</td>"
            f"<td>{_safe_float(r.get('Requests/s')):.2f}</td>"
            f"<td>{fpct:.2f}</td>"
            f"<td>{_safe_float(r.get('Average Content Size')):.2f}</td>"
            "</tr>"
        )
    return f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>"


def _response_time_table(stats_rows: List[Dict[str, str]]) -> str:
    if not stats_rows:
        return "<table><tr><td>No data available</td></tr></table>"
    head = (
        "<thead><tr><th>Type</th><th>Name</th><th>Median</th><th>Average</th>"
        "<th>Min</th><th>Max</th><th>P90</th><th>P95</th><th>P99</th></tr></thead>"
    )
    body_rows = []
    for r in stats_rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(r.get('Type') or '')}</td>"
            f"<td>{html.escape(r.get('Name') or '')}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('Median Response Time')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('Average Response Time')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('Min Response Time')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('Max Response Time')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('90%')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('95%')))}</td>"
            f"<td>{_format_seconds(_safe_float(r.get('99%')))}</td>"
            "</tr>"
        )
    return f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>"


def _failures_table(failure_rows: List[Dict[str, str]]) -> str:
    head = "<thead><tr><th>Method</th><th>Name</th><th>Error</th><th>Occurrences</th></tr></thead>"
    if not failure_rows:
        return f"<table>{head}<tbody><tr><td colspan='4'>No data available</td></tr></tbody></table>"
    body_rows = []
    for r in failure_rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(r.get('Method') or '')}</td>"
            f"<td>{html.escape(r.get('Name') or '')}</td>"
            f"<td>{html.escape(r.get('Error') or '')}</td>"
            f"<td>{_safe_int(r.get('Occurrences'))}</td>"
            "</tr>"
        )
    return f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>"


def _kv_table(d: Dict[str, Any]) -> str:
    if not d:
        return "<p class='note'>No data</p>"
    rows = "".join(
        f"<tr><td><strong>{html.escape(str(k))}</strong></td><td>{html.escape(str(v))}</td></tr>"
        for k, v in d.items()
    )
    return f"<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table>"


# --------------------------------------------------------------------------- #
# CSS / JS templates
# --------------------------------------------------------------------------- #

_CSS = """
:root {
  --primary: #2563eb;
  --primary-dark: #123c69;
  --good: #10b981;
  --warn: #f97316;
  --bad: #dc2626;
  --bg: #f5f7fb;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --text: #1f2937;
  --muted: #6b7280;
}
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif; margin: 0; background: var(--bg); color: var(--text); }
header { background: linear-gradient(135deg, var(--primary-dark), var(--primary)); color: white; padding: 28px 36px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
header h1 { margin: 0; font-size: 28px; letter-spacing: -0.5px; }
.subtitle { margin-top: 8px; opacity: 0.92; font-size: 14px; }
main { padding: 24px 36px; max-width: 1400px; margin: 0 auto; }
section { background: var(--card-bg); border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
h2 { margin: 0 0 16px 0; color: var(--primary-dark); border-bottom: 2px solid var(--border); padding-bottom: 10px; font-size: 20px; }
h3 { color: var(--text); margin: 16px 0 8px 0; font-size: 16px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.card { background: #eef4ff; border-left: 5px solid var(--primary); padding: 14px; border-radius: 8px; transition: transform .15s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.card.warn { background: #fff7ed; border-left-color: var(--warn); }
.card.bad  { background: #fef2f2; border-left-color: var(--bad); }
.card.good { background: #ecfdf5; border-left-color: var(--good); }
.card .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.card .metric { font-size: 24px; font-weight: 700; margin-top: 4px; color: var(--text); }
table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
th, td { border: 1px solid var(--border); padding: 9px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; font-weight: 600; color: var(--text); }
tr:nth-child(even) td { background: #fafbfd; }
ul { line-height: 1.7; padding-left: 20px; }
.bar-row { margin: 12px 0; }
.bar-label { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; }
.bar-bg { background: var(--border); border-radius: 999px; overflow: hidden; height: 18px; }
.bar { height: 18px; background: var(--primary); transition: width .4s; }
.bar.sla { background: var(--good); }
.bar.p95 { background: var(--warn); }
.bar.p99 { background: var(--bad); }
.note { color: var(--muted); font-size: 13px; margin: 6px 0; }
.chart-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
.chart-grid.two { grid-template-columns: 1fr 1fr; }
@media (max-width: 900px) { .chart-grid.two { grid-template-columns: 1fr; } }
.chart-card { border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; background: #fff; }
.chart-card .chart { width: 100%; height: 320px; }
.badge { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
.badge.pass { background: #dcfce7; color: #166534; }
.badge.fail { background: #fee2e2; color: #991b1b; }
.badge.warn { background: #ffedd5; color: #9a3412; }
.meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.meta-block { border: 1px solid var(--border); border-radius: 10px; padding: 14px; background: #fafbfd; }
.meta-block h3 { margin-top: 0; color: var(--primary-dark); }
details { margin-top: 12px; }
summary { cursor: pointer; font-weight: 600; color: var(--primary); padding: 6px 0; }
pre { background: #1f2937; color: #f3f4f6; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 12px; line-height: 1.5; }
footer { text-align: center; color: var(--muted); padding: 20px; font-size: 12px; }
.kv-inline { display: inline-block; margin-right: 16px; }
.kv-inline strong { color: #fef3c7; }
code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
"""


def _build_charts_js(chart_data: Dict[str, Any], sla_seconds: float) -> str:
    """Inline ECharts JS that builds 5 interactive charts."""
    data_json = json.dumps(chart_data)
    sla_ms = sla_seconds * 1000
    return f"""
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script>
(function() {{
  var DATA = {data_json};
  var SLA_MS = {sla_ms};

  var commonGrid = {{ left: 60, right: 30, top: 50, bottom: 70 }};
  var lineSmooth = {{ smooth: true, showSymbol: false }};

  function makeTimeChart(elId, title, series) {{
    var dom = document.getElementById(elId);
    if (!dom) return;
    var chart = echarts.init(dom, null, {{ renderer: 'canvas' }});
    chart.setOption({{
      title: {{ text: title, left: 'center', textStyle: {{ fontSize: 14, fontWeight: 600 }} }},
      tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }} }},
      legend: {{ top: 26 }},
      grid: commonGrid,
      xAxis: {{ type: 'time', boundaryGap: false }},
      yAxis: {{ type: 'value', boundaryGap: [0, '5%'] }},
      dataZoom: [
        {{ type: 'inside', start: 0, end: 100 }},
        {{ type: 'slider', start: 0, end: 100, height: 18, bottom: 8 }}
      ],
      toolbox: {{
        right: 20,
        feature: {{
          dataZoom: {{ yAxisIndex: 'none' }},
          restore: {{}},
          saveAsImage: {{ name: title.replace(/\\s+/g, '_').toLowerCase() }}
        }}
      }},
      series: series
    }});
    window.addEventListener('resize', function() {{ chart.resize(); }});
    return chart;
  }}

  function pairs(times, values) {{
    var out = [];
    for (var i = 0; i < times.length; i++) out.push([times[i], values[i]]);
    return out;
  }}

  // Chart 1: RPS + Failures/s
  makeTimeChart('chart-rps', 'Total Requests per Second', [
    Object.assign({{
      name: 'Requests/s', type: 'line',
      data: pairs(DATA.timestamps, DATA.rps),
      itemStyle: {{ color: '#00ca5a' }},
      areaStyle: {{ opacity: 0.18 }}
    }}, lineSmooth),
    Object.assign({{
      name: 'Failures/s', type: 'line',
      data: pairs(DATA.timestamps, DATA.failuresPerSec),
      itemStyle: {{ color: '#ff6d6d' }}
    }}, lineSmooth)
  ]);

  // Chart 2: Response time percentiles
  makeTimeChart('chart-resp', 'Response Times (ms)', [
    Object.assign({{ name: 'Average', type: 'line',
      data: pairs(DATA.timestamps, DATA.avgMs),
      itemStyle: {{ color: '#2563eb' }} }}, lineSmooth),
    Object.assign({{ name: 'Median', type: 'line',
      data: pairs(DATA.timestamps, DATA.medianMs),
      itemStyle: {{ color: '#10b981' }} }}, lineSmooth),
    Object.assign({{ name: 'P90', type: 'line',
      data: pairs(DATA.timestamps, DATA.p90),
      itemStyle: {{ color: '#eab308' }} }}, lineSmooth),
    Object.assign({{ name: 'P95', type: 'line',
      data: pairs(DATA.timestamps, DATA.p95),
      itemStyle: {{ color: '#f97316' }} }}, lineSmooth),
    Object.assign({{ name: 'P99', type: 'line',
      data: pairs(DATA.timestamps, DATA.p99),
      itemStyle: {{ color: '#dc2626' }},
      markLine: {{ symbol: 'none', data: [{{ yAxis: SLA_MS, name: 'SLA',
        lineStyle: {{ color: '#dc2626', type: 'dashed' }},
        label: {{ formatter: 'SLA: ' + SLA_MS + 'ms', position: 'insideEndTop' }} }}] }}
    }}, lineSmooth)
  ]);

  // Chart 3: Users
  makeTimeChart('chart-users', 'Number of Users', [
    {{ name: 'Users', type: 'line', step: 'end', showSymbol: false,
      data: pairs(DATA.timestamps, DATA.users),
      itemStyle: {{ color: '#7c3aed' }}, areaStyle: {{ opacity: 0.22 }} }}
  ]);

  // Chart 4: Per-endpoint comparison (avg vs p95) -- horizontal bar
  if (DATA.endpoints && DATA.endpoints.names.length) {{
    var dom = document.getElementById('chart-endpoints');
    if (dom) {{
      var c = echarts.init(dom);
      c.setOption({{
        title: {{ text: 'Endpoint Comparison (Avg vs P95)', left: 'center',
          textStyle: {{ fontSize: 14, fontWeight: 600 }} }},
        tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
        legend: {{ top: 26 }},
        grid: {{ left: 140, right: 40, top: 60, bottom: 40 }},
        xAxis: {{ type: 'value', name: 'ms' }},
        yAxis: {{ type: 'category', data: DATA.endpoints.names }},
        series: [
          {{ name: 'Average (ms)', type: 'bar', data: DATA.endpoints.avg,
            itemStyle: {{ color: '#2563eb' }} }},
          {{ name: 'P95 (ms)', type: 'bar', data: DATA.endpoints.p95,
            itemStyle: {{ color: '#f97316' }},
            markLine: {{ symbol: 'none',
              data: [{{ xAxis: SLA_MS, name: 'SLA',
                lineStyle: {{ color: '#dc2626', type: 'dashed' }},
                label: {{ formatter: 'SLA' }} }}] }} }}
        ],
        toolbox: {{ right: 20, feature: {{ saveAsImage: {{ name: 'endpoint_comparison' }} }} }}
      }});
      window.addEventListener('resize', function() {{ c.resize(); }});
    }}
  }}

  // Chart 5: Pass/Fail donut
  var pf = DATA.passFail || {{ pass: 0, fail: 0 }};
  if ((pf.pass + pf.fail) > 0) {{
    var dom2 = document.getElementById('chart-passfail');
    if (dom2) {{
      var c2 = echarts.init(dom2);
      c2.setOption({{
        title: {{ text: 'Success vs Failure', left: 'center',
          textStyle: {{ fontSize: 14, fontWeight: 600 }} }},
        tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}} ({{d}}%)' }},
        legend: {{ bottom: 0 }},
        series: [{{
          type: 'pie', radius: ['45%', '70%'], center: ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {{ borderRadius: 6, borderColor: '#fff', borderWidth: 2 }},
          label: {{ show: true, formatter: '{{b}}\\n{{d}}%' }},
          data: [
            {{ name: 'Success', value: pf.pass, itemStyle: {{ color: '#10b981' }} }},
            {{ name: 'Failure', value: pf.fail, itemStyle: {{ color: '#dc2626' }} }}
          ]
        }}]
      }});
      window.addEventListener('resize', function() {{ c2.resize(); }});
    }}
  }}
}})();
</script>
"""


def _verdict(fail_pct: float, avg_s: float, p95_s: float, sla_s: float) -> Tuple[str, str]:
    if fail_pct > 1.0:
        return ("FAIL", "fail")
    if avg_s > sla_s or p95_s > sla_s * 1.5:
        return ("AT RISK", "warn")
    return ("PASS", "pass")


def _bar_pct(value_s: float, max_s: float) -> float:
    if max_s <= 0:
        return 0.0
    return min(100.0, value_s / max_s * 100.0)


# --------------------------------------------------------------------------- #
# Main HTML builder
# --------------------------------------------------------------------------- #

def build_html(
    csv_base: str,
    test_parameters: Optional[Dict[str, Any]] = None,
    monitoring_data: Optional[Dict[str, Any]] = None,
    sla_seconds: float = 1.0,
    objective: Optional[str] = None,
    service_name: Optional[str] = None,
    azure_devops_url: Optional[str] = None,
) -> str:
    base = Path(csv_base)
    stats_rows = _read_csv(base.with_name(base.name + "_stats.csv"))
    history_rows = _read_csv(base.with_name(base.name + "_stats_history.csv"))
    failure_rows = _read_csv(base.with_name(base.name + "_failures.csv"))
    exception_rows = _read_csv(base.with_name(base.name + "_exceptions.csv"))
    metadata, raw_metadata = _parse_metadata(base.with_name(base.name + "_metadata.txt"))

    test_parameters = dict(test_parameters or {})
    monitoring_data = dict(monitoring_data or {})
    meta_params = metadata.get("Test Parameters", {})
    meta_sysmon = metadata.get("System Monitoring", {})
    meta_cli = metadata.get("Command Line Arguments", {})

    for k, v in meta_params.items():
        test_parameters.setdefault(k, v)
    for k, v in meta_sysmon.items():
        monitoring_data.setdefault(k, v)

    agg = _aggregated_row(stats_rows) or {}
    total_req = _safe_int(agg.get("Request Count"))
    total_fail = _safe_int(agg.get("Failure Count"))
    avg_ms = _safe_float(agg.get("Average Response Time"))
    median_ms = _safe_float(agg.get("Median Response Time"))
    p90_ms = _safe_float(agg.get("90%"))
    p95_ms = _safe_float(agg.get("95%"))
    p99_ms = _safe_float(agg.get("99%"))
    rps_avg = _safe_float(agg.get("Requests/s"))
    rps_max = _max_rps_from_history(history_rows) or rps_avg
    fail_pct = (total_fail / total_req * 100) if total_req else 0.0

    avg_s = avg_ms / 1000
    p95_s = p95_ms / 1000
    p99_s = p99_ms / 1000

    target_rps = _safe_float(test_parameters.get("target_rps"))
    users = _safe_int(test_parameters.get("users") or meta_cli.get("users (-u)"))
    spawn_rate = test_parameters.get("spawn_rate") or meta_cli.get("spawn_rate (-r)") or "N/A"
    run_time = test_parameters.get("run_time") or meta_cli.get("run_time (-t)") or "N/A"
    env_label = test_parameters.get("env", "N/A")
    file_label = test_parameters.get("file") or test_parameters.get("folder") or "N/A"
    timestamp = test_parameters.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    verdict_text, verdict_cls = _verdict(fail_pct, avg_s, p95_s, sla_seconds)
    avg_card_cls = "good" if avg_s <= sla_seconds else ("warn" if avg_s <= sla_seconds * 1.5 else "bad")
    fail_card_cls = "good" if fail_pct == 0 else ("warn" if fail_pct < 1 else "bad")

    # APDEX (industry standard satisfaction score)
    agg_curve = _percentile_curve(agg)
    apdex_score, apdex_rating, apdex_cls = _apdex(agg_curve, sla_seconds, fail_pct)

    bar_max_s = max(sla_seconds, p99_s) * 1.05

    objective_text = objective or (
        f"Evaluate the performance of {html.escape(service_name)} ({html.escape(file_label)})"
        if service_name else f"Evaluate the performance of {html.escape(file_label)}"
    )

    azure_link_html = (
        f'<a href="{html.escape(azure_devops_url)}" target="_blank">{html.escape(azure_devops_url)}</a>'
        if azure_devops_url else "Azure DevOps link not available in this run."
    )

    observations = []
    if total_fail == 0:
        observations.append("No errors were observed during the test.")
    else:
        observations.append(f"<strong>{total_fail}</strong> failures observed ({fail_pct:.2f}%).")
    observations.append(
        f"Overall average response time is <strong>{avg_s:.2f} sec</strong>, "
        f"compared with SLA of <strong>{sla_seconds:.2f} sec</strong>."
    )
    observations.append(
        f"Median response time is {median_ms / 1000:.2f} sec; "
        f"P95 is {p95_s:.2f} sec; P99 is {p99_s:.2f} sec."
    )
    observations.append(
        f"Achieved cumulative RPS is approximately {rps_avg:.2f}; "
        f"maximum observed RPS is approximately {rps_max:.2f}."
    )
    if monitoring_data:
        cpu = monitoring_data.get("cpu_avg_percent", "N/A")
        mem = monitoring_data.get("memory_delta_gb", "N/A")
        net_sent = monitoring_data.get("network_sent_mb", "N/A")
        net_recv = monitoring_data.get("network_recv_mb", "N/A")
        observations.append(
            f"Load generator CPU avg {cpu}%, memory delta {mem} GB, "
            f"network sent {net_sent} MB / recv {net_recv} MB."
        )

    chart_data = _build_chart_data(history_rows, stats_rows)

    test_config_items = [
        ("File / Folder", file_label),
        ("Environment", env_label),
        ("Test Type", test_parameters.get("test_type", "N/A")),
        ("Users (-u)", users),
        ("Spawn Rate (-r)", spawn_rate),
        ("Run Time (-t)", run_time),
        ("Target RPS", target_rps if target_rps else "N/A"),
        ("Run Once", test_parameters.get("run_once", "N/A")),
        ("Timestamp", timestamp),
    ]

    meta_blocks_html = ""
    if meta_params:
        meta_blocks_html += f"<div class='meta-block'><h3>Test Parameters</h3>{_kv_table(meta_params)}</div>"
    if meta_sysmon:
        meta_blocks_html += f"<div class='meta-block'><h3>System Monitoring</h3>{_kv_table(meta_sysmon)}</div>"
    if meta_cli:
        meta_blocks_html += f"<div class='meta-block'><h3>Command Line Arguments</h3>{_kv_table(meta_cli)}</div>"
    if not meta_blocks_html:
        meta_blocks_html = "<p class='note'>No metadata file (_metadata.txt) found alongside CSV artifacts.</p>"

    endpoint_chart_html = ""
    if chart_data["endpoints"]["names"]:
        endpoint_chart_html = "<div class='chart-card'><div id='chart-endpoints' class='chart'></div></div>"

    passfail_chart_html = ""
    if (chart_data["passFail"]["pass"] + chart_data["passFail"]["fail"]) > 0:
        passfail_chart_html = "<div class='chart-card'><div id='chart-passfail' class='chart'></div></div>"

    raw_metadata_html = ""
    if raw_metadata:
        raw_metadata_html = (
            f"<details><summary>View raw metadata file</summary>"
            f"<pre>{html.escape(raw_metadata)}</pre></details>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Performance Executive Summary{f' - {html.escape(service_name)}' if service_name else ''}</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>Performance Executive Summary</h1>
  <div class="subtitle">
    <span class="kv-inline"><strong>Generated:</strong> {html.escape(timestamp)}</span>
    {f'<span class="kv-inline"><strong>Service:</strong> {html.escape(service_name)}</span>' if service_name else ''}
    {f'<span class="kv-inline"><strong>Env:</strong> {html.escape(str(env_label))}</span>' if env_label != 'N/A' else ''}
    <span class="kv-inline"><strong>Verdict:</strong> <span class="badge {verdict_cls}">{verdict_text}</span></span>
  </div>
</header>
<main>

<section>
  <h2>Objective</h2>
  <p>{objective_text}</p>
</section>

<section>
  <h2>Executive Summary</h2>
  <p>Performed a performance test with <strong>{users} users</strong> over a configured runtime of <strong>{html.escape(str(run_time))}</strong>.</p>
  <ul>
    <li><strong>Test Timestamp:</strong> {html.escape(timestamp)}</li>
    <li><strong>Overall response time:</strong> {avg_s:.2f} sec; this is <strong>{'within' if avg_s <= sla_seconds else 'above'} SLA</strong> of {sla_seconds:.2f} sec.</li>
    <li><strong>Maximum RPS achieved:</strong> approximately {rps_max:.2f}.</li>
    <li><strong>Cumulative/Average RPS achieved:</strong> approximately {rps_avg:.2f}.</li>
    <li><strong>Error rate:</strong> approximately {fail_pct:.2f}%.</li>
    <li><strong>Azure DevOps raw results:</strong> {azure_link_html}</li>
  </ul>
</section>

<section>
  <h2>Key Observations</h2>
  <ul>{''.join(f'<li>{o}</li>' for o in observations)}</ul>
</section>

<section>
  <h2>At-a-Glance Metrics</h2>
  <div class="cards">
    <div class="card {apdex_cls}"><div class="label">APDEX (T={sla_seconds:.1f}s)</div><div class="metric">{apdex_score:.2f}</div><div class="note" style="margin:0">{apdex_rating}</div></div>
    <div class="card"><div class="label">Total Requests</div><div class="metric">{total_req}</div></div>
    <div class="card {fail_card_cls}"><div class="label">Failure Rate</div><div class="metric">{fail_pct:.2f}%</div></div>
    <div class="card {avg_card_cls}"><div class="label">Avg Response</div><div class="metric">{avg_s:.2f}s</div></div>
    <div class="card"><div class="label">Median</div><div class="metric">{median_ms / 1000:.2f}s</div></div>
    <div class="card"><div class="label">P90</div><div class="metric">{p90_ms / 1000:.2f}s</div></div>
    <div class="card"><div class="label">P95</div><div class="metric">{p95_s:.2f}s</div></div>
    <div class="card"><div class="label">P99</div><div class="metric">{p99_s:.2f}s</div></div>
    <div class="card"><div class="label">Avg RPS</div><div class="metric">{rps_avg:.2f}</div></div>
    <div class="card"><div class="label">Max RPS</div><div class="metric">{rps_max:.2f}</div></div>
    <div class="card"><div class="label">Target RPS</div><div class="metric">{target_rps if target_rps else 'N/A'}</div></div>
  </div>
</section>

<section>
  <h2>Charts</h2>
  <p class="note">Interactive charts powered by Apache ECharts &mdash; hover for tooltips, drag the slider to zoom, click legend to toggle series, use the toolbox to download as PNG.</p>
  <div class="chart-grid">
    <div class="chart-card"><div id="chart-rps" class="chart"></div></div>
    <div class="chart-card"><div id="chart-resp" class="chart"></div></div>
    <div class="chart-card"><div id="chart-users" class="chart"></div></div>
    <div class="chart-card"><div id="chart-percentile" class="chart" style="height:380px"></div></div>
    <div class="chart-card"><div id="chart-slowest" class="chart" style="height:380px"></div></div>
  </div>
  <div class="chart-grid two" style="margin-top:16px;">
    <div class="chart-card"><div id="chart-errors" class="chart"></div></div>
    {endpoint_chart_html}
    {passfail_chart_html}
  </div>

  <h3>Response Time vs SLA</h3>
  <div class="bar-row"><div class="bar-label"><span>SLA</span><span>{sla_seconds:.2f} sec</span></div>
    <div class="bar-bg"><div class="bar sla" style="width:{_bar_pct(sla_seconds, bar_max_s):.1f}%"></div></div></div>
  <div class="bar-row"><div class="bar-label"><span>Average</span><span>{avg_s:.2f} sec</span></div>
    <div class="bar-bg"><div class="bar" style="width:{_bar_pct(avg_s, bar_max_s):.1f}%"></div></div></div>
  <div class="bar-row"><div class="bar-label"><span>P95</span><span>{p95_s:.2f} sec</span></div>
    <div class="bar-bg"><div class="bar p95" style="width:{_bar_pct(p95_s, bar_max_s):.1f}%"></div></div></div>
  <div class="bar-row"><div class="bar-label"><span>P99</span><span>{p99_s:.2f} sec</span></div>
    <div class="bar-bg"><div class="bar p99" style="width:{_bar_pct(p99_s, bar_max_s):.1f}%"></div></div></div>
</section>

<section>
  <h2>Request Statistics</h2>
  {_request_stats_table(stats_rows)}
</section>

<section>
  <h2>Response Time Statistics</h2>
  {_response_time_table(stats_rows)}
</section>

<section>
  <h2>Failures</h2>
  {_failures_table(failure_rows)}
  {('<h3>Exceptions</h3>' + _failures_table(exception_rows)) if exception_rows else ''}
</section>

<section>
  <h2>Run Metadata</h2>
  <p class="note">Captured from <code>{html.escape(base.name)}_metadata.txt</code> at the end of the Locust run.</p>
  <div class="meta-grid">{meta_blocks_html}</div>
  {raw_metadata_html}
</section>

<section>
  <h2>Test Configuration (effective)</h2>
  <ul>
    {''.join(f'<li><strong>{html.escape(k)}:</strong> {html.escape(str(v))}</li>' for k, v in test_config_items)}
  </ul>
  <p class="note">The standard Locust HTML report (<code>{html.escape(base.name)}.html</code>) is generated alongside this summary.</p>
</section>

<footer>
  Generated by perf_summary_reporter &middot; Charts: Apache ECharts &middot; SLA: {sla_seconds:.2f}s
</footer>
</main>
{_build_charts_js(chart_data, sla_seconds)}
</body>
</html>"""


def generate_executive_summary(
    csv_base: str,
    test_parameters: Optional[Dict[str, Any]] = None,
    monitoring_data: Optional[Dict[str, Any]] = None,
    sla_seconds: float = 1.0,
    objective: Optional[str] = None,
    service_name: Optional[str] = None,
    azure_devops_url: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    html_content = build_html(
        csv_base=csv_base,
        test_parameters=test_parameters,
        monitoring_data=monitoring_data,
        sla_seconds=sla_seconds,
        objective=objective,
        service_name=service_name,
        azure_devops_url=azure_devops_url,
    )
    if output_path is None:
        output_path = f"{csv_base}_executive_summary.html"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")
    return str(out.resolve())


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Performance Executive Summary HTML from Locust artifacts.")
    parser.add_argument("--csv-base", required=True, help="Locust --csv prefix, e.g. reports/performance_report")
    parser.add_argument("--sla", type=float, default=1.0, help="SLA threshold in seconds (default: 1.0)")
    parser.add_argument("--service-name", default=None)
    parser.add_argument("--objective", default=None)
    parser.add_argument("--azure-devops-url", default=None)
    parser.add_argument("--output", default=None, help="Output HTML path (default: <csv-base>_executive_summary.html)")
    args = parser.parse_args(argv)

    out = generate_executive_summary(
        csv_base=args.csv_base,
        sla_seconds=args.sla,
        service_name=args.service_name,
        objective=args.objective,
        azure_devops_url=args.azure_devops_url,
        output_path=args.output,
    )
    print(f"Executive summary written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
