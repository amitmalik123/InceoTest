
# CoreAPI Automation Framework Architecture

## Purpose
This document provides a technical overview of the architecture, design rationale, extensibility, and technology choices for the CoreAPI Automation Framework.

For onboarding, usage, and feature details, see [README.md](./README.md).

## Strategic Overview
Contract-Driven Development (CDD) centers API development and testing around formal contracts—typically defined using OpenAPI, Swagger, or similar specifications. These contracts serve as the single source of truth for API behavior, enabling faster, more reliable automation and collaboration across teams.

## Key Benefits for Core API Automation

- **Alignment Across Teams**: Contracts act as shared agreements between frontend, backend, and QA teams.
- **Shift-Left Testing**: Enables early validation before implementation.
- **Scalable Automation**: Test cases are generated directly from contracts.
- **Reduced Regression Risk**: Automated checks catch breaking changes early.
- **Improved Governance**: Enforces standards, versioning, and documentation.

---

## Architectural Overview
The framework is designed for:
- Protocol-agnostic API automation (REST, SOAP, GraphQL, gRPC, and more)
- Modular, pluggable components for clients, loaders, validators, and reporters
- Easy extensibility for new protocols, validation logic, and reporting formats
- Support for dynamic test case generation and AI augmentation

## Key Capabilities of the Framework

- **Multi-protocol support**: REST, GraphQL, SOAP, gRPC, and more
- **Database integration**: MSSQL, PostgreSQL, MongoDB, CosmosDB, SQLite, InfluxDB with Azure AD authentication support
- **Static and dynamic test case management**: OpenAPI/Swagger/Postman imports with auto-generation
- **Data-driven and hybrid testing**: CSV-based test data with Jinja2 templating
- **Modular test execution**: Pluggable test_helpers modules for separation of concerns
- **Centralized configuration**: Environment-specific configs with multiple API endpoints and DB connections
- **Rich reporting**: Allure, JUnit, JSON, HTML, and custom reports
- **Performance/load testing**: Built-in Locust integration with framework clients, validators, and automatic report archiving
- **Real-time monitoring**: InfluxDB integration for time-series metrics with Grafana dashboards
- **Security scanning**: Bandit and Safety integration for vulnerability detection
- **Modular, pluggable design**: Easy extension for new protocols, validators, and reporters
- **Azure AD authentication**: Passwordless authentication for PostgreSQL and Azure APIs
- **Optional AI/LLM integration**: For test generation and validation

---

### Directory Structure (High-Level)
```
core-api-automation/
├── .env                     # Environment variables configuration
├── .gitignore               # Git ignore patterns
├── config/                  # Configuration files (environment-specific YAML configs)
│   ├── config.yaml          # Default/local configuration
│   ├── config.example.yaml  # Example configuration template
│   ├── config.TSADEV.yaml   # TSADEV environment config
│   ├── config.T12.yaml      # T12 environment config
│   ├── config.T11.yaml      # T11 environment config
│   ├── config.T10.yaml      # T10 environment config
│   └── config.aks.yaml      # AKS environment config
├── framework/               # Core framework modules
│   ├── api_common_definitions.json # Common API definitions and schemas
│   ├── clients/             # Multi-protocol clients
│   │   ├── api_client.py    # Enhanced REST API client with factory pattern
│   │   ├── azure_auth.py    # Azure AD authentication utilities
│   │   ├── db_client.py     # Database clients (MSSQL, PostgreSQL, MongoDB, CosmosDB, SQLite, InfluxDB)
│   │   ├── graphql_client.py # GraphQL client
│   │   ├── grpc_client.py   # gRPC client
│   │   ├── soap_client.py   # SOAP client
│   │   └── README.md        # Client documentation
│   ├── test_helpers/        # Modular test execution managers
│   │   ├── __init__.py
│   │   ├── test_case_loader.py      # Load and filter test cases
│   │   ├── test_client_manager.py   # Manage API clients with pooling
│   │   ├── test_context_manager.py  # Handle test context and variables
│   │   ├── test_db_manager.py       # Database operations and validation
│   │   ├── test_payload_manager.py  # Payload templating with Jinja2
│   │   ├── test_result_collector.py # Collect and organize test results
│   │   └── test_validation_manager.py # Response validation and assertions
│   ├── common/              # Common utilities and helpers
│   │   ├── common_functions.py # Shared helper functions
│   │   ├── logger.py        # Centralized logging configuration
│   │   ├── template_utils.py # Jinja2 template rendering utilities
│   │   └── utils.py         # General utility functions
│   ├── loaders/             # Configuration and data loaders
│   │   ├── api_definitions_loader.py # Load OpenAPI/Swagger/Postman definitions
│   │   ├── config_loader.py         # Load environment configs with singleton pattern
│   │   ├── path_loader.py           # Project path resolution utilities
│   │   ├── testcase_loader.py       # Load test case JSON files
│   │   └── testdata_loader.py       # Load CSV test data with templating
│   ├── reporter/            # Reporting utilities
│   │   ├── influx_reporter.py # InfluxDB time-series metrics reporting
│   │   └── reporter.py      # Multi-format report generation (Allure, JUnit, JSON, HTML)
│   ├── validators/          # Response validators
│   │   └── validators.py    # Schema, security, field, and data comparison validation
│   ├── logs/                # Framework log files
│   ├── runner.py            # Test execution orchestrator
│   └── generate_testcases.py # Generate tests from OpenAPI/Swagger/Postman
├── reports/                 # Test execution reports (HTML, JSON, Allure, etc.)
│   ├── YYYYMMDD_HHMMSS/     # Timestamped report folders
│   └── archive/             # Archived old reports
├── templates/               # Templates for testcases and testdata
│   ├── LoadTest_Template.json # Load test template
│   ├── TestCase_Template.json # Test case template
│   ├── TestCase_Enhanced_Reference.md # Enhanced test case reference
│   └── TestCase_Template_README.md # Template documentation
├── testcases_autogenerated/ # Auto-generated testcases (organized by API/spec name)
├── testdata/                # Test data files (JSON test cases, CSV data)
│   ├── addressservice/      # Address service test cases
│   ├── parties/             # Parties service test cases
│   ├── WorkItemNotification/ # WorkItem notification test cases
│   └── [other services]/    # Other service-specific test data
├── tests/                   # Test scripts (pytest integration)
│   └── test_api_generic.py  # Main test runner with fixtures
├── webui/                   # Web UI for framework (optional)
│   ├── app.py               # Flask/Streamlit web application
│   ├── static/              # Static assets (CSS, JS, images)
│   └── templates/           # HTML templates
├── ARCHITECTURE.md          # This file - architecture documentation
├── ARCHITECTURE_DIAGRAM.md  # Architecture diagrams and visualizations
├── conftest.py              # Pytest configuration and fixtures
├── GIT_BEST_PRACTICES.md    # Git workflow and best practices
├── locustfile.py            # Performance/load testing with Locust and framework integration
├── LOCUST_INFLUXDB_INTEGRATION.md # InfluxDB integration documentation for Locust
├── Performance_README.md    # Comprehensive performance testing documentation
├── pytest.ini               # Pytest configuration file
├── README.md                # Main project documentation
├── README.security.md       # Security scanning and best practices
├── requirements.txt         # Python dependencies
├── run_full_suite.ps1       # PowerShell script for full test suite execution
├── run_full_suite.sh        # Bash script for full test suite execution
├── test_config.csv          # Test configuration data
└── azure-pipelines.yml      # Azure DevOps CI/CD pipeline configuration
```

**Key Notes:**
- **Test case generator**: Outputs to `testcases_autogenerated/<API or Spec Name>/` by default
- **Reports**: Automatically organized in timestamped folders with archive management
- **Config files**: Environment-specific YAML configs for different deployment targets
- **Framework modularity**: Clear separation between clients, loaders, validators, reporters, and test helpers
- **Performance testing**: Locust integrated with framework components (clients, validators, InfluxDB)
- **Documentation**: Multiple specialized README files for different aspects (Performance, Security, Architecture)

---

## Design Rationale

- **Python + pytest**: Chosen for maturity, extensibility, and rich ecosystem for API, data, and AI/ML tooling.
- **Modular Structure**: Each protocol/client/validator is a separate module, allowing easy extension and maintenance.
- **Dynamic Test Generation**: Supports static and dynamic test case creation (OpenAPI, Postman, etc.).
- **AI Augmentation**: Designed to allow LLMs for test generation, anomaly detection, and smart validation.
- **CI/CD Friendly**: Integrates with Azure Pipelines, GitHub Actions, and other CI/CD tools.

---

## Extensibility

### Core Components
The framework is designed with modularity and extensibility at its core:

- **API Clients**: Add new protocol clients by extending base classes in `framework/clients/`
- **Database Clients**: Implement new DB clients by extending `DatabaseClient` abstract base class
- **Test Helpers**: Add new test helpers in `framework/test_helpers/` for specialized functionality
- **Validators**: Extend validation logic in `framework/validators/`
- **Reporters**: Add custom report formats in `framework/reporter/`
- **Loaders**: Create new data loaders in `framework/loaders/`

### Test Helpers Module Architecture
The `test_helpers/` module provides a modular, manager-based approach for test execution:

1. **test_case_loader.py**: Discovery, loading, and filtering of test cases from files or directories
2. **test_client_manager.py**: Manages API client pool with support for multiple service endpoints
3. **test_context_manager.py**: Maintains test context, variables, and state across test steps
4. **test_db_manager.py**: Database connection pooling and query execution with multi-DB support
5. **test_payload_manager.py**: Jinja2-based payload templating with context substitution
6. **test_result_collector.py**: Aggregates and organizes test results for reporting
7. **test_validation_manager.py**: Schema validation, data comparison, and custom assertions

### Hooks and Integrations
- **Database Hooks**: Pre- and post-test DB validation supporting MSSQL, PostgreSQL, CosmosDB, MongoDB, SQLite. Azure AD authentication for passwordless database access.
- **Library Hooks**: Custom Python libraries for authentication (Azure AD, OAuth2), data transformation, or external service calls at any test step
- **Observability Hooks**:
  - **InfluxDB**: Send test metrics and timings to InfluxDB for time-series analysis
  - **Grafana**: Visualize test results and metrics via Grafana dashboards
  - **Azure Application Insights**: Distributed tracing, logging, and telemetry
  - **Other Tools**: Prometheus, Datadog, or custom monitoring solutions

Hooks can be implemented as:
- Pre/post actions in test cases
- Decorators for functions/methods
- Plugin modules loaded dynamically
- pytest fixtures in `conftest.py`

This allows deep integration with enterprise observability and monitoring stacks.

---

## Technology Choices

- **pytest**: Test runner and framework
- **Allure**: Reporting
- **Locust**: Performance/load testing
- **Flask**: Web UI/dashboard
- **Jinja2**: Templating for dynamic payloads
- **pydantic**: Data validation (optional)
- **python-dotenv**: Environment variable management

---

## Comparison with Alternatives

| Feature                | Python + pytest         | Node.js + Playwright      |
|------------------------|------------------------|---------------------------|
| REST/GraphQL/SOAP      | Native, mature         | REST/GraphQL only         |
| Protocol Extensibility | Easy (many libs)       | HTTP/WS only              |
| AI/ML Integration      | Best-in-class          | Limited                   |
| Data Science           | Best-in-class          | Limited                   |
| Load Testing           | Locust, native         | 3rd party, less mature    |
| Dashboarding           | Flask, Jupyter, etc.   | 3rd party, less mature    |
| CI/CD Integration      | Excellent              | Good                      |
| Community/Plugins      | Large, mature          | Growing                   |
| Modularity             | Excellent              | Good                      |
| Learning Curve         | Easy                   | Easy                      |
| Dependency Management  | Robust, pip-tools, CI  | Good, npm/yarn            |

---

## Conclusion
The CoreAPI Automation Framework is architected for scalability, maintainability, and extensibility, with a focus on protocol diversity, AI-readiness, and robust CI/CD integration. Python + pytest is the optimal stack for these goals.
