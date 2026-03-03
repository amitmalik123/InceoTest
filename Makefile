# Makefile for Python Playwright Automation Framework

.PHONY: help install setup test lint format type-check quality clean pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install all dependencies"
	@echo "  make setup          - Setup pre-commit hooks"
	@echo ""
	@echo "Test Execution (By Marker/Tag):"
	@echo "  make smoke          - Run smoke tests"
	@echo "  make critical       - Run critical tests"
	@echo "  make regression     - Run regression tests"
	@echo "  make ach            - Run ACH tests"
	@echo "  make e2e            - Run E2E tests"
	@echo "  make fast           - Run smoke tests (exclude slow)"
	@echo ""
	@echo "Test Execution (By File/Folder):"
	@echo "  make test           - Run all tests"
	@echo "  make test-ui        - Run UI tests"
	@echo "  make test-bdd       - Run BDD tests"
	@echo "  make test-api       - Run API tests"
	@echo "  make test-add-ach   - Run Add ACH test file"
	@echo ""
	@echo "Test Execution (Modes):"
	@echo "  make test-headed    - Run tests in headed mode"
	@echo "  make test-parallel  - Run tests in parallel (auto-detect CPUs)"
	@echo "  make test-debug     - Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run all linters"
	@echo "  make format         - Format code with Black and isort"
	@echo "  make type-check     - Run type checking with mypy"
	@echo "  make quality        - Run all quality checks"
	@echo "  make security       - Run security checks with Bandit"
	@echo ""
	@echo "Reporting:"
	@echo "  make reports        - Generate all reports"
	@echo "  make allure         - Generate Allure report"
	@echo "  make coverage       - Run tests with coverage"
	@echo ""
	@echo "Clean:"
	@echo "  make clean          - Clean up generated files"
	@echo "  make clean-reports  - Clean report files"

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

install:
	pip install --upgrade pip
	pip install -e .
	playwright install chromium

setup: install
	pre-commit install
	@echo "✅ Development environment setup complete!"

# ============================================================================
# TEST EXECUTION BY MARKER/TAG (Primary Method)
# ============================================================================

smoke:
	pytest -m smoke -v --html=reports/smoke_report.html --self-contained-html

critical:
	pytest -m critical -v --html=reports/critical_report.html --self-contained-html

regression:
	pytest -m regression -v --html=reports/regression_report.html --self-contained-html

ach:
	pytest -m add_ach -v --headed --slowmo=500 --html=reports/ach_report.html --self-contained-html

e2e:
	pytest -m e2e -v --html=reports/e2e_report.html --self-contained-html

fast:
	pytest -m "smoke and not slow" -v --html=reports/fast_report.html --self-contained-html

# ============================================================================
# TEST EXECUTION BY FILE/FOLDER
# ============================================================================

test:
	pytest tests/ -v --html=reports/all_tests_report.html --self-contained-html

test-ui:
	pytest tests/ui/ -v --html=reports/ui_tests_report.html --self-contained-html

test-bdd:
	pytest tests/bdd/ -v --html=reports/bdd_tests_report.html --self-contained-html

test-api:
	pytest tests/api/ -v --html=reports/api_tests_report.html --self-contained-html

test-add-ach:
	pytest tests/ui/test_add_ach.py -v --headed --slowmo=500 --html=reports/add_ach_report.html --self-contained-html

test-roth:
	pytest tests/ui/test_roth_conversion_bdd.py -v --headed --slowmo=500 --html=reports/roth_report.html --self-contained-html

# ============================================================================
# TEST EXECUTION MODES
# ============================================================================

test-headed:
	pytest tests/ --headed -v

test-parallel:
	pytest tests/ -n auto -v --html=reports/parallel_report.html --self-contained-html

test-parallel-4:
	pytest tests/ -n 4 -v --html=reports/parallel_4_report.html --self-contained-html

test-debug:
	pytest tests/ -v -s --headed --slowmo=1000

# ============================================================================
# ENVIRONMENT-SPECIFIC TESTS
# ============================================================================

test-test11:
	TEST_ENV=test11 pytest -m test11 -v

test-test12:
	TEST_ENV=test12 pytest -m test12 -v

test-silo:
	TEST_ENV=silo pytest -m silo -v

test-prod:
	TEST_ENV=prod pytest -m "prod and critical" -v

# Format code
format:
	@echo "🎨 Formatting code..."
	black .
	isort .
	@echo "✅ Code formatting complete!"

# Format check (don't modify files)
format-check:
	black --check .
	isort --check-only .

# Linting
lint:
	@echo "🔍 Running linters..."
	flake8 .
	@echo "✅ Linting complete!"

# Pylint
pylint:
	@echo "🔍 Running Pylint..."
	pylint pages utils config fixtures --output-format=colorized

# Type checking
type-check:
	@echo "🔍 Running type checker..."
	mypy .
	@echo "✅ Type checking complete!"

# Security check
security:
	@echo "🔒 Running security checks..."
	bandit -r . -f screen
	@echo "✅ Security check complete!"

# Run all quality checks
quality: format-check lint type-check security
	@echo "✅ All quality checks passed!"

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

# Update pre-commit hooks
pre-commit-update:
	pre-commit autoupdate

# Clean generated files
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf reports/*.html
	rm -rf allure-results/*
	rm -rf traces/*
	@echo "✅ Cleanup complete!"

# Clean all including videos and screenshots
clean-all: clean
	rm -rf reports/videos/*
	rm -rf reports/screenshots/*
	rm -rf screenshots/*
	rm -rf videos/*

# Generate coverage report
coverage:
	pytest --cov=pages --cov=utils --cov=config --cov=fixtures \
		--cov-report=html:reports/coverage \
		--cov-report=term-missing

# Generate all reports
reports: coverage
	@echo "📊 Generating reports..."
	pytest --html=reports/report.html --self-contained-html
	allure generate allure-results --clean -o reports/allure-report
	@echo "✅ Reports generated!"

# Serve Allure report
allure-serve:
	allure serve allure-results

# Run tests in parallel
test-parallel:
	pytest -n auto tests/

# Run tests in parallel with specific workers
test-parallel-4:
	pytest -n 4 tests/

# Run tests with loadscope distribution
test-parallel-loadscope:
	pytest -n auto --dist loadscope tests/

# Run tests with loadfile distribution
test-parallel-loadfile:
	pytest -n auto --dist loadfile tests/

# Run smoke tests in parallel
test-smoke-parallel:
	pytest -n auto -m smoke

# Run with test sharding (shard 1 of 4)
test-shard-1:
	TEST_SHARD_INDEX=0 TEST_SHARD_TOTAL=4 pytest -n auto

# Run with test sharding (shard 2 of 4)
test-shard-2:
	TEST_SHARD_INDEX=1 TEST_SHARD_TOTAL=4 pytest -n auto

# Run with test sharding (shard 3 of 4)
test-shard-3:
	TEST_SHARD_INDEX=2 TEST_SHARD_TOTAL=4 pytest -n auto

# Run with test sharding (shard 4 of 4)
test-shard-4:
	TEST_SHARD_INDEX=3 TEST_SHARD_TOTAL=4 pytest -n auto

# Show test distribution analysis
test-distribution:
	@echo "Analyzing test distribution..."
	pytest --collect-only -q | head -20

# Run parallel examples
test-parallel-examples:
	pytest tests/examples/test_parallel_examples.py -n auto -v

# Install development tools only
install-dev:
	pip install black flake8 mypy pylint isort pre-commit bandit

# Check for outdated packages
check-updates:
	pip list --outdated

# Upgrade all packages
upgrade-packages:
	pip install --upgrade -r requirements.txt

# Create virtual environment
venv:
	python -m venv venv
	@echo "✅ Virtual environment created. Activate with: .\venv\Scripts\Activate.ps1"

# Full CI pipeline
ci: install format-check lint type-check security test
	@echo "✅ CI pipeline complete!"
# SonarQube targets
# Run tests with coverage for SonarQube
test-coverage:
	@echo "🧪 Running tests with coverage..."
	mkdir -p reports
	pytest tests/ \
		--cov=pages \
		--cov=utils \
		--cov=config \
		--cov=fixtures \
		--cov-report=xml:reports/coverage.xml \
		--cov-report=html:reports/htmlcov \
		--junitxml=reports/junit.xml \
		--tb=short \
		-v
	@echo "✅ Coverage reports generated!"

# Run quality tools for SonarQube
quality-reports:
	@echo "📊 Generating quality reports..."
	mkdir -p reports
	flake8 --output-file=reports/flake8-report.txt --format=default pages utils config fixtures features/steps || true
	pylint pages utils config fixtures features/steps --output-format=json --output=reports/pylint-report.json --exit-zero || true
	mypy pages utils config fixtures --config-file=mypy.ini > reports/mypy-report.txt 2>&1 || true
	bandit -r pages utils config fixtures -f json -o reports/bandit-report.json || true
	@echo "✅ Quality reports generated!"

# Run SonarQube analysis (requires SONAR_HOST_URL and SONAR_TOKEN environment variables)
sonar: quality-reports test-coverage
	@echo "🔍 Running SonarQube analysis..."
	@if [ -z "$$SONAR_HOST_URL" ] || [ -z "$$SONAR_TOKEN" ]; then \
		echo "❌ Error: SONAR_HOST_URL and SONAR_TOKEN environment variables must be set"; \
		echo "   Set them using: export SONAR_HOST_URL=<url> SONAR_TOKEN=<token>"; \
		exit 1; \
	fi
	sonar-scanner \
		-Dsonar.projectKey=python-playwright-automation \
		-Dsonar.host.url=$$SONAR_HOST_URL \
		-Dsonar.login=$$SONAR_TOKEN
	@echo "✅ SonarQube analysis complete!"
	@echo "📊 View results at: $$SONAR_HOST_URL/dashboard?id=python-playwright-automation"

# Run SonarQube analysis with local server
sonar-local: quality-reports test-coverage
	@echo "🔍 Running SonarQube analysis (local server)..."
	@if [ -z "$$SONAR_TOKEN" ]; then \
		echo "❌ Error: SONAR_TOKEN environment variable must be set"; \
		echo "   Set it using: export SONAR_TOKEN=<token>"; \
		exit 1; \
	fi
	sonar-scanner \
		-Dsonar.projectKey=python-playwright-automation \
		-Dsonar.host.url=http://localhost:9000 \
		-Dsonar.login=$$SONAR_TOKEN
	@echo "✅ SonarQube analysis complete!"
	@echo "📊 View results at: http://localhost:9000/dashboard?id=python-playwright-automation"

# Run SonarQube analysis using PowerShell script (Windows)
sonar-windows:
	@echo "🔍 Running SonarQube analysis (Windows)..."
	powershell -ExecutionPolicy Bypass -File .\run_sonar_analysis.ps1

# Run SonarQube analysis using PowerShell script (Windows, local server)
sonar-windows-local:
	@echo "🔍 Running SonarQube analysis (Windows, local server)..."
	powershell -ExecutionPolicy Bypass -File .\run_sonar_analysis.ps1 -Local
