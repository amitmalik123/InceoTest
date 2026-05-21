# Azure Pipeline Guide

CI/CD setup for **salesforceqe**.

## Files

| File | Purpose |
|---|---|
| [azure-pipelines/salesforce.yml](../azure-pipelines/salesforce.yml) | Pipeline entry point — triggers, parameters, stage call |
| [azure-pipelines/templates/team-stage-salesforce.yml](../azure-pipelines/templates/team-stage-salesforce.yml) | Reusable stage: install, run pytest, publish reports |

## Triggers

`salesforce.yml` triggers on pushes and PRs to `develop` / `salesforcefeature`
when any of the following change:

- `salesforceqe/data/salesforce/**`
- `salesforceqe/config/salesforce/**`
- `salesforceqe/tests/features/salesforce/**`
- `salesforceqe/tests/steps/salesforce/**`
- `salesforceqe/pages/salesforce/**`
- `salesforceqe/azure-pipelines/templates/**`
- `salesforceqe/requirements.txt`

## Manual run parameters

| Parameter | Values | Default |
|---|---|---|
| `environment` | `monarchqa`, `monarchuat`, `prod`, *(blank)* | *(blank)* |
| `marker` | `smoke`, `regression` | `smoke` |
| `workers` | `1`, `2`, `3`, `4`, `auto` | `1` |
| `browser` | `chromium`, `msedge`, `both` | `chromium` |

These are wired through to the `team-stage-salesforce.yml` template and
ultimately to `pytest -m <marker> -n <workers> --browser <browser>`.

## What the stage does

`team-stage-salesforce.yml` runs on the `ubuntu2204-qa` pool and:

1. Checks out the repo.
2. Promotes pipeline parameters into job variables (`TEST_ENV`, `marker`,
   `workers`, `browser`).
3. Installs Python, the `requirements.txt`, and Playwright browsers.
4. Runs the pytest-bdd suite against `tests/steps/salesforce/`.
5. Publishes:
   - JUnit results
   - Allure results to `reports/salesforce/allure-results`
   - Generated Allure HTML to `reports/salesforce/allure-report`
   - InfluxDB metrics (via [`utils/influx_reporter.py`](../utils/influx_reporter.py))

## InfluxDB reporting

The template defines the InfluxDB endpoint as job variables:

```yaml
INFLUXDB_URL:    'http://azncc03perf.corp.local:8086'
INFLUXDB_ORG:    'MF'
INFLUXDB_BUCKET: 'AutomationData'
INFLUXDB_TOKEN:  '<token>'
```

> The token is currently inlined in the template. For better hygiene, replace
> it with a pipeline secret variable and reference `$(INFLUXDB_TOKEN)`.

## Registering the pipeline in Azure DevOps

1. **Pipelines → New pipeline → Azure Repos Git**.
2. Select the repo, then **Existing Azure Pipelines YAML file**.
3. Pick `/salesforceqe/azure-pipelines/salesforce.yml`.
4. Name it (e.g. `QE-Salesforce`).
5. Save & run.

## Local equivalent

You can mirror what CI does locally:

```powershell
$env:TEST_ENV = "monarchqa"
pytest -m smoke -n 2 --browser chromium `
    --alluredir=reports\salesforce\allure-results `
    --junitxml=reports\junit.xml
```

