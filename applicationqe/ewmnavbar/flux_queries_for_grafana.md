# Flux Queries for test_behaviors Measurement - Grafana

## 1. Behavior Pass Rate Over Time
Track pass rate trends for each behavior across builds.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> group(columns: ["behavior_name", "auth_type"])
  |> sort(columns: ["_time"], desc: false)
```

**Use case:** Time-series graph to show behavior stability over time

---

## 2. Test Count Per Behavior (Latest Build)
Shows test distribution across behaviors for the most recent build.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "count")
  |> group(columns: ["behavior_name"])
  |> last()
  |> sort(columns: ["_value"], desc: true)
```

**Use case:** Bar chart showing test count per behavior

---

## 3. Behavior Pass/Fail/Broken Status (Latest)
Stacked bar showing pass/fail/broken breakdown per behavior.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field =~ /^(passed|failed|broken)$/)
  |> group(columns: ["behavior_name", "_field"])
  |> last()
  |> pivot(rowKey: ["behavior_name"], columnKey: ["_field"], valueColumn: "_value")
```

**Use case:** Stacked bar chart for test status per behavior

---

## 4. Average Duration Per Behavior (Latest Build)
Identify slowest behaviors.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "avg_duration")
  |> group(columns: ["behavior_name", "auth_type"])
  |> last()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)
```

**Use case:** Bar chart showing top 10 slowest behaviors

---

## 5. Behavior Pass Rate by Authentication Type
Compare pass rates between setup, authenticated, and other auth types.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> group(columns: ["auth_type"])
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
```

**Use case:** Time-series with separate lines for each auth_type

---

## 6. Pass Rate Heatmap (Behavior x Auth Type)
Matrix view of all behaviors and their pass rates.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> group(columns: ["behavior_name", "auth_type"])
  |> last()
  |> pivot(rowKey: ["behavior_name"], columnKey: ["auth_type"], valueColumn: "_value")
```

**Use case:** Heatmap panel showing pass rates for all behavior/auth combinations

---

## 7. Latest Build Behavior Summary (Single Stat)
Show overall pass rate for a specific behavior.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r.behavior_name == "sub-menus - All Clients (authenticated)")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> last()
```

**Use case:** Single stat panel for a specific behavior

---

## 8. Behavior Duration Trend (Min/Avg/Max)
Track performance changes for a behavior over time.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r.behavior_name == "create auth storage (setup)")
  |> filter(fn: (r) => r._field =~ /^(min_duration|avg_duration|max_duration)$/)
  |> group(columns: ["_field"])
```

**Use case:** Time-series with min/avg/max lines for performance monitoring

---

## 9. Behavior Comparison (Selected Builds)
Compare specific behaviors across different builds/environments.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> filter(fn: (r) => r.environment == "test11")
  |> group(columns: ["build_id", "behavior_name"])
  |> last()
```

**Use case:** Compare behavior metrics across multiple builds

---

## 10. Failing Behaviors Alert Query
Get list of behaviors with pass rate below threshold.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> group(columns: ["behavior_name", "auth_type"])
  |> last()
  |> filter(fn: (r) => r._value < 100)
  |> sort(columns: ["_value"], desc: false)
```

**Use case:** Alert query or table panel for failing behaviors

---

## 11. Total Tests Per Behavior (With Trend)
Show test count with day-over-day comparison.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field == "count")
  |> group(columns: ["behavior_name", "auth_type", "_time"])
  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
```

**Use case:** Bar chart with trend line for test distribution

---

## 12. Build Status Dashboard
Summary stats for latest build.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field =~ /^(count|passed|failed|broken)$/)
  |> group(columns: ["_field"])
  |> last()
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**Use case:** Summary table or stats for dashboard

---

## 13. Allure Results Links (test_artifacts2)
Get Allure results URLs with proper formatting for Grafana table links.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_artifacts2")
  |> filter(fn: (r) => r._field == "AllureResults")
  // Flatten group key so Grafana doesn't mark columns as "group"
  |> group(columns: [])
  // Keep only the columns you want to see as table columns
  |> keep(columns: ["_time", "_value", "build_id", "build_reason", "environment"])
  // Rename _value to a friendly column name
  |> rename(columns: {_value: "AllureResults"})
  // Optional: if some values are non-string, force to string
  |> map(fn: (r) => ({ r with AllureResults: string(v: r.AllureResults) }))
```

**Use case:** Table panel with clickable links to Allure results - TESTED & WORKING ✅

---

## 14. Allure Report Links (test_artifacts2)
Get Allure report URLs with proper formatting.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_artifacts2")
  |> filter(fn: (r) => r._field == "AllureReport")
  |> group(columns: [])
  |> keep(columns: ["_time", "_value", "build_id", "build_reason", "environment"])
  |> rename(columns: {_value: "AllureReport"})
  |> map(fn: (r) => ({ r with AllureReport: string(v: r.AllureReport) }))
```

**Use case:** Table panel with clickable links to Allure HTML reports - TESTED & WORKING ✅

---

## 15. Playwright Report Links (test_artifacts2)
Get Playwright report URLs with screenshots and videos.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_artifacts2")
  |> filter(fn: (r) => r._field == "PlaywrightReport")
  |> group(columns: [])
  |> keep(columns: ["_time", "_value", "build_id", "build_reason", "environment"])
  |> rename(columns: {_value: "PlaywrightReport"})
  |> map(fn: (r) => ({ r with PlaywrightReport: string(v: r.PlaywrightReport) }))
```

**Use case:** Table panel with clickable links to Playwright reports

---

## 16. All Artifacts in Single Query (test_artifacts2)
Get all artifact types in one table view.

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_artifacts2")
  |> filter(fn: (r) => r._field =~ /^(AllureReport|AllureResults|PlaywrightReport|TestResults)$/)
  |> group(columns: [])
  |> keep(columns: ["_time", "_value", "_field", "build_id", "build_reason", "environment"])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**Use case:** Comprehensive table with all artifact links in separate columns

---

## 17. Behavior Metrics with Artifact Links from test_behaviors
Get behavior stats AND artifact URLs (all-in-one from test_behaviors measurement).

```flux
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> filter(fn: (r) => r._field =~ /^(pass_rate|count|passed|failed|AllureReport|AllureResults|PlaywrightReport)$/)
  |> group(columns: [])
  |> keep(columns: ["_time", "_value", "_field", "behavior_name", "auth_type", "build_id"])
  |> pivot(rowKey: ["behavior_name"], columnKey: ["_field"], valueColumn: "_value")
```

**Use case:** Table showing behavior metrics + artifact links together

---

## Tips for Grafana Integration:

1. **For Time-Series Panels**: Use queries 1, 8, 11
2. **For Bar Charts**: Use queries 2, 4
3. **For Heatmaps**: Use query 6
4. **For Status Cards (Single Stat)**: Use query 7
5. **For Tables**: Use queries 10, 12
6. **For Alerts**: Use query 10
7. **For Artifact Links**: Use queries 13, 14, 15, 16, 17 ⭐ **TESTED & WORKING**

## Important Query Patterns:

### Pattern 1: Using Grafana Time Range Variables
Always use `v.timeRangeStart` and `v.timeRangeStop` for dashboard time range support:
```flux
|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
```

### Pattern 2: Flattening Group Keys for Table Display
Use `group(columns: [])` to prevent Grafana from marking columns as "group":
```flux
|> group(columns: [])
```

### Pattern 3: Selecting Columns for Tables
Use `keep()` to only show relevant columns:
```flux
|> keep(columns: ["_time", "_value", "build_id", "build_reason", "environment"])
```

### Pattern 4: Making Values Table-Friendly
Rename fields and convert to strings:
```flux
|> rename(columns: {_value: "AllureResults"})
|> map(fn: (r) => ({ r with AllureResults: string(v: r.AllureResults) }))
```

### Pattern 5: Getting test_artifacts2 (Recommended for Pure Artifacts)
Use `test_artifacts2` measurement for artifact links - cleaner data structure
```flux
|> filter(fn: (r) => r._measurement == "test_artifacts2")
```

### Pattern 6: Getting test_behaviors (For Behavior Metrics + Artifacts)
Use `test_behaviors` measurement when you need both metrics AND artifacts
```flux
|> filter(fn: (r) => r._measurement == "test_behaviors")
```

## Grafana Panel Configuration for Artifacts:

### For Query 13-16 (Artifact Links):
- **Panel Type**: Table
- **Field Options**: Configure as links with "Data links"
- **Link Label**: Use field name (AllureReport, AllureResults, PlaywrightReport)
- **Link URL**: `${AllureResults}` or `${AllureReport}` etc.
- **Open in**: New tab

### Example Data Link Configuration:
```json
{
  "title": "Allure Report",
  "url": "${AllureReport}",
  "targetBlank": true
}
```

---

```flux
# Behavior Name Variable (for dropdowns)
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> group(columns: ["behavior_name"])
  |> distinct(column: "behavior_name")

# Auth Type Variable
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> group(columns: ["auth_type"])
  |> distinct(column: "auth_type")

# Build ID Variable
from(bucket: "AutomationData")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "test_behaviors")
  |> group(columns: ["build_id"])
  |> distinct(column: "build_id")
```

---

## Field Reference:
- **Tags**: build_id, environment, build_reason, behavior_name, auth_type
- **Fields**: 
  - **Metrics**: count, passed, failed, broken, skipped, pass_rate, total_duration, avg_duration, max_duration, min_duration
  - **Artifact URLs**: PlaywrightReport, AllureReport, AllureResults, TestResults
  
### Artifact URL Fields Details:
- **AllureReport**: Allure HTML report with full test execution details
- **AllureResults**: Raw Allure results data package
- **PlaywrightReport**: Playwright test report with screenshots and videos
- **TestResults**: Generic test results artifact
