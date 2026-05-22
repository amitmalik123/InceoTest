# Performance Testing with Locust

This guide explains how to run performance tests using Locust with the provided automation framework. You can configure test runs using either CLI arguments or environment variables.

## Prerequisites
- Python 3.8+
- Locust installed (`pip install locust`)
- All dependencies from `requirements.txt` installed
- InfluxDB client installed (`pip install influxdb-client`) - optional for metrics
- Configured environment files in `config/` directory

## Framework Integration

Locust performance tests are fully integrated with the automation framework:

**Core Framework Components:**
- **Config Loaders** - Environment-specific settings from YAML configs
- **API Clients** - REST, GraphQL, SOAP, gRPC protocol support
- **Validators** - Response validation (status code, schema, fields)
- **InfluxDB Reporter** - Real-time metrics and time-series data
- **Test Helpers** - Modular test execution managers
- **Jinja2 Templating** - Dynamic payload generation

**Benefits:**
- Consistent test execution across pytest and Locust
- Centralized configuration management
- Reusable API clients and validators
- Real-time performance monitoring
- Automatic report organization

## Running Locust

### 1. Using CLI Arguments
You can pass custom arguments directly to the Locust command:

```powershell
locust -f core-api-automation/locustfile.py --folder WorkItemNotification\testcases --test_type Performance
```

- `--folder`: Path to the folder containing test case JSON files
- `--test_type`: Type of test to run (e.g., Performance)
- `--file`: (Optional) Path to a specific test case file

### 2. Using Environment Variables (PowerShell)
Set environment variables before running Locust:

```powershell
$env:LOCUST_FOLDER="WorkItemNotification\testcases"
$env:LOCUST_TEST_TYPE="Performance"
locust -f core-api-automation/locustfile.py
```

You can also set `LOCUST_FILE` for a specific test case file.

### 3. Using .env File
Set variables in `.env`:

```
LOCUST_FOLDER=WorkItemNotification\testcases
LOCUST_TEST_TYPE=Performance
LOCUST_FILE=path/to/testcase.json
ENV_NAME=T12
```

Locust will automatically pick up these values if not provided via CLI or environment.

### 4. Host Configuration
The API base URL (`host`) is set dynamically from the config file corresponding to `ENV_NAME` in `.env` (e.g., `config.TSADEV.yaml`, `config.T12.yaml`).

**Supported environments:**
- `TSADEV` - Development environment
- `T12`, `T11`, `T10` - Test environments
- `aks` - Azure Kubernetes Service

Each config file contains:
- API service endpoints with base URLs
- Authentication settings
- Database connections
- InfluxDB configuration
- Timeout and retry settings

### 5. Example: Set Number of Users, Ramp-up, and Duration
You can control the number of users, ramp-up rate, and test duration using CLI options:

```powershell
locust -f locustfile.py --folder WorkItemNotification/testcases --test_type Performance -u 50 -r 5 -t 10m
```

- `-u` or `--users`: Number of users to simulate (e.g., 50)
- `-r` or `--spawn-rate`: Users spawned per second (e.g., 5)
- `-t` or `--run-time`: Total test duration (e.g., 10m for 10 minutes)

You can combine these with other arguments as needed.


### 6. Example: Generate HTML and CSV Reports
To save Locust reports in the `reports` folder and organize them automatically:

```powershell
locust -f locustfile.py --folder WorkItemNotification/testcases --test_type Performance -u 1 -r 1 -t 10s --headless --html reports/performance_report.html --csv reports/performance_report
```

- `--html reports/performance_report.html`: Generates an HTML report in the `reports` folder.
- `--csv reports/performance_report`: Generates CSV reports (stats, failures, etc.) in the `reports` folder.

After the run, the script automatically moves new performance reports to a timestamped folder under `reports/`, and archives older timestamped folders to `reports/archive/`.

**Example folder structure after multiple runs:**

```
reports/
	20251015_140900/
		performance_report.html
		performance_report_stats.csv
		...
	archive/
		20251014_120000/
		20251013_110000/
```

This keeps your reports organized and prevents clutter.

---

## InfluxDB Integration for Real-Time Monitoring

### Overview
Locust automatically pushes performance metrics to InfluxDB when enabled in the environment configuration. This provides real-time monitoring and historical trend analysis.

### Configuration
Add InfluxDB settings to your environment config (e.g., `config/config.TSADEV.yaml`):

```yaml
db_connections:
  influxdb:
    default:
      url: "http://your-influxdb-server:8086"
      token: "your-influxdb-token"
      org: "your-organization"
      bucket: "your-bucket-name"
      timeout: 10000
      batch_size: 50  # Batch size for optimized writes
      enabled: true
```

### Metrics Pushed to InfluxDB

**1. Request Metrics (`locust_requests`)**
- Response time (ms)
- Response length (bytes)
- Success/failure status
- HTTP status code
- Endpoint path
- HTTP method
- Timestamp

**2. Test Summary (`locust_test_summary`)**
- Total requests
- Total failures
- Average response time
- P50, P95, P99 percentiles
- Requests per second
- Test duration

**3. Endpoint Summary (`locust_endpoint_summary`)**
- Per-endpoint aggregated statistics
- Request counts
- Failure rates
- Response time percentiles

### Metric Tags for Filtering
- `environment` - Test environment (TSADEV, T12, etc.)
- `test_id` - Test case identifier
- `endpoint` - API endpoint path
- `method` - HTTP method (GET, POST, PUT, DELETE)
- `status_code` - HTTP response code
- `request_type` - Request category
- `test_type` - Performance test type

### Batch Writing for Performance
Metrics are buffered and written in batches (default: 50 metrics per batch) to optimize InfluxDB write performance:
- Reduces network overhead
- Improves write throughput
- Configurable batch size via `batch_size` parameter

### Grafana Dashboard Integration

**Add InfluxDB as Data Source:**
1. Go to Grafana → Configuration → Data Sources
2. Add InfluxDB
3. Configure URL, organization, token, and bucket

**Example Flux Queries for Dashboards:**

```flux
// Average response time over time
from(bucket: "your-bucket-name")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "locust_requests")
  |> filter(fn: (r) => r._field == "response_time")
  |> filter(fn: (r) => r.environment == "TSADEV")
  |> aggregateWindow(every: 1m, fn: mean)

// Request success rate
from(bucket: "your-bucket-name")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "locust_requests")
  |> filter(fn: (r) => r._field == "success")
  |> aggregateWindow(every: 1m, fn: mean)
  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))

// Requests per second
from(bucket: "your-bucket-name")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "locust_requests")
  |> aggregateWindow(every: 1m, fn: count)

// P95 response time by endpoint
from(bucket: "your-bucket-name")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "locust_requests")
  |> filter(fn: (r) => r._field == "response_time")
  |> group(columns: ["endpoint"])
  |> aggregateWindow(every: 5m, fn: (tables=<-, column) =>
      tables |> quantile(q: 0.95, column: column))
```

**Recommended Dashboard Panels:**
- Response time trends (average, P95, P99)
- Request throughput (requests/second)
- Success rate percentage
- Error rate by status code
- Per-endpoint performance comparison
- User count over time
- Response size distribution

---

## Azure Log Analytics Performance History

Locust CSV and metadata artifacts can be pushed to Azure Log Analytics as dedicated performance tables. These tables are separate from the functional `TestResults_CL` table so performance runs can keep BlazeMeter-style run history, endpoint history, load-profile comparisons, baseline records, and Grafana dashboards without adding sparse performance columns to functional test rows.

### Tables

The first successful push creates the custom tables automatically. Later pushes append records to the same tables; they do not truncate or recreate them.

| Log-Type | Custom table | Purpose |
| --- | --- | --- |
| `PerfRun` | `PerfRun_CL` | One row per Locust execution/run. |
| `PerfEndpointSummary` | `PerfEndpointSummary_CL` | One row per endpoint/request name per run. |
| `PerfTimeSeries` | `PerfTimeSeries_CL` | In-run trend rows from `performance_report_stats_history.csv`. |
| `PerfFailure` | `PerfFailure_CL` | Locust failures and exceptions. |
| `PerfBaseline` | `PerfBaseline_CL` | Approved baseline records promoted from pipeline runs. |

Custom tables may take 5-15 minutes to appear in Log Analytics after first ingestion.

### Reporter Usage

The performance reporter reads Locust artifacts from the latest timestamped report directory unless a path is supplied.

```bash
python3 framework/reporter/performance_log_analytics_reporter.py \
  --reports-path reports/20260509_120000
```

Dry-run mode prints the JSON records without sending them:

```bash
python3 framework/reporter/performance_log_analytics_reporter.py \
  --reports-path reports/20260509_120000 \
  --dry-run
```

Required environment variables for ingestion:

```bash
LOG_ANALYTICS_WORKSPACE_ID="<workspace-id>"
LOG_ANALYTICS_SHARED_KEY="<workspace-shared-key>"
LOG_ANALYTICS_ENABLED="true"
```

Optional environment variables:

```bash
SERVICE_NAME="models"
ENV_NAME="T12"
PERF_LOAD_PROFILE="1x"
PERF_LOAD_MULTIPLIER="1"
PERF_LOG_ANALYTICS_TIMESERIES_ENABLED="true"
```

The reporter preserves numeric fields as JSON numbers so Log Analytics creates numeric `_d` columns such as `P95ResponseTimeMs_d`, `RequestsPerSecond_d`, and `FailureRate_d`.

### Key Fields

All performance tables include enough shared identity fields for filtering and joins:

- `RunId`, `Environment`, `ServiceName`, `LoadProfile`, `LoadMultiplier`
- `BuildId`, `BuildNumber`, `PipelineId`, `PipelineName`, `SourceBranch`, `CommitSha`
- `Users`, `SpawnRate`, `RunTimeSeconds`, `TargetRps`

Performance metric fields include:

- `TotalRequests`, `TotalFailures`, `FailureRate`, `RequestsPerSecond`
- `AvgResponseTimeMs`, `MinResponseTimeMs`, `MaxResponseTimeMs`
- `P50ResponseTimeMs`, `P90ResponseTimeMs`, `P95ResponseTimeMs`, `P99ResponseTimeMs`

### Azure Pipeline Integration

The standalone pipeline and the shared matrix/callable template both run the performance reporter after Locust when `testType` is `non-functional` or `both`.

Manual baseline promotion is controlled by pipeline parameters:

```yaml
promotePerformanceBaseline: true
baselineReason: 'Stable T12 1x model service run'
```

When promotion is enabled, the current run is written to `PerfBaseline_CL` with `IsActive=true`, `ApprovedBy`, `ApprovedOn`, `BaselineRunId`, and the measured baseline metrics. Log Analytics is append-only, so previous baselines are not updated in place. Queries should select the latest active baseline with `arg_max(TimeGenerated, *) by BaselineId_s`.

Treat each load profile as a separate baseline. For example, compare `1x` runs with `1x` baselines, `2x` runs with `2x` baselines, and `3x` runs with `3x` baselines.

### Grafana Dashboard

Import the dashboard JSON from:

```text
grafana/performance-log-analytics-dashboard.json
```

Replace `${AZURE_MONITOR_DS_UID}` with the Grafana Azure Monitor data source UID. The dashboard expects the Azure Monitor data source to have access to the Log Analytics workspace.

Dashboard variables:

- `environment`
- `service`
- `loadProfile`
- `runId`

Dashboard panels include:

- Latest run status
- Latest run summary
- P95/P99 response-time history
- Throughput history
- 1x/2x/3x comparison
- Endpoint baseline comparison
- In-run response-time trend
- Failures and exceptions

Example KQL for latest active baseline:

```kql
PerfBaseline_CL
| where Environment_s == "$environment"
| where ServiceName_s == "$service"
| where LoadProfile_s == "$loadProfile"
| where IsActive_b == true
| summarize arg_max(TimeGenerated, *) by BaselineId_s
| project BaselineRunId_s, BaselineBuildId_s, BaselineP95Ms_d,
          BaselineP99Ms_d, BaselineRps_d, ApprovedBy_s, ApprovedOn_t, Reason_s
```

Example KQL for current endpoint versus baseline:

```kql
let activeBaselines = PerfBaseline_CL
| where Environment_s == "$environment"
| where ServiceName_s == "$service"
| where LoadProfile_s == "$loadProfile"
| where IsActive_b == true
| summarize arg_max(TimeGenerated, *) by BaselineId_s;
PerfEndpointSummary_CL
| where RunId_s == "$runId"
| join kind=leftouter activeBaselines on BaselineId_s
| extend P95RegressionPercent = iff(BaselineP95Ms_d > 0, ((P95ResponseTimeMs_d - BaselineP95Ms_d) / BaselineP95Ms_d) * 100.0, real(null))
| project Endpoint_s, Method_s, P95ResponseTimeMs_d, BaselineP95Ms_d,
          P95RegressionPercent, RequestsPerSecond_d, BaselineRps_d
```

### App Insights Relationship

Application Insights remains the service-side source of truth for dependencies, exceptions, traces, and server-side request duration. The Log Analytics performance tables are the controlled test-run history: build ID, load profile, Locust-observed latency, endpoint summaries, failures, and baselines.

---

## Response Validation

Locust tests include comprehensive response validation using the framework's validators:

### Validation Levels

**1. Basic Validation (Always Enabled)**
- HTTP status code validation
- Response time tracking
- Success/failure detection

**2. Full Validation (Configurable)**
Enable with `--enable_full_validation` or `LOCUST_ENABLE_FULL_VALIDATION=true`:
- JSON schema validation
- Required field validation
- Field type and format validation
- Custom validation rules from test case
- Database comparison validation

### Validation Configuration in Test Cases

```json
{
  "test_id": "TC_PERF_001",
  "endpoint": "/api/users",
  "method": "GET",
  "expected_status": 200,
  "validate": {
    "performance": {
      "max_response_time_ms": 500
    },
    "required_fields": ["id", "name", "email"],
    "field_types": {
      "id": "string",
      "email": "string",
      "active": "boolean"
    }
  }
}
```

### Running with Validation

```powershell
# With full validation
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --enable_full_validation --headless -u 10 -r 2 -t 60s

# Status code validation only (default)
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --headless -u 10 -r 2 -t 60s
```

---

## Locust Web UI
After starting Locust, open [http://localhost:8089](http://localhost:8089) in your browser to control and monitor the test.

## Example Command Variations

### Basic Execution

#### Run specific test case file
```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV
```

#### Run with folder of test cases
```powershell
locust --folder testdata\WorkItemNotification\testcases --test_type Performance --env TSADEV
```

#### Run with environment variables
```powershell
$env:LOCUST_FOLDER="WorkItemNotification\testcases"; $env:LOCUST_TEST_TYPE="Performance"; $env:ENV_NAME="TSADEV"; locust
```

#### Run with .env file only
```powershell
locust
```

### Headless Mode (Automated Testing)

#### Quick smoke test (10 seconds)
```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --headless -u 5 -r 1 -t 10s
```

#### Standard load test (5 minutes, 50 users)
```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --headless -u 50 -r 5 -t 5m --html "reports\load_test.html" --csv "reports\load_test"
```

#### Stress test (10 minutes, 200 users)
```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --headless -u 200 -r 10 -t 10m --html "reports\stress_test.html"
```

#### Spike test (rapid ramp-up)
```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --headless -u 100 -r 50 -t 2m
```

### With Full Validation

```powershell
locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV --enable_full_validation --headless -u 10 -r 2 -t 60s --html "reports\validated_test.html"
```

### Multiple Test Types

```powershell
# Run only Smoke tests
locust --folder testdata\WorkItemNotification\testcases --test_type Smoke --env TSADEV --headless -u 2 -r 1 -t 30s

# Run Performance tests
locust --folder testdata\parties\testcases --test_type Performance --env T12 --headless -u 50 -r 5 -t 5m
```

## Troubleshooting

### Common Issues

**Unrecognized arguments error:**
- Use environment variables or `.env` file instead of CLI for custom arguments
- Standard Locust parameters (`-u`, `-r`, `-t`, `--headless`) work on CLI

**Configuration not loading:**
- Verify `ENV_NAME` in `.env` matches config file name (e.g., `ENV_NAME=TSADEV` → `config.TSADEV.yaml`)
- Check YAML syntax in config file
- Ensure config file exists in `config/` directory

**Host/base URL issues:**
- Host is set from config file, not CLI
- Verify `api_services.default.base_url` in config YAML
- Check environment variable substitution in config

**InfluxDB not pushing metrics:**
- Verify `db_connections.influxdb.default.enabled: true` in config
- Check InfluxDB server URL and connectivity
- Validate InfluxDB token has write permissions
- Check bucket name exists in InfluxDB
- Look for "[InfluxDB] Integration enabled" message in Locust output
- Verify `influxdb-client` package installed: `pip install influxdb-client`

**InfluxDB connection errors:**
- Test connectivity: `curl http://your-influxdb-server:8086/health`
- Verify firewall rules allow connection to InfluxDB port (default: 8086)
- Check InfluxDB server logs for authentication errors
- Validate token format (should be long base64 string)

**Validation errors:**
- Full validation may slow down load tests - use only for functional validation
- Check test case JSON for correct `validate` structure
- Verify expected fields exist in API response
- Use `--enable_full_validation` flag or env var to enable

**Test cases not loading:**
- Verify `--file` path points to valid JSON test case
- Check `--folder` path contains test case JSON files
- Ensure `test_type` in test case matches `--test_type` filter
- Test case JSON must follow framework schema

**SSL/TLS errors:**
- Set `verify_ssl: false` in config YAML for dev environments
- For production, ensure valid SSL certificates
- Check certificate chain and CA certificates

**Performance issues:**
- Reduce `batch_size` if InfluxDB writes are slow
- Disable full validation for high-load tests
- Check network latency between test runner and target API
- Monitor system resources (CPU, memory, network)

### Debug Mode

Enable detailed logging:
```powershell
$env:LOG_LEVEL="DEBUG"; locust --file testdata\parties\testcases\TestCase_Party_id_GET.json --test_type Performance --env TSADEV
```

### Check InfluxDB Data

Query InfluxDB directly to verify metrics:
```bash
# Using influx CLI
influx query 'from(bucket: "your-bucket") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "locust_requests") |> limit(n: 10)'

# Or using HTTP API
curl -X POST "http://your-influxdb-server:8086/api/v2/query?org=your-org" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/vnd.flux" \
  -d 'from(bucket: "your-bucket") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "locust_requests") |> limit(n: 10)'
```

---

## Best Practices

### Load Test Design
- **Start small**: Begin with 1-5 users to verify functionality
- **Gradual ramp-up**: Use appropriate spawn rate (`-r`) to avoid overwhelming the system
- **Realistic duration**: Run tests long enough to reach steady state (minimum 5-10 minutes)
- **Monitor resources**: Watch CPU, memory, and network on both client and server

### InfluxDB Monitoring
- **Use appropriate batch_size**: 50-100 for most scenarios
- **Set up Grafana dashboards**: Real-time monitoring during tests
- **Tag properly**: Use consistent environment and test_id tags
- **Archive old data**: Set retention policies in InfluxDB

### Validation Strategy
- **Functional tests**: Enable full validation with low user count
- **Load tests**: Use status code validation only for high throughput
- **Baseline tests**: Run validated tests first to ensure correctness

### Report Management
- **Use timestamps**: Reports auto-organize in timestamped folders
- **Archive regularly**: Old reports move to `reports/archive/`
- **Compare trends**: Use InfluxDB/Grafana for historical comparison
- **Document baselines**: Keep baseline performance metrics for regression testing

---

For more details on framework features and test case structure, see the [main README](./README.md).
