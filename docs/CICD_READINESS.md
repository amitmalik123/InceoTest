# CI/CD Readiness Checklist ✅

## Status: **READY FOR CI/CD** 🚀

Last Updated: January 6, 2026

---

## ✅ Prerequisites Met

### 1. Dependencies Installed
- ✅ **pytest-xdist (3.6.1)** - Parallel execution
- ✅ **allure-pytest (2.15.2)** - Reporting
- ✅ **pytest-bdd (7.3.0)** - BDD support
- ✅ All dependencies in requirements.txt

### 2. Folder Structure
- ✅ `reports/junit/` - JUnit XML for Azure DevOps
- ✅ `reports/allure-results/` - Auto-created by pytest
- ✅ `reports/allure-report/` - Auto-generated
- ✅ `tests/.auth/` - Session storage
- ✅ `config/` - Environment configs (test11, test12, silo, qa, prod)

### 3. Configuration Files
- ✅ [FormsAndTracking.yaml](../FormsAndTracking.yaml) - CI/CD pipeline
- ✅ [pyproject.toml](../pyproject.toml) - Pytest config
- ✅ [requirements.txt](../requirements.txt) - Dependencies
- ✅ Environment configs (5 environments)

### 4. Reporting Setup
- ✅ **Allure Reports** - Auto-generated with `--single-file`
- ✅ **JUnit XML** - Published to Azure DevOps Tests tab
- ✅ **pytest-html** - Self-contained HTML reports
- ✅ **InfluxDB** - Performance metrics (optional)

### 5. Parallel Execution
- ✅ **Worker isolation** - Separate sessions per worker
- ✅ **Distribution strategy** - `loadscope` (scenario-level)
- ✅ **Configurable workers** - Pipeline parameter (default: 1, scheduled: 2)
- ✅ **Session management** - Worker-specific auth files

### 6. Session Management
- ✅ **Auto session reuse** - Saves login state
- ✅ **Expiration detection** - 8-hour timeout
- ✅ **Worker isolation** - Separate files per worker
- ✅ **Auto-renewal** - Detects expired sessions

---

## 🎯 Pipeline Parameters

### Manual Run Options
```yaml
environment: test11, test12, silo, qa, prod
marker: roth_conversion, add_ach, etc.
workers: 1 (default), 2, 4, auto
```

### Scheduled Run Defaults
```yaml
environment: test11
marker: roth_conversion
workers: 2 (parallel)
```

---

## 🚀 How to Run

### Azure DevOps Pipeline

**Manual Run:**
1. Go to Pipelines → Select pipeline
2. Click "Run pipeline"
3. Select parameters:
   - Environment: `test11` (or test12, silo, qa, prod)
   - Marker: `roth_conversion` (or add_ach)
   - Workers: `2` (or 1, 4, auto)
4. Click "Run"

**Scheduled Run:**
- Uncomment schedule in [FormsAndTracking.yaml](../FormsAndTracking.yaml)
- Runs daily at 12:35 PM PST on `test11` with 2 workers

### Local Testing (Before CI/CD)

**Sequential execution:**
```bash
pytest -m roth_conversion -v
```

**Parallel execution (2 workers):**
```bash
pytest -m roth_conversion -v -n 2 --dist loadscope
```

**Specific environment:**
```bash
$env:TEST_ENV="test12"
pytest -m roth_conversion -v -n 2 --dist loadscope
```

---

## 📊 CI/CD Outputs

### 1. Test Results
- **Location**: Azure DevOps Tests tab
- **Format**: JUnit XML
- **Path**: `reports/junit/junit-report.xml`

### 2. Allure Report
- **Artifact**: `AllureReport`
- **Format**: Single-file HTML
- **Features**: History, trends, categories, attachments

### 3. Pytest HTML Report
- **Artifact**: `PytestReport`
- **Format**: Self-contained HTML
- **Path**: `reports/pytest-report.html`

### 4. Test Artifacts
- **Videos**: Retained on failure only
- **Traces**: Retained on failure only
- **Screenshots**: On failure only
- **All published**: `TestResults` artifact

### 5. InfluxDB Metrics (Optional)
- Test duration
- Pass/fail counts
- Environment tags
- Build metadata

---

## 🔧 Pipeline Features

### Auto-Configuration
- ✅ Python 3.10 setup
- ✅ Node.js 22.x for Playwright
- ✅ Chromium browser installation
- ✅ Allure CLI installation
- ✅ Environment detection (manual vs scheduled)

### Parallel Execution Support
```bash
# Pipeline dynamically builds command:
pytest -m "roth_conversion" \
  -v \
  -n 2 \                              # Added if workers > 1
  --dist loadscope \                  # Added if workers > 1
  --alluredir="reports/allure-results" \
  --junitxml="reports/junit/junit-report.xml" \
  --html="reports/pytest-report.html" \
  --self-contained-html \
  --video=retain-on-failure \
  --tracing=retain-on-failure \
  --screenshot=only-on-failure
```

### Report Generation
- ✅ Auto-clears old allure-results
- ✅ Generates single-file Allure HTML
- ✅ Creates timestamped copies locally (not in CI)
- ✅ Publishes all artifacts to Azure

### Session Management in CI
- ✅ First run: Login and save session
- ✅ Subsequent runs: Reuse session (if < 8 hours old)
- ✅ Expired sessions: Auto-detect and re-login
- ✅ Parallel workers: Isolated session files

---

## ⚙️ Environment Variables

### Set in Pipeline
```yaml
TEST_ENV: $(environment)           # test11, test12, silo, qa, prod
CI: true                          # Indicates CI environment
PYTHONUNBUFFERED: 1               # Real-time output
ALLURE_RESULTS_DIR: reports/allure-results
```

### Optional (Configured)
```yaml
WORK_ITEM_AUTH_TOKEN: $(WORK_ITEM_AUTH_TOKEN)  # API auth
PARTIES_AUTH_TOKEN: $(PARTIES_AUTH_TOKEN)       # API auth
INFLUXDB_URL: http://azncc03perf.corp.local:8086
INFLUXDB_ORG: MF
INFLUXDB_BUCKET: AutomationData
INFLUXDB_TOKEN: <configured>
```

---

## 🎯 Execution Flow

### Pipeline Execution Steps

1. **Checkout Code** - Clean checkout from repo
2. **Set Environment** - Determine env, marker, workers
3. **Setup Python 3.10** - Install Python
4. **Install Dependencies** - `pip install -e .`
5. **Setup Node.js** - Install Node.js 22.x
6. **Install Playwright** - `npx playwright install chromium`
7. **Install Allure CLI** - `npm install allure-commandline`
8. **Run Tests** - Execute pytest with parallel support
9. **Generate Allure Report** - `allure generate --single-file`
10. **Push InfluxDB Metrics** - Performance tracking
11. **Publish Artifacts**:
    - TestResults (all output)
    - PytestReport (HTML)
    - AllureReport (HTML)
    - AllureResults (JSON)
12. **Publish Test Results** - JUnit XML to Tests tab

### Parallel Execution Flow (workers > 1)

```
Master Process
  ├─ Worker 0 (gw0)
  │  ├─ Session: username_gw0.json
  │  ├─ Videos: test-results/videos/gw0/
  │  └─ Runs scenarios 0, 2, 4...
  │
  ├─ Worker 1 (gw1)
  │  ├─ Session: username_gw1.json
  │  ├─ Videos: test-results/videos/gw1/
  │  └─ Runs scenarios 1, 3, 5...
  │
  └─ Collects results → allure-results/
```

---

## 🔍 Verification Steps

### Before Triggering Pipeline

1. **Check local execution:**
   ```bash
   pytest -m roth_conversion -v
   ```

2. **Test parallel locally:**
   ```bash
   pytest -m roth_conversion -v -n 2 --dist loadscope
   ```

3. **Verify environment config:**
   ```bash
   cat config/env.test11.yaml
   ```

4. **Check dependencies:**
   ```bash
   pip list | Select-String "pytest|playwright|allure"
   ```

### After Pipeline Run

1. **Check Test Results Tab** - Pass/fail status
2. **Download Artifacts**:
   - AllureReport → View index.html
   - PytestReport → View pytest-report.html
3. **Review Logs** - Check for warnings/errors
4. **InfluxDB Dashboard** - View metrics (if configured)

---

## 🐛 Troubleshooting

### Common Issues

**1. Session expired in CI**
- **Symptom**: Tests redirect to login
- **Solution**: Auto-handled by session expiration detection
- **Logs**: Check `[SESSION DEBUG]` messages

**2. Parallel execution conflicts**
- **Symptom**: "Permission denied" on trace files
- **Solution**: Already fixed with worker-specific directories
- **Verify**: Each worker has separate videos/gw0, videos/gw1

**3. Allure report not generated**
- **Symptom**: Empty AllureReport artifact
- **Check**: allure-results has JSON files
- **Solution**: Pipeline auto-generates even if empty

**4. Tests fail in CI but pass locally**
- **Check**: Environment variables (TEST_ENV)
- **Check**: Browser installation logs
- **Check**: Session file permissions

**5. Parallel workers hanging**
- **Check**: Worker count vs available CPU
- **Solution**: Use `workers: auto` or reduce count
- **Timeout**: Pipeline timeout set to 45 minutes

---

## 📋 Quick Reference

### Run Commands

| Scenario | Command |
|----------|---------|
| Single test, sequential | `pytest -m roth_conversion -v` |
| Single test, parallel | `pytest -m roth_conversion -v -n 2 --dist loadscope` |
| All tests, parallel | `pytest tests/ui/ -v -n auto --dist loadscope` |
| Specific env | `$env:TEST_ENV="test12"; pytest -m roth_conversion -v` |
| With headed browser | `pytest -m roth_conversion -v --headed --slowmo=500` |
| Generate Allure locally | `allure generate reports/allure-results -o reports/allure-report --clean --single-file` |

### Pipeline Triggers

| Type | When | Environment | Workers |
|------|------|-------------|---------|
| Manual | On-demand | User selects | User selects |
| Scheduled | Daily 12:35 PM PST | test11 | 2 |
| PR | Disabled | - | - |
| Push | Disabled | - | - |

### Artifacts

| Name | Contents | Size |
|------|----------|------|
| TestResults | All reports, videos, traces | ~50-200 MB |
| AllureReport | Single HTML file + assets | ~5-10 MB |
| PytestReport | Single HTML file | ~1-2 MB |
| AllureResults | JSON data files | ~1-5 MB |

---

## ✅ Final Checklist

Before triggering CI/CD pipeline, verify:

- [ ] Requirements.txt has all dependencies
- [ ] Environment configs exist (config/env.*.yaml)
- [ ] Tests pass locally (`pytest -m roth_conversion -v`)
- [ ] Parallel execution works (`pytest -m roth_conversion -v -n 2 --dist loadscope`)
- [ ] Session storage working (check tests/.auth/)
- [ ] Azure Pipeline YAML updated
- [ ] Pool configuration correct (`ubuntu2204-qa`)
- [ ] Secrets configured in Azure DevOps:
  - [ ] WORK_ITEM_AUTH_TOKEN
  - [ ] PARTIES_AUTH_TOKEN
  - [ ] INFLUXDB_TOKEN (if using metrics)

---

## 🎉 You're Ready!

All prerequisites are met. Your framework is **production-ready** for CI/CD execution with:

✅ Parallel execution support
✅ Auto-generated reports (Allure + pytest-html + JUnit)
✅ Session management with expiration handling
✅ Worker isolation for conflict-free parallel runs
✅ Comprehensive artifact publishing
✅ InfluxDB metrics tracking
✅ Multi-environment support

**Next Step**: Trigger your Azure Pipeline! 🚀

---

## 📚 Related Documentation

- [Parallel Execution Guide](PARALLEL_EXECUTION_GUIDE.md)
- [Azure Pipeline Guide](AZURE_PIPELINE_GUIDE.md)
- [Allure Reports Guide](allureReadme.md)
- [Framework Guide](FRAMEWORK_GUIDE.md)
- [Environment Configuration](ENVIRONMENT_GUIDE.md)
