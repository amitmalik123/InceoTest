# Azure Pipeline Guide

> **CI/CD Setup for Billing QE Automation**  
> Platform Revenue Dashboard · Strategist Group Model

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Billing Pipeline File](#billing-pipeline-file)
3. [Trigger Strategy](#trigger-strategy)
4. [Pipeline Stages and Steps](#pipeline-stages-and-steps)
5. [Agent Pool Requirements](#agent-pool-requirements)
6. [Secret Variables Configuration](#secret-variables-configuration)
7. [Artifact Publishing](#artifact-publishing)
8. [Running the Pipeline Manually](#running-the-pipeline-manually)
9. [Scheduled Execution](#scheduled-execution)
10. [Adding New Test Coverage to the Pipeline](#adding-new-test-coverage)

---

## Pipeline Overview

The Billing QE pipeline lives at:

```
azure-pipelines/prd_sgm.yml
```

It is designed as a **standalone team pipeline** — independent of other module pipelines (BAW, NAW, OAM, etc.). This lets the Billing team trigger, schedule, and monitor their own test runs without affecting other teams.

```
azure-pipelines/
├── prd_sgm.yml           ← Billing team pipeline (this guide)
├── baw.yml
├── naw.yml
├── oam.yml
├── proposal.yml
├── model-management.yml
├── stp-ict.yml
├── stp-journals.yml
├── full_regression.yml    ← Full cross-team regression
└── templates/
    └── team-stage.yml       ← Shared execution template
```

---

## Billing Pipeline File

```yaml
# azure-pipelines/prd_sgm.yml
name: billing-$(Date:yyyyMMdd)$(Rev:.r)

pool:
  name: 'ubuntu2204-qa'
  timeoutInMinutes: 10

trigger: none   # CI trigger disabled; manual or scheduled only

schedules:
  - cron: "30 8 * * *"   # 8:30 AM UTC (~12:30 AM PST) daily
    displayName: Daily Billing Regression
    branches:
      include:
        - main
    always: true

variables:
  - group: billing-qa-credentials    # Secret variable group in Azure DevOps

stages:
  - stage: BillingRegression
    displayName: Billing Platform Revenue Dashboard Tests
    jobs:
      - job: SGM_Tests
        displayName: Strategist Group Model
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'

          - script: |
              pip install -r requirements.txt
              playwright install chromium
            displayName: Install dependencies

          - script: |
              pytest tests/runners/platformrevenuedashboard/strategistgroupmodel/ \
                -m regression \
                -v \
                --tb=short
            displayName: Run SGM Regression
            env:
              BILLING_USERNAME: $(BILLING_USERNAME)
              BILLING_PASSWORD: $(BILLING_PASSWORD)
              CI: "true"

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: JUnit
              testResultsFiles: 'reports/**/junit.xml'
            condition: always()

          - task: PublishBuildArtifacts@1
            inputs:
              pathtoPublish: 'reports/platformrevenuedashboard'
              artifactName: billing-test-reports
            condition: always()
```

---

## Trigger Strategy

| Trigger Type | Status | Details |
|-------------|--------|--------|
| Push (CI) | Disabled | Can be enabled for branch-specific triggers |
| Pull Request | Not configured | Optional — enable per team policy |
| Scheduled | **Enabled** | Daily at 8:30 AM UTC (12:30 AM PST) |
| Manual | **Enabled** | Run on-demand from Azure DevOps UI |

To enable CI triggers, uncomment the `trigger:` block in `prd_sgm.yml` and configure path filters:

```yaml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - billingqe/data/**
      - billingqe/config/**
      - billingqe/tests/runners/**
      - billingqe/tests/features/**
      - billingqe/tests/steps/**
      - billingqe/pages/**
      - billingqe/fixtures/**
      - billingqe/pytest.ini
      - billingqe/requirements.txt
    exclude:
      - billingqe/docs/**
      - '*.md'
```

---

## Pipeline Stages and Steps

| Step | Purpose |
|------|---------|
| `UsePythonVersion@0` | Pin Python 3.11 on the agent |
| `pip install -r requirements.txt` | Install all test dependencies |
| `playwright install chromium` | Download Chromium browser binary |
| `pytest tests/runners/ -m regression` | Execute the regression suite |
| `PublishTestResults@2` | Publish JUnit XML to Azure DevOps Tests tab |
| `PublishBuildArtifacts@1` | Attach HTML/Allure reports as build artifacts |

---

## Agent Pool Requirements

| Requirement | Details |
|------------|--------|
| Pool name | `ubuntu2204-qa` |
| OS | Ubuntu 22.04 |
| Python | 3.11 (via `UsePythonVersion`) |
| Display | Not required — headless mode enforced via `CI=true` |
| Network | Must reach `https://app-billing-ui-test.azurewebsites.net/` |

For **Windows agents**, change `Scripts\activate` path and Playwright binary accordingly.

---

## Secret Variables Configuration

Never store credentials in the YAML file. Use **Azure DevOps variable groups** or **pipeline secret variables**:

1. Go to **Azure DevOps** → **Pipelines** → **Library**
2. Create a variable group named `billing-qa-credentials`
3. Add variables:
   - `BILLING_USERNAME` — mark as **secret**
   - `BILLING_PASSWORD` — mark as **secret**
4. Link the group to the pipeline under **Variables** → **Variable groups**

Or define them directly in the pipeline UI under **Edit** → **Variables** → **Add** (enable the lock icon to make them secret).

---

## Artifact Publishing

The pipeline publishes two artifacts after every run:

| Artifact | Contents | Location |
|----------|---------|----------|
| `billing-test-reports` | HTML report, Allure results, pytest.log | `reports/` |
| Test Results (Azure tab) | JUnit XML parsed by DevOps | `reports/**/junit.xml` |

To download artifacts: **Pipeline run** → **Artifacts** → `billing-test-reports`.

To generate and view the Allure report locally after download:
```bash
allure serve <downloaded-path>/allure-results
```

---

## Running the Pipeline Manually

1. Go to **Azure DevOps** → **Pipelines** → `Billing-QE`
2. Click **Run pipeline**
3. Select branch (`main` or feature branch)
4. Optionally override variables
5. Click **Run**

To run a specific marker only, override the `pytest` command in a custom pipeline run (or use a pipeline parameter for `PYTEST_MARKERS`).

---

## Scheduled Execution

| Schedule | Time (UTC) | Time (PST) | Branch |
|----------|-----------|-----------|--------|
| Daily regression | 8:30 AM | 12:30 AM | `main` |

Schedule can be modified in `prd_sgm.yml` by editing the `cron` expression:

```yaml
schedules:
  - cron: "0 14 * * 1-5"   # 2:00 PM UTC, Mon–Fri
```

---

## Adding New Test Coverage to the Pipeline

When new runner files or features are added:

1. **No pipeline changes needed** if the new tests share the `regression` marker and live under `tests/runners/`
2. **Add path trigger** (if CI trigger is enabled) to include the new data/config/feature paths
3. **Increase `timeoutInMinutes`** if the new tests significantly extend the run duration
4. **Update artifact paths** if new report directories are added

---

*Last updated: May 2026*
