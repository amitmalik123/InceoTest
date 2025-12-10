# Playwright QA Automation Pipeline Documentation

## Overview
This document provides comprehensive documentation for the Playwright QA automation pipeline setup, covering JUnit XML report generation, Allure reporting, InfluxDB metrics, and Playwright test execution.

---

## Table of Contents
1. [JUnit XML Report Generation](#junit-xml-report-generation)
2. [Allure Reporting](#allure-reporting)
3. [InfluxDB Metrics Integration](#influxdb-metrics-integration)
4. [Playwright Test Configuration](#playwright-test-configuration)
5. [Azure Pipeline Setup](#azure-pipeline-setup)
6. [Running Tests](#running-tests)
7. [Troubleshooting](#troubleshooting)

---

## JUnit XML Report Generation

### Overview
JUnit XML reports are generated through a **3-tier fallback approach** to ensure test results are always available for publishing in Azure DevOps.

### Architecture

#### **Tier 1: Playwright Native Reporter (Primary)**
Playwright's built-in JUnit reporter generates the report directly during test execution.

**Configuration in `playwright.config.ts`:**
```typescript
reporter: [
  ['allure-playwright', { outputFolder: join(__dirname, 'target/allure-results') }],
  ['html', { outputFolder: join(__dirname, 'playwright-report') }],
  ['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }],
],
```

**Key Points:**
- Uses **absolute paths** with `join(__dirname, ...)` to ensure file creation regardless of working directory
- Output file: `applicationqe/ewmnavbar/test-results/junit-report.xml`
- Generates standard JUnit XML format compatible with Azure DevOps PublishTestResults task

#### **Tier 2: Generate from Allure Results (Fallback)**
If Playwright doesn't generate the junit report, extract test data from Allure JSON results.

**Process:**
1. Find all Allure result files: `target/allure-results/*-result.json`
2. Parse JSON to extract:
   - Test name (from `"name":"..."`)
   - Test status (from `"status":"passed|failed|skipped"`)
3. Generate JUnit XML with:
   - Test counts (total, passed, failed, skipped)
   - Individual test case entries with proper status tags

**Example Bash Logic:**
```bash
# Count test results from Allure JSON files
TEST_COUNT=$(find "$ALLURE_RESULTS_DIR" -name "*-result.json" -type f 2>/dev/null | wc -l)
FAILED_COUNT=$(find "$ALLURE_RESULTS_DIR" -name "*-result.json" \
  -exec grep -l '"status":"failed"' {} \; 2>/dev/null | wc -l)
PASSED_COUNT=$((TEST_COUNT - FAILED_COUNT))
SKIPPED_COUNT=$(find "$ALLURE_RESULTS_DIR" -name "*-result.json" \
  -exec grep -l '"status":"skipped"' {} \; 2>/dev/null | wc -l)

# Parse individual test data
find "$ALLURE_RESULTS_DIR" -name "*-result.json" -type f 2>/dev/null | while read -r result_file; do
  TEST_NAME=$(grep -o '"name":"[^"]*' "$result_file" | head -1 | cut -d'"' -f4)
  STATUS=$(grep -o '"status":"[^"]*' "$result_file" | head -1 | cut -d'"' -f4)
  # Generate XML testcase based on STATUS
done
```

#### **Tier 3: Empty Fallback (Last Resort)**
If no test data is available, create a minimal valid JUnit XML to prevent publishing failure.

**Minimal Valid Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Playwright Test Results" tests="0" failures="0" skipped="0" time="0.000">
  <testsuite name="Playwright Tests" tests="0" failures="0" skipped="0" time="0.000">
    <properties>
      <property name="note" value="No test results available - Check Allure report for details"/>
    </properties>
  </testsuite>
</testsuites>
```

### Implementation in Azure Pipeline

**Step: Generate JUnit Report for Publishing**
```yaml
- script: |
    # Define paths
    SRC_JUNIT="$(ewmnavbarPath)/test-results/junit-report.xml"
    DEST_JUNIT="$(buildPath)/test-results/junit-report.xml"
    
    # Tier 1: Check if Playwright generated it
    if [ -f "$SRC_JUNIT" ]; then
      mkdir -p "$(buildPath)/test-results"
      cp "$SRC_JUNIT" "$DEST_JUNIT"
    else
      # Tier 2 & 3: Generate from Allure or create empty
      # ... fallback logic here
    fi
  displayName: "Generate JUnit Report for Publishing"
  continueOnError: true
```

### JUnit XML Output Locations
- **Source:** `applicationqe/ewmnavbar/test-results/junit-report.xml`
- **Published to:** `$(Build.SourcesDirectory)/test-results/junit-report.xml`
- **Published by task:** `PublishTestResults@2` with `testResultsFormat: 'JUnit'`

---

## Allure Reporting

### Overview
Allure provides detailed, interactive test reports with history and trends. The pipeline generates both Allure results (JSON) and a formatted HTML report.

### Configuration in `playwright.config.ts`

```typescript
['allure-playwright', { outputFolder: join(__dirname, 'target/allure-results') }],
```

**Output Location:** `applicationqe/ewmnavbar/target/allure-results/`

### Allure Result Files Structure

Allure stores test execution data in JSON format:
- **`*-result.json`** - Individual test result (one per test)
- **`*-attachment`** - Test attachments (screenshots, logs, etc.)
- **`categories.json`** - Test categorization
- **`environment.properties`** - Environment info

### JSON Result File Example
```json
{
  "name": "test_name",
  "status": "passed",
  "stage": "finished",
  "steps": [...],
  "attachments": [...],
  "parameters": {...},
  "start": 1702156800000,
  "stop": 1702156900000,
  "uuid": "unique-id"
}
```

### Pipeline Steps for Allure Report Generation

#### Step 1: Install Allure CLI
```yaml
- script: |
    mkdir -p $(allureToolsDir)
    npm install allure-commandline --prefix $(allureToolsDir)
    export PATH="$(allureToolsDir)/node_modules/.bin:$PATH"
    allure --version
  displayName: "Install and Verify Allure CLI"
```

#### Step 2: Generate Allure Report
```yaml
- script: |
    mkdir -p "$(allureReportDir)"
    allure generate \
      --clean \
      -o "$(allureReportDir)" \
      "$(allureResultsDir)"
    echo "✓ Allure report generated at: $(allureReportDir)"
  displayName: "Generate Allure Report"
  env:
    PATH: "$(allureToolsDir)/node_modules/.bin:$PATH"
```

**Command Breakdown:**
- `allure generate` - Generate HTML report from results
- `--clean` - Clean previous report directory
- `-o` - Output directory
- Source directory - Where Allure JSON results are stored

#### Step 3: Copy Reports to Artifacts
```yaml
- task: CopyFiles@2
  inputs:
    SourceFolder: '$(allureReportDir)'
    Contents: '**/*'
    TargetFolder: '$(Build.ArtifactStagingDirectory)/allure-report'
  displayName: "Copy Allure Report to Artifacts"
```

### Accessing Allure Reports

**In Azure DevOps Pipeline:**
1. Go to pipeline run
2. Click "Published" artifacts tab
3. Download `allure-report` folder
4. Open `index.html` in browser

**Report Features:**
- Timeline view of test execution
- Failure analysis with root causes
- Test history and trends
- Screenshots and logs attached to failed tests
- Category-based filtering
- Retry analysis

---

## InfluxDB Metrics Integration

### Overview
InfluxDB stores test execution metrics for long-term trend analysis and performance monitoring.

### Configuration

**Pipeline Variables:**
```yaml
INFLUXDB_URL: 'http://azncc03perf.corp.local:8086'
INFLUXDB_ORG: 'MF'
INFLUXDB_BUCKET: 'AutomationData'
INFLUXDB_TOKEN: '$(InfluxDBToken)'  # Secret variable
```

### Metrics Reported

**Key Metrics:**
- Total tests executed
- Passed/Failed/Skipped counts
- Pass rate percentage
- Execution time
- Environment (test/dev)
- Build ID and reason
- Test project
- Pipeline URL

### Implementation Steps

#### Step 1: Setup Python
```yaml
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.x'
  displayName: "Setup Python for InfluxDB Reporter"
```

#### Step 2: Install Dependencies
```yaml
- script: |
    pip install -r $(Build.SourcesDirectory)/applicationqe/ewmnavbar/framework/reporter/requirements.txt
  displayName: "Install Python Dependencies"
```

**requirements.txt:**
```
influxdb-client>=1.18.0
```

#### Step 3: Run InfluxDB Reporter
```yaml
- script: |
    export INFLUXDB_URL="${INFLUXDB_URL}"
    export INFLUXDB_TOKEN="${INFLUXDB_TOKEN}"
    export INFLUXDB_ORG="${INFLUXDB_ORG}"
    export INFLUXDB_BUCKET="${INFLUXDB_BUCKET}"
    export ALLURE_RESULTS_DIR="$(allureResultsDir)"
    export ENVIRONMENT="$(environment)"
    export BUILD_ID="$(Build.BuildId)"
    
    python3 $(Build.SourcesDirectory)/applicationqe/ewmnavbar/framework/reporter/influx_reporter.py
  displayName: "Push Test Metrics to InfluxDB"
  continueOnError: true
```

### Example Python InfluxDB Reporter Script

**File: `framework/reporter/influx_reporter.py`**

```python
import json
import os
from datetime import datetime
from pathlib import Path
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

def get_allure_metrics():
    """Extract metrics from Allure results"""
    allure_dir = os.getenv('ALLURE_RESULTS_DIR')
    
    if not allure_dir or not os.path.exists(allure_dir):
        return None
    
    passed = failed = skipped = 0
    
    for file in Path(allure_dir).glob('*-result.json'):
        with open(file) as f:
            result = json.load(f)
            status = result.get('status', 'unknown')
            
            if status == 'passed':
                passed += 1
            elif status == 'failed':
                failed += 1
            elif status == 'skipped':
                skipped += 1
    
    total = passed + failed + skipped
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': pass_rate
    }

def send_to_influxdb(metrics):
    """Send metrics to InfluxDB"""
    client = InfluxDBClient(
        url=os.getenv('INFLUXDB_URL'),
        token=os.getenv('INFLUXDB_TOKEN'),
        org=os.getenv('INFLUXDB_ORG')
    )
    
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    point = {
        'measurement': 'test_execution',
        'tags': {
            'environment': os.getenv('ENVIRONMENT', 'unknown'),
            'project': 'ewmnavbar',
            'build_id': os.getenv('BUILD_ID')
        },
        'fields': {
            'total_tests': metrics['total'],
            'passed': metrics['passed'],
            'failed': metrics['failed'],
            'skipped': metrics['skipped'],
            'pass_rate': metrics['pass_rate']
        },
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    
    write_api.write(bucket=os.getenv('INFLUXDB_BUCKET'), record=point)
    client.close()

if __name__ == '__main__':
    metrics = get_allure_metrics()
    if metrics:
        send_to_influxdb(metrics)
        print(f"✓ Metrics sent to InfluxDB: {metrics}")
    else:
        print("⚠ No metrics to report")
```

---

## Playwright Test Configuration

### Overview
Playwright configuration defines test execution parameters, reporters, projects, and browser settings.

### Key Configuration File: `playwright.config.ts`

```typescript
import { defineConfig, devices } from "@playwright/test";
import { join } from "path";

export default defineConfig({
  // Test settings
  timeout: 3 * 60 * 1000,          // 3 minutes per test
  testDir: "./",                    // Root test directory
  testIgnore: ["**/unit-tests/**"], // Exclude unit tests
  
  // Parallel execution settings
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  
  // Reporters configuration
  reporter: [
    ['allure-playwright', { outputFolder: join(__dirname, 'target/allure-results') }],
    ['html', { outputFolder: join(__dirname, 'playwright-report') }],
    ['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }],
  ],
  
  // Projects
  projects: [
    // Unit tests
    {
      name: "unit-tests",
      testDir: "./unit-tests",
      testMatch: "/**/*.test.ts",
    },
    
    // Setup (authentication)
    {
      name: "setup",
      testDir: "./helper",
      testMatch: ["global.auth.setup.spec.ts"],
    },
    
    // Authenticated tests
    {
      name: "authenticated",
      testDir: "./e2e",
      testMatch: "/auth/**/*.spec.ts",
      dependencies: ["setup"],
      use: {
        storageState: join(__dirname, '.auth/user.json'),
      },
    },
    
    // Unauthenticated tests
    {
      name: "unauthenticated",
      testDir: "./e2e",
      testMatch: "/unauth/**/*.spec.ts",
    },
  ],
});
```

### Important Settings

**Absolute Paths for Reporters:**
```typescript
// ✅ CORRECT - Uses absolute path
['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }]

// ❌ WRONG - Uses relative path (may not work in CI)
['junit', { outputFile: 'test-results/junit-report.xml' }]
```

**Project Dependencies:**
```typescript
{
  name: "authenticated",
  dependencies: ["setup"],  // Runs setup first, then authenticated
}
```

**Authentication State Reuse:**
```typescript
use: {
  storageState: join(__dirname, '.auth/user.json'),
}
```

---

## Azure Pipeline Setup

### Pipeline Structure

```yaml
pool:
  name: 'ubuntu2204-qa'
  timeoutInMinutes: 10

jobs:
  - job: RunPlaywrightTests
    timeoutInMinutes: 60
    
    variables:
      buildPath: '$(Build.SourcesDirectory)'
      ewmnavbarPath: '$(Build.SourcesDirectory)/applicationqe/ewmnavbar'
      allureResultsDir: '$(ewmnavbarPath)/target/allure-results'
      allureReportDir: '$(ewmnavbarPath)/target/allure-report'
      INFLUXDB_URL: 'http://azncc03perf.corp.local:8086'
      INFLUXDB_TOKEN: '$(InfluxDBToken)'  # Secret variable
```

### Key Pipeline Tasks

#### 1. Checkout Code
```yaml
- checkout: self
  clean: true
```

#### 2. Setup Node.js
```yaml
- task: NodeTool@0
  inputs:
    versionSpec: "22.x"
  displayName: "Install Node.js"
```

#### 3. Install Dependencies
```yaml
- script: npm ci --ignore-scripts
  displayName: "Install Dependencies"
```

#### 4. Install Browsers
```yaml
- script: npx playwright install chromium
  displayName: "Install Playwright Browsers"
```

#### 5. Run Tests
```yaml
- script: |
    export ALLURE_RESULTS_DIR="$(allureResultsDir)"
    export CI=true
    npx playwright test
  displayName: "Run Playwright Tests"
  workingDirectory: $(ewmnavbarPath)
  continueOnError: true
```

#### 6. Generate Reports & Metrics
- Copy Allure report
- Generate JUnit XML
- Push metrics to InfluxDB

#### 7. Publish Results
```yaml
- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '$(buildPath)/test-results/junit-report.xml'
    testRunTitle: 'Playwright Tests'
    failTaskOnFailedTests: false
  condition: always()
```

---

## Running Tests

### Local Development

**Run all tests:**
```bash
npx playwright test
```

**Run specific project:**
```bash
npx playwright test --project=authenticated
```

**Run specific test file:**
```bash
npx playwright test tests/auth/ClientsPages.spec.ts
```

**Run with grep filter:**
```bash
npx playwright test --grep "sub-menus"
```

**Debug mode:**
```bash
npx playwright test --debug
```

**Headed mode (see browser):**
```bash
npx playwright test --headed
```

### Azure Pipeline (Manual Trigger)

**Parameters available:**
- **Environment:** test, dev
- **Test Project:** all, authenticated, unauthenticated, local, unit-tests, setup
- **Test Filter:** Specific test name or pattern (e.g., "Accounts", "Investments")

---

## Troubleshooting

### Issue: JUnit XML Not Generated

**Diagnosis:**
```bash
# Check if test-results directory exists
ls -la applicationqe/ewmnavbar/test-results/

# Check if junit-report.xml was created
[ -f applicationqe/ewmnavbar/test-results/junit-report.xml ] && echo "Found" || echo "Not found"
```

**Solutions:**

1. **Verify Playwright config has absolute path:**
   ```typescript
   ['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }]
   ```

2. **Ensure tests actually ran:**
   - Check for Allure results in `target/allure-results/`
   - Verify test exit code is 0 or 1 (not error)

3. **Check for authentication issues:**
   - Verify credentials in `.env.test` are correct
   - Check if setup project runs successfully

4. **Manual fallback XML creation:**
   ```bash
   mkdir -p $(buildPath)/test-results
   printf '<?xml version="1.0" encoding="UTF-8"?>\n<testsuites name="Playwright Test Results" tests="0" failures="0" skipped="0" time="0.000">\n  <testsuite name="Playwright Tests" tests="0" failures="0" skipped="0" time="0.000"></testsuite>\n</testsuites>\n' > $(buildPath)/test-results/junit-report.xml
   ```

### Issue: Allure Report Not Generated

**Check Allure CLI installation:**
```bash
allure --version
```

**Verify results directory:**
```bash
ls -la applicationqe/ewmnavbar/target/allure-results/
```

**Generate report manually:**
```bash
allure generate \
  --clean \
  -o applicationqe/ewmnavbar/target/allure-report \
  applicationqe/ewmnavbar/target/allure-results
```

### Issue: InfluxDB Metrics Not Sent

**Check environment variables:**
```bash
echo $INFLUXDB_URL
echo $INFLUXDB_ORG
echo $INFLUXDB_BUCKET
```

**Verify connection:**
```bash
curl -X GET "http://azncc03perf.corp.local:8086/api/v2/health"
```

**Check Python dependencies:**
```bash
pip list | grep influxdb
```

### Issue: Tests Not Running

**Check project configuration:**
```bash
npx playwright test --list
```

**Verify environment file:**
```bash
cat applicationqe/ewmnavbar/env/.env.test
```

**Check test files exist:**
```bash
find applicationqe/ewmnavbar -name "*.spec.ts" | head -10
```

---

## Summary

This comprehensive setup ensures:

✅ **Reliable Test Reporting** - JUnit XML always available through 3-tier fallback  
✅ **Detailed Analytics** - Allure reports with screenshots and history  
✅ **Metrics Tracking** - InfluxDB for long-term trend analysis  
✅ **CI/CD Integration** - Full Azure DevOps pipeline support  
✅ **Flexible Execution** - Multiple test projects with dependencies  
✅ **Easy Debugging** - Comprehensive logging and diagnostics  

For questions or issues, refer to the troubleshooting section or check the specific step logs in Azure DevOps.
