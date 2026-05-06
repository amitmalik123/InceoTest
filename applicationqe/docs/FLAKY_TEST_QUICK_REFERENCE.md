# Flaky Test Detection - Quick Reference

## How It Works

### 1. Automatic Retry Detection
- **pytest-rerunfailures** plugin automatically retries failed tests
- Default: 2 retries with 1-second delay
- Configured in `pyproject.toml` and `tests/conftest.py`

### 2. Flaky Test Tracking
When a test **passes after failing** at least once:
```
Attempt 1: FAIL ❌
Attempt 2: PASS ✅  ← Flaky test detected!
```

The tracker records:
- Test name and ID
- Total attempts (2)
- Failed attempts (1)
- Final status (passed)
- Duration
- Error message

### 3. Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Test Execution (pytest with --reruns=2)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Test 1: Pass on first try          → No tracking         │
│  Test 2: Fail → Pass (2 attempts)   → Track as flaky! ⚠️  │
│  Test 3: Fail → Fail → Fail         → Track as failed     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Flaky Test Tracker (conftest.py hooks)                     │
├─────────────────────────────────────────────────────────────┤
│  - pytest_runtest_setup()    → Count attempts              │
│  - pytest_runtest_makereport() → Detect flaky pattern      │
│  - pytest_sessionfinish()    → Push to InfluxDB           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ InfluxDB Bucket: "AutomationData"                          │
├─────────────────────────────────────────────────────────────┤
│  Measurement: flaky_tests                                  │
│  Tags: test_name, environment, build_id, final_status     │
│  Fields: total_attempts, failed_attempts, duration_ms      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Grafana Dashboard                                          │
├─────────────────────────────────────────────────────────────┤
│  - Flaky test count over time                             │
│  - Top 10 flaky tests                                     │
│  - Flaky rate by environment                              │
│  - Alert: Flaky rate > 10%                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

### Local Execution
Set in terminal or `.env` file:
```bash
# Windows PowerShell
$env:INFLUXDB_URL="http://azncc03perf.corp.local:8086"
$env:INFLUXDB_TOKEN="your-token"
$env:INFLUXDB_ORG="MF"
$env:INFLUXDB_BUCKET="AutomationData"
$env:TEST_ENV="test11"
$env:BUILD_ID="local"

# Run tests
pytest tests/ui/test_add_ach.py -v
```

### CI/CD Execution
**Automatically set in Azure Pipeline** via `variables` and `env` sections:

```yaml
# FormsAndTracking.yaml - Lines 67-74
variables:
  INFLUXDB_URL: 'http://azncc03perf.corp.local:8086'
  INFLUXDB_ORG: 'MF'
  INFLUXDB_BUCKET: 'AutomationData'
  INFLUXDB_TOKEN: 'g5gf0ukY8fPdwaWynLviDLd0wz1l5snomLbip3t2IrQkeNNkiEFYECEHlcJLwsAPvv2Gx-op4ho6QcpVsCpdGQ=='

# Passed to pytest execution - Lines 241-247
env:
  INFLUXDB_URL: $(INFLUXDB_URL)      # ✅ Available during test execution
  INFLUXDB_TOKEN: $(INFLUXDB_TOKEN)  # ✅ Available during test execution
  INFLUXDB_ORG: $(INFLUXDB_ORG)
  INFLUXDB_BUCKET: $(INFLUXDB_BUCKET)
```

---

## Where InfluxDB Credentials Are Used

### 1. During Test Execution (NEW ✅)
**File:** `tests/conftest.py` → `pytest_sessionfinish()`
- **Purpose:** Push flaky test metrics immediately after tests complete
- **Requires:** InfluxDB env vars during pytest execution
- **Data:** Individual flaky test details

### 2. Post-Execution Reporter
**File:** `utils/influx_reporter.py`
- **Purpose:** Parse Allure results and push aggregated metrics
- **Requires:** InfluxDB env vars after tests complete
- **Data:** Total passed/failed/flaky counts, pass rate, duration

---

## Testing Flaky Detection

### Local Test (Simulate Flaky Test)

Create a flaky test:
```python
# tests/ui/test_flaky_demo.py
import random
import pytest

@pytest.mark.flaky_demo
def test_flaky_example():
    """Randomly fails to simulate flakiness"""
    if random.random() < 0.5:  # 50% chance to fail
        raise AssertionError("Simulated flaky failure")
    assert True
```

Run with retries:
```bash
pytest tests/ui/test_flaky_demo.py -v --reruns=2
```

Expected output:
```
⚠️  FLAKY TEST DETECTED:
   Test: tests/ui/test_flaky_demo.py::test_flaky_example
   Attempts: 2 (failed: 1)
   Final Status: passed
   Duration: 150ms

📊 Pushing 1 flaky test metric(s) to InfluxDB...
✓ Successfully pushed flaky test metrics to InfluxDB
```

### CI/CD Test

Trigger pipeline with:
- Marker: `add_ach`
- Workers: `1` or `2`

Check InfluxDB after execution:
```flux
from(bucket: "AutomationData")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
```

---

## Configuration Options

### Customize Retry Behavior

**In `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
addopts = """
--reruns=3          # Increase to 3 retries
--reruns-delay=2    # Increase delay to 2 seconds
--only-rerun=AssertionError  # Only retry assertion failures
"""
```

**Via CLI (override config):**
```bash
pytest -v --reruns=5 --reruns-delay=1
```

**Disable retries (no flaky detection):**
```bash
pytest -v --reruns=0
```

### Mark Specific Tests as Expected to Be Flaky

```python
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_known_flaky():
    """This test is known to be flaky, retry 5 times"""
    assert external_api_call()
```

---

## Grafana Queries

### Current Flaky Rate
```flux
from(bucket: "AutomationData")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "test_quality")
  |> filter(fn: (r) => r["_field"] == "flaky_rate")
  |> last()
```

### Flaky Tests This Week
```flux
from(bucket: "AutomationData")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> distinct(column: "test_name")
  |> count()
```

### Most Flaky Test
```flux
from(bucket: "AutomationData")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "flaky_tests")
  |> group(columns: ["test_name"])
  |> count()
  |> group()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 1)
```

---

## Troubleshooting

### Flaky Tests Not Tracked in CI/CD?

**Check:**
1. ✅ InfluxDB env vars passed to pytest execution step (FormsAndTracking.yaml line 241-247)
2. ✅ `pytest-rerunfailures` installed (requirements.txt line 43)
3. ✅ `--reruns` flag in addopts (pyproject.toml line 49)
4. ✅ InfluxDB token has write permissions

**Verify in pipeline logs:**
```
⚠️  FLAKY TEST DETECTED:
   Test: tests/ui/test_add_ach.py::test_scenario_1
   Attempts: 2 (failed: 1)
   ...
📊 Pushing 1 flaky test metric(s) to InfluxDB...
✓ Successfully pushed flaky test metrics to InfluxDB
```

### Flaky Tests Not Tracked Locally?

**Set environment variables:**
```powershell
$env:INFLUXDB_URL="http://azncc03perf.corp.local:8086"
$env:INFLUXDB_TOKEN="your-token"
$env:INFLUXDB_ORG="MF"
$env:INFLUXDB_BUCKET="AutomationData"
```

**Or skip InfluxDB (still shows console output):**
```bash
# Unset token to skip push (still detects flaky tests)
$env:INFLUXDB_TOKEN=""
pytest tests/ui/ -v
```

---

## Benefits

1. **Early Detection:** Know which tests are unstable before they block deployments
2. **Root Cause Analysis:** Error messages help identify why tests are flaky
3. **Trend Analysis:** Track if flakiness is increasing over time
4. **Environment Comparison:** See which environments have more flaky tests
5. **Test Quality Metrics:** Measure test suite stability

---

## Next Steps

1. ✅ Run CI/CD pipeline to verify flaky tracking
2. ✅ Create Grafana dashboard (see FLAKY_TEST_DETECTION.md)
3. ✅ Set up alerts for flaky rate > 10%
4. ✅ Review top flaky tests weekly
5. ✅ Fix or mark expected flaky tests with `@pytest.mark.flaky`
