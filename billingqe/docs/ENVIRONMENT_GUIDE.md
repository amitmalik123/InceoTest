# Environment Guide

> **Configuration, Credentials, and Environment Management**

---

## Table of Contents

1. [Environment Overview](#environment-overview)
2. [Configuration Files](#configuration-files)
3. [Credential Management](#credential-management)
4. [Environment Variables](#environment-variables)
5. [Multiple Environments](#multiple-environments)
6. [CI/CD Environment Setup](#cicd-environment-setup)
7. [Config Loading Priority](#config-loading-priority)

---

## Environment Overview

The Billing SGM test suite currently targets:

| Environment | Base URL | Usage |
|-------------|---------|-------|
| QA | `https://app-billing-ui-test.azurewebsites.net/` | Default — all regression runs |

Config and credentials are separated into YAML files so URLs and credentials can be updated independently.

---

## Configuration Files

```
config/billing/platformrevenuedashboard/strategistgroupmodel/
├── env.qa.yaml           ← Base URL (committed to source control)
└── env.qa.local.yaml     ← Credentials (git-ignored, local only)
```

### `env.qa.yaml` (committed)

```yaml
application:
  base_url: "https://app-billing-ui-test.azurewebsites.net/"

credentials:
  username: ""
  password: ""
```

The base YAML **never contains real credentials** — usernames and passwords are always blank placeholders.

### `env.qa.local.yaml` (git-ignored — create locally)

```yaml
application:
  base_url: "https://app-billing-ui-test.azurewebsites.net/"

credentials:
  username: "your.email@company.com"
  password: "your_password_here"
```

Create this file locally and **never commit it**. It is listed in `.gitignore`.

---

## Credential Management

### Local Setup

```bash
# Copy base config and add credentials
cp config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.yaml \
   config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.local.yaml

# Edit env.qa.local.yaml with your actual credentials
```

### What to Never Do

- ❌ Never commit credentials to source control
- ❌ Never hardcode credentials in step files or page objects
- ❌ Never log passwords in test output
- ✅ Always use `env.qa.local.yaml` or environment variables

---

## Environment Variables

Environment variables take the **highest priority** and override any YAML values. Use them for CI pipelines and secure environments:

| Variable | Purpose | Example |
|----------|---------|--------|
| `BILLING_BASE_URL` | Override the application URL | `https://app-billing-ui-test.azurewebsites.net/` |
| `BILLING_USERNAME` | Azure AD login username | `qa-automation@company.com` |
| `BILLING_PASSWORD` | Azure AD login password | `<secret>` |
| `TEST_CONFIG_PATH` | Absolute path to a custom config YAML | `/opt/configs/billing-qa.yaml` |
| `CI` | Set to `true` in CI environments | Switches browser to headless mode |

### Setting Variables Locally (Windows)

```powershell
$env:BILLING_USERNAME = "your.email@company.com"
$env:BILLING_PASSWORD = "your_password"
pytest tests/runners/ -q
```

### Setting Variables Locally (macOS/Linux)

```bash
export BILLING_USERNAME="your.email@company.com"
export BILLING_PASSWORD="your_password"
pytest tests/runners/ -q
```

---

## Multiple Environments

To support additional environments (e.g., staging, prod), add a new YAML file:

```bash
# Staging example
cp config/billing/.../env.qa.yaml config/billing/.../env.staging.yaml
# Edit base_url to staging URL
```

Then select it at runtime:
```bash
export TEST_CONFIG_PATH=/path/to/env.staging.yaml
pytest tests/runners/ -q
```

The config loader in `revenue_dashboard_common_steps.py` honours `TEST_CONFIG_PATH` first, then falls back to `env.qa.local.yaml`, then `env.qa.yaml`.

---

## CI/CD Environment Setup

In **Azure Pipelines**, credentials are injected as pipeline secret variables:

1. In Azure DevOps → Pipeline → Edit → Variables
2. Add `BILLING_USERNAME` and `BILLING_PASSWORD` as **secret** variables
3. In `prd_sgm.yml`, they are automatically available as environment variables

```yaml
# prd_sgm.yml (excerpt)
env:
  BILLING_USERNAME: $(BILLING_USERNAME)
  BILLING_PASSWORD: $(BILLING_PASSWORD)
  CI: "true"
```

See [AZURE_PIPELINE_GUIDE.md](AZURE_PIPELINE_GUIDE.md) for the full pipeline setup.

---

## Config Loading Priority

The framework resolves configuration in this order (highest to lowest):

```
1. Environment variable (BILLING_BASE_URL, BILLING_USERNAME, BILLING_PASSWORD)
       ↓ if not set
2. TEST_CONFIG_PATH explicit file
       ↓ if not set
3. env.qa.local.yaml  (deep-merged over base)
       ↓ if not found
4. env.qa.yaml        (base fallback)
```

Both `env.qa.yaml` and `env.qa.local.yaml` are deep-merged per section (`application`, `credentials`). Local values override base values for matching keys.

---

*Last updated: May 2026*
