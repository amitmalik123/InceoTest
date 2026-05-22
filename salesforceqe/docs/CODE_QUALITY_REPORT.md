# Code Quality

Linters, static analysis, and reporting configured for **salesforceqe**.

## Tools in `requirements.txt`

| Tool | Purpose |
|---|---|
| `flake8` | Style / lint (PEP 8 + pyflakes) |
| `black` | Auto-formatter |
| `mypy` | Optional static type checks |
| `pytest-cov` | Coverage reporting |

`bandit` (security lint) is invoked in CI; install it locally on demand with
`pip install bandit`.

## Running locally

```powershell
# Format
black .

# Lint
flake8 .

# Type-check (optional)
mypy pages utils fixtures

# Security
bandit -r pages utils fixtures tests

# Coverage
pytest -m smoke --cov=pages --cov=utils --cov-report=html
start htmlcov\index.html
```

## Output locations

| Report | Path |
|---|---|
| flake8 | `reports/flake8-report.txt` |
| bandit (JSON) | `reports/bandit-report.json` |
| JUnit | `reports/salesforce/junit/junit-report.xml` |
| pytest-html | `reports/salesforce/pytest-report.html` |
| Coverage HTML | `htmlcov/` |
| Allure | `reports/salesforce/allure-results`, `reports/salesforce/allure-report` |

## SonarQube

[`sonar-project.properties`](../sonar-project.properties) is the entry point
for Sonar scans. Populate it with your project key / organization, e.g.:

```properties
sonar.projectKey=qeautomation-salesforceqe
sonar.projectName=salesforceqe
sonar.sources=pages,utils,fixtures,tests
sonar.python.version=3.11
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.flake8.reportPaths=reports/flake8-report.txt
sonar.python.bandit.reportPaths=reports/bandit-report.json
```

Then run:

```powershell
pytest -m regression --cov=. --cov-report=xml
sonar-scanner
```

## Conventions

- **Black** is the source of truth for formatting — no manual style debates.
- **flake8** must pass before merge; fix or `# noqa` with justification.
- Avoid suppressing **bandit** findings without a comment explaining why the
  pattern is safe in context.
- Aim for ≥ 70% coverage on `pages/` and `utils/`; BDD tests usually drive
  this naturally.
