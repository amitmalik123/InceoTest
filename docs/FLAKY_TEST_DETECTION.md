# Flaky Test Detection - Grafana Dashboard Queries

This document provides Flux queries for visualizing flaky test data in Grafana.

## Dashboard Panels

### 1. Flaky Test Count Over Time

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_count")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> yield(name: "flaky_count")
```

**Panel Type:** Time series graph
**Description:** Shows trend of flaky tests detected over time

---

### 2. Flaky Rate Percentage

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_rate")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "flaky_rate")
```

**Panel Type:** Gauge or Time series
**Description:** Percentage of tests that are flaky
**Thresholds:** Green (< 5%), Yellow (5-10%), Red (> 10%)

---

### 3. Top 10 Flaky Tests

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> filter(fn: (r) => r["_field"] == "failed_attempts")
  |> group(columns: ["test_name"])
  |> sum()
  |> group()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)
  |> yield(name: "top_flaky_tests")
```

**Panel Type:** Bar chart or Table
**Description:** Tests with most failures before passing

---

### 4. Flaky Test Success Rate

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> filter(fn: (r) => r["_field"] == "flaky_rate")
  |> group(columns: ["test_name"])
  |> mean()
  |> map(fn: (r) => ({ r with _value: 100.0 - r._value }))
  |> sort(columns: ["_value"])
  |> yield(name: "success_rate")
```

**Panel Type:** Table
**Description:** Success rate for each flaky test (100 - flaky_rate)

---

### 5. Retry Distribution

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> filter(fn: (r) => r["_field"] == "total_attempts")
  |> group(columns: ["_value"])
  |> count()
  |> yield(name: "retry_distribution")
```

**Panel Type:** Pie chart
**Description:** Distribution of test attempts (1, 2, 3 attempts)

---

### 6. Flaky Tests by Environment

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_count")
  |> group(columns: ["environment"])
  |> sum()
  |> yield(name: "flaky_by_env")
```

**Panel Type:** Bar chart
**Description:** Compare flaky test counts across environments

---

### 7. Recent Flaky Tests (Last 24 Hours)

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> filter(fn: (r) => r["_field"] == "failed_attempts" or r["_field"] == "total_attempts")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({ r with success_rate: float(v: r.total_attempts - r.failed_attempts) / float(v: r.total_attempts) * 100.0 }))
  |> keep(columns: ["_time", "test_name", "environment", "failed_attempts", "total_attempts", "success_rate", "error_message"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 20)
  |> yield(name: "recent_flaky")
```

**Panel Type:** Table
**Columns:** Time, Test Name, Environment, Failed Attempts, Total Attempts, Success Rate, Error Message
**Description:** Most recent flaky test occurrences with details

---

### 8. Flaky Test Trend (7-Day Moving Average)

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_rate")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> movingAverage(n: 7)
  |> yield(name: "7day_ma")
```

**Panel Type:** Time series
**Description:** 7-day moving average of flaky test rate

---

### 9. Flaky Tests Impact (Duration)

**Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> filter(fn: (r) => r["_field"] == "duration_ms")
  |> group(columns: ["test_name"])
  |> sum()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)
  |> yield(name: "flaky_duration")
```

**Panel Type:** Bar chart
**Description:** Total time wasted by flaky tests (sum of all attempts)

---

### 10. Flaky Test Alert Query

**Alert Query:**
```flux
from(bucket: "AutomationData")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_rate")
  |> mean()
  |> yield(name: "mean_flaky_rate")
```

**Alert Condition:** `mean_flaky_rate > 10`
**Alert Message:** "⚠️ High flaky test rate detected: ${mean_flaky_rate}%. Investigate unstable tests."

---

## Dashboard Variables

Create these variables for filtering:

1. **environment**
   ```flux
   from(bucket: "AutomationData")
     |> range(start: -30d)
     |> filter(fn: (r) => r["_measurement"] == "test_quality")
     |> keep(columns: ["environment"])
     |> distinct(column: "environment")
   ```

2. **test_name** (for drill-down)
   ```flux
   from(bucket: "AutomationData")
     |> range(start: -7d)
     |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
     |> keep(columns: ["test_name"])
     |> distinct(column: "test_name")
   ```

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Flaky Test Detection Dashboard                        │
├──────────────┬──────────────┬──────────────────────────┤
│ Flaky Count  │  Flaky Rate  │  Total Tests Affected   │
│   (Stat)     │   (Gauge)    │      (Stat)             │
├──────────────┴──────────────┴──────────────────────────┤
│  Flaky Test Count Over Time                            │
│  (Time Series - 30 days)                               │
├────────────────────────────────────────────────────────┤
│  Top 10 Flaky Tests          │  Retry Distribution    │
│  (Bar Chart)                 │  (Pie Chart)           │
├──────────────────────────────┼────────────────────────┤
│  Flaky Tests by Environment  │  7-Day Trend          │
│  (Bar Chart)                 │  (Time Series)        │
├──────────────────────────────┴────────────────────────┤
│  Recent Flaky Tests (Last 24 Hours)                   │
│  (Table with error messages)                          │
└────────────────────────────────────────────────────────┘
```

---

## Alerting Rules

1. **Critical: High Flaky Rate**
   - Condition: Flaky rate > 15% in last hour
   - Severity: Critical
   - Action: Slack notification + email

2. **Warning: Increasing Flaky Trend**
   - Condition: 7-day MA increasing by > 5% week-over-week
   - Severity: Warning
   - Action: Slack notification

3. **Info: New Flaky Test Detected**
   - Condition: New test_name appears in flaky_tests measurement
   - Severity: Info
   - Action: Slack notification

---

## Usage

1. Import dashboard JSON to Grafana
2. Configure InfluxDB data source
3. Set up alert notifications (Slack, email, etc.)
4. Customize time ranges and thresholds as needed

---

## Example: Full Dashboard JSON

See `grafana_flaky_dashboard.json` for complete dashboard configuration.
