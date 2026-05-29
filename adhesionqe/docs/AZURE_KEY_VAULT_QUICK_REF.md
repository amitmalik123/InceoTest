# Quick Reference: Azure Key Vault Setup

## 1. Install Packages
```bash
pip install azure-identity azure-keyvault-secrets
```

## 2. Configure .env
```bash
AZURE_KEY_VAULT_URL=https://your-keyvault-name.vault.azure.net/
```

## 3. Authenticate
```bash
# Local dev
az login

# CI/CD - add to .env
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx
AZURE_TENANT_ID=xxx
```

## 4. Secret Naming Convention
`{env}-{service}-{type}`
- test11-api-auth-token
- test11-azure-sql-username
- test11-azure-sql-password

## 5. Upload Secrets
```bash
az keyvault secret set --vault-name YOUR_VAULT \
  --name test11-api-auth-token \
  --value "your-token"
```

## 6. Usage
```python
from utils.settings import Settings
settings = Settings(env="test11")
token = settings.api_auth_token  # Auto-fetches from Key Vault
```

## Required Secrets for test11:
- `test11-api-auth-token`
- `test11-azure-sql-username`
- `test11-azure-sql-password`
- `test11-sql-server-username`
- `test11-sql-server-password`
