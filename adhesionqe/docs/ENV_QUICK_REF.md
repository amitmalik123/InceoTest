# Quick Environment Reference

## Switch Environments (PowerShell)

```powershell
# Test11 (Default)
$env:TEST_ENV = "test11"
pytest tests/ui/test_roth_conversion_cucumber.py -v

# Test12
$env:TEST_ENV = "test12"
pytest tests/ui/test_roth_conversion_cucumber.py -v

# Silo
$env:TEST_ENV = "silo"
pytest tests/ui/test_roth_conversion_cucumber.py -v

# Prod
$env:TEST_ENV = "prod"
pytest tests/ui/test_roth_conversion_cucumber.py -v
```

## Environment URLs

| Env | URL |
|-----|-----|
| test11 | https://test11.ewealthmanager.com/ |
| test12 | https://test12.ewealthmanager.com/ |
| silo | https://silo.ewealthmanager.com/ |
| prod | https://wrmqa.schwabplan.com/ |

## Files

- `config/env.test11.yaml` - Test11 config
- `config/env.test12.yaml` - Test12 config
- `config/env.silo.yaml` - Silo config
- `config/env.prod.yaml` - Prod config

## In Code

```python
from utils.settings import Settings

# Specific environment
settings = Settings(env='test12')

# Using environment variable
import os
env = os.getenv('TEST_ENV', 'test11')
settings = Settings(env=env)

# Access values
base_url = settings.base_url
login_url = settings.login_url
```
