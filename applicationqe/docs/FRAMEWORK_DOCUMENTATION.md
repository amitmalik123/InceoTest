# UI Automation Framework - Updated Folder Structure

This document reflects the current project layout after restructuring:
- Removed the intermediate `tests/bdd` folder.
- Moved `features` and `steps` under `tests`.
- Kept `fixtures` at the project root.
- Added domain subfolders with nested `STP` children.

## Current Structure

```text
QEAutomation_Application/
|
|-- config/
|   |-- env.prod.yaml
|   |-- env.qa.yaml
|   |-- env.silo.yaml
|   |-- env.test11.yaml
|   |-- env.test12.yaml
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- data/
|   |-- test_data.prod.csv
|   |-- test_data.qa.csv
|   |-- test_data.silo.csv
|   |-- test_data.test11.csv
|   |-- test_data.test12.csv
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- queries/
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- pages/
|   |-- __init__.py
|   |-- base_page.py
|   |-- login_page.py
|   |-- clients_page.py
|   |-- account_list_page.py
|   |-- account_detail_page.py
|   |-- roth_conversion_page.py
|   |-- tracking_center_page.py
|   |-- ewm/
|   |-- baw/
|   \-- navbar/
|
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- ui/
|   |   \-- test_roth_conversion_cucumber.py
|   |-- features/
|   |   |-- roth_conversion.feature
|   |   |-- naw/
|   |   |-- baw/
|   |   |-- stp/
|   |   |   |-- stp-ict/
|   |   |   \-- stp-journals/
|   |   |-- oam/
|   |   |-- model-management/
|   |   |-- proposal/
|   |   \-- full-regression/
|   \-- steps/
|       |-- test_roth_conversion_steps.py
|       |-- naw/
|       |-- baw/
|       |-- stp/
|       |   |-- stp-ict/
|       |   \-- stp-journals/
|       |-- oam/
|       |-- model-management/
|       |-- proposal/
|       \-- full-regression/
|
|-- utils/
|   |-- __init__.py
|   |-- logger.py
|   |-- settings.py
|   \-- influx_reporter.py
|
|-- reports/
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   |-- stp-journals/
|   |   |   |-- allure-results/
|   |   |   \-- allure-report/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|   |-- pytest_report.html
|   |-- junit.xml
|   |-- flake8-report.txt
|   |-- pylint-report.txt
|   \-- bandit-report.json
|
|-- test-results/
|-- fixtures/
|-- src/
|   \-- testScript/
|-- tools/
|
|-- azurePipeline.yaml
|-- pyproject.toml
|-- requirements.txt
|-- run_tests.bat
|-- generate_allure_report.bat
|-- sonar-project.properties
|
\-- docs/
	|-- README.md
	|-- FRAMEWORK_DOCUMENTATION.md
	|-- BDD_GUIDE.md
	|-- TESTING_GUIDE.md
	|-- ENVIRONMENT_GUIDE.md
	|-- DEBUGGING_GUIDE.md
	|-- AZURE_PIPELINE_GUIDE.md
	|-- TAG_USAGE_GUIDE.md
	|-- CODE_QUALITY_REPORT.md
	\-- SETUP_SUMMARY.md
```

## Notes

- `stp-ict` and `stp-journals` are nested under `stp` in each applicable folder.
- `full-regression` folder contains cross-domain regression test assets.
- All markdown documentation files are kept in the `docs` folder.
