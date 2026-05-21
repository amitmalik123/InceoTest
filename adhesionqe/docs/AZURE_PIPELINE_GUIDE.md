# Azure Pipeline Guide - Python Playwright BDD Tests

## Overview
This pipeline runs Python-based Playwright BDD tests using pytest, pytest-bdd, and generates Allure reports.

## Pipeline Configuration

### Agent Pool
- **Default**: `ubuntu-22.04` (Microsoft-hosted)
- **Custom**: Change `vmImage` to `name: 'your-pool-name'` if using self-hosted agents

### Trigger
- **Manual runs**: Enabled with parameters
- **Scheduled runs**: Daily at 12:35 PM PST (20:35 UTC) on main branch
- **Branch triggers**: Disabled (`trigger: none`)

### Parameters (Manual Runs)

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `environment` | Target test environment | `test11` | test11, test12, silo, prod, qa |
| `marker` | Pytest marker to filter tests | `roth_conversion` | Any pytest marker |
| `workers` | Number of parallel workers | `2` | Any number (string) |

## How to Run

### Manual Pipeline Run
1. Go to Azure Pipelines
2. Select your pipeline
3. Click "Run pipeline"
4. Choose parameters:
   - **Environment**: `test11` (or test12, silo, prod, qa)
   - **Marker**: `roth_conversion` (or smoke, regression, etc.)
   - **Workers**: `2` (parallel execution)
5. Click "Run"

### Command Line (Azure CLI)
```bash
az pipelines run \
  --name "YourPipelineName" \
  --parameters environment=test11 marker=roth_conversion workers=2
```

## Test Execution

### Pytest Command
The pipeline runs pytest with:
```bash
pytest -m <marker> -n <workers> -v --headed \
  --alluredir=reports/allure-results \
  --junitxml=reports/test-results/junit-results.xml \
  --html=reports/test-results/pytest-report.html \
  --self-contained-html
```

### Environment Variables
- `TEST_ENV`: Set to selected environment (test11, test12, etc.)
- `CI=true`: Indicates running in CI/CD
- `PYTHONUNBUFFERED=1`: Ensures real-time log output

### Test Selection
Tests are filtered using pytest markers:
- `-m roth_conversion`: Runs tests marked with `@pytest.mark.roth_conversion`
- `-m smoke`: Runs smoke tests
- `-m "smoke and not slow"`: Combines markers

## Reports & Artifacts

### Published Artifacts

1. **PytestResults**
   - JUnit XML: `junit-results.xml`
   - HTML Report: `pytest-report.html`
   - Location: `reports/test-results/`

2. **AllureReport**
   - Interactive HTML report
   - Location: `reports/allure-report/`
   - View: Download artifact and open `index.html`

3. **AllureResults**
   - Raw test data for trending
   - Location: `reports/allure-results/`

### Viewing Reports

#### In Azure Pipelines
- **Tests Tab**: Shows JUnit test results with pass/fail status
- **Artifacts**: Download published artifacts

#### Allure Report
```bash
# Download AllureReport artifact, extract, then:
cd allure-report
python -m http.server 8080
# Open http://localhost:8080 in browser
```

## Pipeline Steps

### 1. Setup Phase
- Checkout repository
- Install Python 3.12
- Install dependencies from `requirements.txt`
- Install Playwright browsers with system dependencies
- Install Allure CLI

### 2. Test Execution
- Set environment variables (TEST_ENV, CI)
- Create report directories
- Run pytest with markers and parallel execution
- Generate JUnit XML and HTML reports
- Capture Allure results

### 3. Reporting Phase
- Generate Allure HTML report
- Verify test artifacts
- Push metrics to InfluxDB (optional)
- Publish test results to Azure Pipelines
- Publish artifacts (Pytest HTML, Allure Report, Allure Results)

## Customization

### Change Python Version
```yaml
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'  # Change to 3.11, 3.10, etc.
```

### Add Browser Options
```yaml
# In pytest command
pytest -m $(PYTEST_MARKER) \
  --browser chromium \
  --browser firefox \
  --browser webkit
```

### Change Parallel Workers
- Adjust `workers` parameter in manual run
- Default is 2 (modify in parameters section)

### Environment-Specific Configuration
Tests automatically load config from `config/env.<environment>.yaml` based on `TEST_ENV`:
- `test11` → `config/env.test11.yaml`
- `test12` → `config/env.test12.yaml`
- etc.

## Troubleshooting

### Tests Not Running
- Check `PYTEST_MARKER` matches actual test markers
- Verify tests exist with: `pytest --collect-only -m <marker>`

### Browser Installation Failed
- Ensure `playwright install chromium --with-deps` succeeds
- May need: `sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0`

### Allure Report Empty
- Check `reports/allure-results/` has JSON files
- Verify `allure-pytest` plugin is installed
- Ensure pytest runs with `--alluredir` flag

### InfluxDB Metrics Failed
- Check `INFLUXDB_TOKEN` variable is set in pipeline
- Verify `utils/influx_reporter.py` exists
- Step is marked `continueOnError: true` so won't fail pipeline

### Test Environment Not Loading
- Verify `TEST_ENV` is exported before pytest runs
- Check `config/env.<environment>.yaml` exists
- Review `utils/settings.py` loads environment correctly

## Best Practices

1. **Use Markers**: Tag tests appropriately (@smoke, @regression, @critical)
2. **Parallel Execution**: Use `-n` workers for faster runs
3. **Environment Isolation**: Each environment has separate config/data files
4. **Artifact Retention**: Set retention policy in Azure DevOps
5. **Schedule Strategically**: Run smoke tests frequently, full regression nightly
6. **Monitor Trends**: Use Allure history for test stability analysis

## Example Workflow

### Daily Smoke Tests
```yaml
schedules:
  - cron: "0 9 * * *"  # 9 AM daily
    displayName: "Daily Smoke Tests"
    branches:
      include: [main]
    always: true
```
Set default marker to `smoke` in parameters.

### Full Regression (Weekly)
```yaml
schedules:
  - cron: "0 2 * * 0"  # 2 AM Sundays
    displayName: "Weekly Regression"
    branches:
      include: [main]
    always: true
```
Set default marker to `regression` in parameters.

## Support

For issues or questions:
1. Check pipeline logs in Azure DevOps
2. Review test results in Tests tab
3. Download and inspect artifacts
4. Check `reports/test-results/pytest-report.html` for detailed test output
