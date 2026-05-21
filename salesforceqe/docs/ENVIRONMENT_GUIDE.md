# Environment Guide

How the **salesforceqe** suite picks a target Salesforce org and authenticates.

## Supported environments

The Azure pipeline ([salesforce.yml](../azure-pipelines/salesforce.yml))
exposes these `environment` values:

| Value | Purpose |
|---|---|
| `monarchqa` | Monarch Console QA sandbox |
| `monarchuat` | Monarch Console UAT sandbox |
| `prod` | Production (read-only / smoke only) |
| *(blank)* | Falls back to `credentials.json` defaults |

Locally, set the same value via:

```powershell
$env:TEST_ENV = "monarchqa"
pytest -m smoke
```

## Credentials file

Credentials live in [data/salesforce/credentials.json](../data/salesforce/credentials.json):

```json
{
  "user_credentials": [
    {
      "environment": "https://<your-org>--pwcqa.sandbox.my.salesforce.com/",
      "username": "<user>@<domain>.pwcqa",
      "password": "<password>"
    },
    {
      "environment": "https://<your-org>--qa.sandbox.my.salesforce.com/",
      "username": "<user>@<domain>.fscqa",
      "password": "<password>"
    }
  ]
}
```

The login page object selects the entry whose `environment` URL matches the
target sandbox.

### Security notes

- **Do not commit real production credentials.** Use sandbox users only.
- In CI, override the file with a pipeline secret variable or replace the
  contents before tests run.
- Consider rotating any password that has been committed to source control.
- For local development, prefer a `credentials.local.json` that is
  `.gitignore`-d and copied into place at runtime.

## Authentication state reuse

[`utils/auth_state_manager.py`](../utils/auth_state_manager.py) provides helpers
to persist and restore Playwright's `storage_state` so individual tests can
skip the full login flow:

```python
from utils.auth_state_manager import save_state, load_state

save_state(context, "auth/monarchqa.json")
# next run:
context = browser.new_context(storage_state="auth/monarchqa.json")
```

This is especially useful when the org requires MFA — sign in once
interactively and reuse the saved state for subsequent automated runs.

## MFA / TOTP

If your sandbox user has MFA enabled, prefer one of:

1. Use a service user with **MFA disabled** for automation (sandbox only).
2. Generate TOTP codes in the login page object using `pyotp` and the user's
   shared secret stored as a pipeline secret.
3. Pre-authenticate once and reuse the saved `storage_state` (see above).

## Settings YAML (optional)

[`utils/settings.py`](../utils/settings.py) supports per-environment YAML
config files such as `config/env.monarchqa.yaml` for `base_url`, `timeout`,
`browser`, `viewport`, etc. The `config/` folder is currently empty — add a
YAML file when you need environment-specific application settings beyond the
URL/credentials in `credentials.json`.
