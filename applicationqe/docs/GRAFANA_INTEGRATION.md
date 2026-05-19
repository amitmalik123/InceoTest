# Grafana Integration (applicationqe)

This framework publishes UI automation summary metrics to InfluxDB, which can be visualized in Grafana.

## Data Flow

1. `pytest` writes Allure and JUnit outputs.
2. Azure pipeline step `Push Metrics to InfluxDB` runs `utils/influx_reporter.py`.
3. Reporter parses Allure (preferred) or JUnit (fallback).
4. Reporter writes one summary point to InfluxDB measurement `ui_test_summary`.
5. Grafana dashboards query `ui_test_summary` using tags for filtering.

## Required InfluxDB Variables

- `INFLUXDB_URL`
- `INFLUXDB_TOKEN`
- `INFLUXDB_ORG`
- `INFLUXDB_BUCKET`

## Measurement Schema

Measurement: `ui_test_summary`

Tags:
- `suite`
- `environment`
- `team`
- `stage`
- `build_id`
- `build_reason`
- `branch`
- `host`
- `source` (`allure` or `junit`)

Fields:
- `total`
- `passed`
- `failed`
- `errors`
- `skipped`
- `unknown`
- `duration_seconds`
- `pass_rate`

## Example Flux Queries

Pass rate trend:

```flux
from(bucket: "AutomationData")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "ui_test_summary")
  |> filter(fn: (r) => r._field == "pass_rate")
  |> filter(fn: (r) => r.team == "Model Management")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
```

Failure count by suite:

```flux
from(bucket: "AutomationData")
  |> range(start: -14d)
  |> filter(fn: (r) => r._measurement == "ui_test_summary")
  |> filter(fn: (r) => r._field == "failed")
  |> group(columns: ["suite"])
  |> sum()
```

Latest run health:

```flux
from(bucket: "AutomationData")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "ui_test_summary")
  |> filter(fn: (r) => r._field == "pass_rate" or r._field == "total" or r._field == "failed")
  |> last()
```

## Local Dry Run

From `applicationqe`:

```bash
python utils/influx_reporter.py --allure-dir reports/allure --junit reports/junit.xml --dry-run
```

This validates parsing logic without pushing to InfluxDB.
