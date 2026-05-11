# Code Quality Guide

This guide explains the code quality tools configured in this framework.

## 🛠️ Tools Configured

### 1. **Black** - Code Formatter
Automatically formats Python code to ensure consistent style.

**Configuration**: `pyproject.toml`
- Line length: 100 characters
- Target Python: 3.8+

**Usage**:
```powershell
# Format all files
black .

# Check without modifying
black --check .

# Format specific file
black path/to/file.py
```

### 2. **isort** - Import Organizer
Sorts and organizes Python imports automatically.

**Configuration**: `pyproject.toml`
- Compatible with Black
- Groups: stdlib, third-party, first-party, local

**Usage**:
```powershell
# Sort all imports
isort .

# Check without modifying
isort --check-only .

# Sort specific file
isort path/to/file.py
```

### 3. **Flake8** - Linter
Checks code for style violations and potential errors.

**Configuration**: `.flake8`
- Max line length: 100
- Max complexity: 10
- Includes plugins for enhanced checks

**Usage**:
```powershell
# Lint all files
flake8 .

# Lint specific file
flake8 path/to/file.py

# Show statistics
flake8 --statistics .
```

### 4. **Mypy** - Type Checker
Performs static type checking for Python code.

**Configuration**: `mypy.ini`
- Checks type hints
- Enforces type safety

**Usage**:
```powershell
# Type check all files
mypy .

# Type check specific file
mypy path/to/file.py

# Generate HTML report
mypy --html-report reports/mypy .
```

### 5. **Pre-commit** - Git Hooks
Automatically runs quality checks before commits.

**Configuration**: `azure-pipelines/.pre-commit-config.yaml`
- Runs all formatters and linters
- Prevents bad code from being committed

**Setup**:
```powershell
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (if needed)
git commit --no-verify
```

### 7. **Bandit** - Security Linter
Scans code for security vulnerabilities.

**Configuration**: `.bandit`
- Detects security issues
- Checks for common vulnerabilities

**Usage**:
```powershell
# Scan all files
bandit -r .

# Generate JSON report
bandit -r . -f json -o reports/bandit_report.json

# Scan specific directory
bandit -r pages/
```

## 📋 Quick Start

### Installation
```powershell
# Install all code quality tools
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Daily Workflow
```powershell
# Before committing, run all checks
pre-commit run --all-files

# Or run individually
black .
isort .
flake8 .
mypy .
pylint pages utils config
bandit -r .
```

### VS Code Integration

Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.rulers": [100],
        "editor.tabSize": 4
    }
}
```

## 🎯 Code Quality Standards

### Type Hints
Always add type hints to functions:

```python
from typing import Optional, List, Dict

def process_data(
    data: List[Dict[str, str]],
    validate: bool = True
) -> Optional[str]:
    """Process data with validation."""
    # Implementation
    return result
```

### Docstrings
Use Google-style docstrings:

```python
def calculate_total(items: List[float], tax_rate: float) -> float:
    """
    Calculate total with tax.

    Args:
        items: List of item prices
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If tax_rate is negative
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

### Import Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import Optional, List

# Third-party imports
import pytest
from playwright.sync_api import Page, expect

# Local imports
from config.config import Config
from pages.base_page import BasePage
from utils.logger import logger
```

## 🚫 Common Issues and Fixes

### Black and Flake8 Conflicts
Already configured to work together. E203, W503, E501 are ignored in Flake8.

### Pre-commit Fails
```powershell
# Update pre-commit
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

### Mypy Import Errors
Missing type stubs are ignored per module in `mypy.ini`.

## 📊 CI/CD Integration

Add to your CI pipeline:

```yaml
# Example GitHub Actions
- name: Code Quality Checks
  run: |
    pip install -r requirements.txt
    black --check .
    isort --check-only .
    flake8 .
    mypy .
    pylint pages utils config
    bandit -r .
```

## 🔧 Customization

### Adjust Line Length
Update in all config files:
- `pyproject.toml` (Black, isort)
- `.flake8`
- `.pylintrc`

### Disable Specific Rules
- **Flake8**: Add to `ignore` in `.flake8`
- **Pylint**: Add to `disable` in `.pylintrc`
- **Mypy**: Add `# type: ignore` comments

### Skip Files
Update `exclude` sections in each config file.

## 📚 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## 🎓 Best Practices

1. **Run formatters before linters**: `black` → `isort` → `flake8`
2. **Fix issues incrementally**: Don't try to fix everything at once
3. **Use pre-commit hooks**: Catch issues before they reach the repository
4. **Add type hints gradually**: Start with new code, then refactor old code
5. **Document exceptions**: Use `# noqa` or `# type: ignore` sparingly with comments
6. **Keep configs updated**: Review and update tools regularly

## 🐛 Troubleshooting

### Pre-commit Hook Fails
```powershell
# See what failed
pre-commit run --all-files --verbose

# Run specific hook
pre-commit run black --all-files
```

### Tools Not Found
```powershell
# Reinstall in virtual environment
pip install --upgrade -r requirements.txt
```

### Performance Issues
```powershell
# Run on changed files only
pre-commit run

# Skip slow hooks temporarily
SKIP=mypy git commit -m "message"
```
