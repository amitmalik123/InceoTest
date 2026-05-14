# Azure Key Vault Integration Guide

## Overview
Secrets are now managed in Azure Key Vault instead of being hardcoded in YAML files. This provides better security and centralized secret management.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create/update `.env` file in project root:
```bash
AZURE_KEY_VAULT_URL=https://your-keyvault-name.vault.azure.net/
```

### 3. Azure Authentication
The framework uses `DefaultAzureCredential` which tries these methods in order:
1. **Environment Variables** (Service Principal)
2. **Managed Identity** (when running in Azure)
3. **Azure CLI** (local development)
4. **Visual Studio Code** (local development)

#### For Local Development (Recommended):
```bash
# Login via Azure CLI
az login
```

#### For CI/CD (Service Principal):
Add to `.env`:
```bash
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 4. Store Secrets in Key Vault

#### Secret Naming Convention
Format: `{environment}-{service}-{secret-type}`

Examples:
- `test11-api-auth-token`
- `test11-azure-sql-username`
- `test11-azure-sql-password`
- `test11-sql-server-username`
- `test11-sql-server-password`

#### Using Azure Portal:
1. Go to your Key Vault
2. Navigate to Secrets
3. Click "+ Generate/Import"
4. Enter secret name and value

#### Using Azure CLI:
```bash
# Set API auth token
az keyvault secret set --vault-name your-keyvault-name \
  --name test11-api-auth-token \
  --value "your-token-value"

# Set database credentials
az keyvault secret set --vault-name your-keyvault-name \
  --name test11-azure-sql-username \
  --value "ishan.mehta@assetmark.com"

az keyvault secret set --vault-name your-keyvault-name \
  --name test11-azure-sql-password \
  --value "your-password"

az keyvault secret set --vault-name your-keyvault-name \
  --name test11-sql-server-username \
  --value "svct_samedaytrading_app"

az keyvault secret set --vault-name your-keyvault-name \
  --name test11-sql-server-password \
  --value "your-password"
```

## Usage

### Automatic Integration
The `Settings` class automatically fetches secrets from Key Vault:

```python
from utils.settings import Settings

settings = Settings(env="test11")

# These now fetch from Key Vault
api_token = settings.api_auth_token
db_user = settings.azure_sql_username
db_pass = settings.azure_sql_password
```

### Direct Key Vault Access
```python
from utils.azure_key_vault import get_secret, AzureKeyVaultClient

# Simple function call
password = get_secret("test11-azure-sql-password")

# Using the client directly
vault = AzureKeyVaultClient()
token = vault.get_secret("test11-api-auth-token")

# Batch fetch
secrets = vault.get_secrets([
    "test11-azure-sql-username",
    "test11-azure-sql-password"
])
```

## Fallback Behavior
If Key Vault is unavailable or secret not found, the framework falls back to values in YAML (if present). This allows:
- **Local development** without Key Vault access
- **Gradual migration** of secrets
- **Testing** with dummy values

## Security Best Practices

### ✅ DO:
- Store ALL credentials in Key Vault
- Use environment-specific secret names
- Set `.env` in `.gitignore`
- Use managed identity in production
- Rotate secrets regularly

### ❌ DON'T:
- Commit secrets to YAML files
- Share `.env` files
- Hardcode credentials
- Use same secrets across environments

## Key Vault Permissions

Ensure the identity running tests has these permissions:
- **Get** - Read secret values
- **List** - List available secrets (optional)

Set via Azure Portal → Key Vault → Access Policies

## Troubleshooting

### "Key Vault client not initialized"
- Check `AZURE_KEY_VAULT_URL` in `.env`
- Verify authentication (run `az login`)

### "Failed to retrieve secret"
- Verify secret exists in Key Vault
- Check secret name matches convention
- Ensure proper access permissions

### "DefaultAzureCredential failed"
- Run `az login` for local development
- For CI/CD, verify service principal credentials

## Migration Checklist

- [x] Install Azure SDK packages
- [x] Create Key Vault utility
- [x] Update Settings class
- [x] Clear secrets from YAML
- [ ] Create Key Vault in Azure
- [ ] Upload secrets to Key Vault
- [ ] Configure `.env` with vault URL
- [ ] Test locally
- [ ] Configure CI/CD authentication
- [ ] Update other environment files (test12, qa, prod, silo)

## Example: Complete Flow

```python
# 1. Settings automatically uses Key Vault
from utils.settings import Settings
settings = Settings(env="test11")

# 2. Database connection uses Key Vault secrets
from utils.database import DatabaseManager
db = DatabaseManager(settings)
db.connect_azure_sql()  # Uses username/password from Key Vault

# 3. API calls use Key Vault tokens
import requests
headers = {"Authorization": settings.api_auth_token}  # From Key Vault
response = requests.get(url, headers=headers)
```

## CI/CD Integration

### Azure DevOps:
```yaml
variables:
  - group: key-vault-secrets  # Link to Azure Key Vault

steps:
  - script: |
      echo "AZURE_KEY_VAULT_URL=$(KeyVaultUrl)" > .env
      echo "AZURE_CLIENT_ID=$(AZURE_CLIENT_ID)" >> .env
      echo "AZURE_CLIENT_SECRET=$(AZURE_CLIENT_SECRET)" >> .env
      echo "AZURE_TENANT_ID=$(AZURE_TENANT_ID)" >> .env
    displayName: 'Configure Environment'
```

### GitHub Actions:
```yaml
env:
  AZURE_KEY_VAULT_URL: ${{ secrets.AZURE_KEY_VAULT_URL }}
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```
