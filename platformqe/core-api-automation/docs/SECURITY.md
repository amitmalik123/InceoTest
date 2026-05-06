# Security Scanning with Bandit and Safety

This project uses Bandit and Safety to help identify security issues and vulnerable dependencies in Python code.

## Bandit: Python Security Linter

Bandit scans your Python source code for common security issues.

### Installation
```
pip install bandit
```

### Usage
Scan the `framework/` and `tests/` directories:
```
bandit -r framework/ tests/ --skip B101
```
- `-r`: Recursively scan directories
- `--skip B101`: Skip assert usage warnings (optional)

### Output
Bandit will print a summary of issues found, including severity and location.

## Safety: Dependency Vulnerability Scanner

Safety checks your installed Python packages for known security vulnerabilities.

### Installation
```
pip install safety
```

### Usage
Check your dependencies:
```
safety check --full-report
```
- `--full-report`: Show detailed vulnerability information

### Output
Safety will list any vulnerable packages and provide remediation advice.

## Best Practices
- Run Bandit and Safety before every release or CI/CD pipeline.
- Fix or suppress issues as appropriate.
- Keep dependencies up to date.

## References
- [Bandit Documentation](https://bandit.readthedocs.io/en/latest/)
- [Safety Documentation](https://pyup.io/safety/)
