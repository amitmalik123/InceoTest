# Code Quality Report

> **Standards, Tooling, and Quality Gates for Billing SGM Automation**

---

## Table of Contents

1. [Quality Standards](#quality-standards)
2. [Static Analysis Tooling](#static-analysis-tooling)
3. [Code Style](#code-style)
4. [Architecture Quality Rules](#architecture-quality-rules)
5. [SonarQube Integration](#sonarqube-integration)
6. [Running Quality Checks](#running-quality-checks)
7. [Quality Gates — Pass/Fail Criteria](#quality-gates)
8. [Improvement Areas](#improvement-areas)

---

## Quality Standards

The Billing QE Framework adheres to the following quality standards:

| Standard | Target |
|----------|-------|
| Code style | PEP 8 (≤4 chars deviation allowed via `black`) |
| Max line length | 120 characters |
| Type annotations | Required on all public page object methods |
| Cyclomatic complexity | ≤15 per function |
| Test isolation | Each test gets a fresh browser context |
| No hardcoded credentials | Enforced via `.gitignore` + code review |
| No hardcoded paths | All paths derived from `__file__` |

---

## Static Analysis Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| `flake8` | PEP 8 linting, unused imports, undefined names | `.flake8` or `setup.cfg` |
| `black` | Auto-formatting | `pyproject.toml` |
| `mypy` | Static type checking | `pyproject.toml` |
| `bandit` | Security vulnerability scanning | `bandit.yaml` |
| `pytest-cov` | Test coverage measurement | `pytest.ini` addopts |
| SonarQube | Centralized quality gate | `sonar-project.properties` |

---

## Code Style

### Formatting (`black`)

All Python files are formatted with `black` (line length 120):

```bash
# Format all files
black .

# Check only (no changes)
black --check .

# Format a specific file
black pages/platformrevenuedashboard/strategistgroupmodel/create_family_page.py
```

### Linting (`flake8`)

```bash
# Run flake8 on all source files
flake8 pages/ tests/ fixtures/ utils/

# Exclude known false positives (wildcard imports in conftest)
flake8 --extend-ignore=F401,F403 tests/conftest.py
```

Current known exceptions:
- `F401` (unused import) and `F403` (wildcard import) are suppressed in `tests/conftest.py` by design — step `import *` is required for pytest-bdd step discovery.

### Type Checking (`mypy`)

```bash
mypy pages/ fixtures/ utils/ --ignore-missing-imports
```

---

## Architecture Quality Rules

### Enforced patterns

| Rule | Where Enforced |
|------|---------------|
| Page objects must not contain `assert` statements | Code review / mypy |
| Step files must not contain Playwright selectors | Code review |
| No credentials in any `.py` file | `.gitignore` + bandit |
| All fixture modules imported via `fixtures/` package | `tests/conftest.py` |
| Feature files must not contain Python | `.feature` extension prevents execution |
| All markers registered before use | `pytest.ini` `--strict-markers` |
| Single `conftest.py` at `tests/` | Structural enforcement |

### Anti-patterns to avoid

| Anti-pattern | Reason |
|-------------|-------|
| Inline `page.locator(...)` in step files | Breaks layer separation |
| Multiple `conftest.py` files in sub-folders | Increases complexity, hard to trace fixture inheritance |
| Hardcoded sleep (`time.sleep(...)`) | Flaky; replace with `wait_for_load_state` or `wait_for_selector` |
| `assert` in page object methods | Page objects express intent, not assertions; use step layer |
| `import *` outside `conftest.py` | Pollutes namespace; explicitly import in all other modules |

---

## SonarQube Integration

SonarQube configuration lives in `sonar-project.properties` at the project root. It provides:

- Centralized quality gate visible to all team members
- Technical debt tracking over time
- Security hotspot detection
- Coverage history

### Key SonarQube Properties

```properties
sonar.projectKey=billingqe
sonar.projectName=Billing QE Automation
sonar.sources=pages,fixtures,utils
sonar.tests=tests
sonar.python.coverage.reportPaths=reports/coverage.xml
sonar.python.xunit.reportPath=reports/platformrevenuedashboard/strategistgroupmodel/junit.xml
sonar.exclusions=reports/**,**/__pycache__/**,**/*.pyc
```

### Running the SonarQube Scan

```bash
# Generate coverage report first
pytest tests/runners/ --cov=pages --cov=fixtures --cov=utils \
       --cov-report=xml:reports/coverage.xml

# Run Sonar scanner
sonar-scanner
```

---

## Running Quality Checks

### Full quality check (local pre-commit)

```bash
# 1. Format check
black --check pages/ fixtures/ tests/ utils/

# 2. Lint
flake8 pages/ fixtures/ utils/ tests/steps/

# 3. Type check
mypy pages/ fixtures/ utils/ --ignore-missing-imports

# 4. Security scan
bandit -r pages/ fixtures/ utils/ -f json -o reports/bandit-report.json

# 5. Test coverage
pytest tests/runners/ --cov=pages --cov=fixtures \
       --cov-report=term-missing --cov-fail-under=80
```

### CI quality checks

In `prd_sgm.yml`, add a quality stage before the test stage:

```yaml
- script: |
    black --check .
    flake8 pages/ fixtures/ utils/ tests/steps/
    bandit -r pages/ fixtures/ -f json -o reports/bandit-report.json
  displayName: Code Quality Gate
  continueOnError: false
```

---

## Quality Gates — Pass/Fail Criteria

| Gate | Threshold | Enforcement |
|------|-----------|------------|
| Test pass rate | 100% on `main` | CI pipeline fails on any test failure |
| `black` formatting | Zero violations | CI quality step |
| `flake8` errors | Zero errors (E/W class) | CI quality step |
| Security (`bandit`) | Zero HIGH severity | CI quality step |
| Coverage | ≥70% on `pages/` | Recommendation (not yet hard-gated) |
| SonarQube gate | Must pass project gate | Configurable per project |

---

## Improvement Areas

The following improvements are tracked for future quality iterations:

| Item | Priority | Status |
|------|---------|--------|
| Add `mypy` to CI pipeline | Medium | Planned |
| Increase test coverage reporting to `utils/` | Low | Planned |
| Hard-gate coverage threshold at 80% | Medium | Planned |
| Enable CI trigger on PR for `main` branch | High | Planned |
| Add pre-commit hooks (`black`, `flake8`) | Medium | Planned |
| Type-annotate all page object public methods | Low | In progress |
| Reduce cyclomatic complexity in `create_family_page.py` | Medium | In progress |

---

*Last updated: May 2026*
