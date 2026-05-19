---
name: 'tsa-constraints'
description: 'AssetMark Target State Architecture (TSA) constraints and compliance rules'
user-invokable: false
---

# TSA Constraints — AssetMark Target State Architecture

This skill defines AssetMark's Target State Architecture (TSA) constraints for Azure services, tech stack, and architectural patterns. All implementations must comply with these rules.

## Tech Stack Constraints

### Languages & Frameworks
- **Backend:** C# with .NET 8+ only
- **Frontend:** TypeScript with React 18+ only
- **Database:** T-SQL for SQL Server / Azure SQL Database
- **No exceptions** — Other languages/frameworks require architecture board approval

### Database Platforms
- **Azure SQL Database** — Primary relational database
- **PostgreSQL (Azure Database for PostgreSQL - Flexible Server)** — For specific workloads
- **Azure Cosmos DB** — For document/NoSQL needs only
- **No self-hosted databases** — Azure PaaS only

## Approved Azure Services

### Compute
- **Azure Container Apps** — Preferred for microservices
- **Azure Functions** — Consumption plan only, for event-driven workloads
- **Azure App Service** — For legacy apps or specific requirements
- **❌ VMs / IaaS** — Prohibited (use PaaS only)

### Data & Storage
- **Azure SQL Database** — Primary relational database
- **PostgreSQL (Azure Flexible Server)** — Approved relational alternative
- **Azure Cosmos DB** — Document/NoSQL database
- **Azure Blob Storage** — Unstructured data storage
- **❌ SQL Server on VMs** — Prohibited (use Azure SQL Database)

### AI & Machine Learning
- **Azure AI Studio** — LLM orchestration and prompt management
- **Azure OpenAI Service** — GPT-4, GPT-4o, embeddings
- **❌ Third-party AI APIs** — Prohibited without security review

### Integration & Messaging
- **Azure Service Bus** — Enterprise messaging (queues, topics)
- **Azure Event Grid** — Event routing
- **Azure API Management** — API gateway and management
- **❌ External message brokers** — Prohibited (RabbitMQ, Kafka on VMs)

### Identity & Secrets
- **Azure AD / Entra ID** — OIDC/OAuth2 only (no SAML)
- **Azure Key Vault** — Mandatory for ALL secrets (connection strings, API keys, certificates)
- **Managed Identities** — Required for service-to-service authentication
- **❌ Shared service accounts** — Prohibited (use managed identities)
- **❌ Hardcoded secrets** — Critical violation

### Monitoring & Logging
- **Application Insights** — Application performance monitoring
- **Azure Monitor** — Infrastructure monitoring
- **Log Analytics** — Centralized logging
- **❌ Third-party APM** — Prohibited without approval

### CI/CD
- **Azure DevOps Pipelines** — Primary CI/CD platform
- **GitHub Actions** — For GitHub-hosted repositories only (this Copilot workflow repo)

## Prohibited Patterns

### ❌ Infrastructure as a Service (IaaS)
- No VMs (use Container Apps, Functions, or App Service)
- No self-managed Kubernetes (use Container Apps)
- No on-premises dependencies

### ❌ Security Violations
- Hardcoded connection strings or secrets in code
- Unencrypted data at rest or in transit
- Public endpoints without authentication
- Missing authorization checks on APIs
- Shared service accounts instead of managed identities

### ❌ Direct Database Access
- Frontend apps must NOT connect directly to databases
- Use API/BFF pattern with backend service layer

### ❌ Legacy Patterns
- No synchronous blocking on async code (`.Result`, `.Wait()`)
- No `async void` (except event handlers)
- No mutable shared state in stateless services

## Required Patterns

### ✅ Security & Identity
- **Managed identities** for all service-to-service authentication
- **Key Vault references** for all secrets and connection strings
- **TLS 1.2+** for all network connections
- **Authorization** on all API endpoints (no anonymous public endpoints)
- **Input validation** on all public-facing APIs

### ✅ Architecture
- **Clean architecture** or hexagonal architecture patterns
- **CQRS with MediatR** for complex domain logic
- **API versioning** via URL path (e.g., `/v1/`, `/v2/`) or header
- **Health check endpoints** on all services (`/health`)

### ✅ Observability
- **Structured logging** with correlation IDs (use `ILogger<T>`)
- **Application Insights** telemetry for all services
- **Distributed tracing** for cross-service calls

### ✅ Data Protection
- **Encryption at rest** for all persistent data
- **Encryption in transit** (TLS 1.2+)
- **PII masking** in logs and error messages
- **Audit logging** for sensitive operations

### ✅ Resilience
- **Retry policies** with exponential backoff (Polly library)
- **Circuit breakers** for external service calls
- **Timeout policies** for all I/O operations
- **Graceful degradation** when dependencies fail

## Unit Test Coverage Standard

> **AssetMark Engineering Standard — Effective Wave 1 Enforcement**

### Coverage Threshold

| Scope | Minimum Required |
|-------|-----------------|
| All new code | **85%** line/branch coverage |
| All modified code | **85%** line/branch coverage |
| Existing legacy code | Exempt until refactored |

### Rationale

- **Quality gate:** 85% coverage is the mandated minimum to ensure new and modified code is adequately tested before merge
- **Consistency:** Uniform enforcement across all Wave 1 teams establishes a shared engineering baseline
- **Wave 1 enforcement:** This standard takes effect as part of the Charlotte quiet launch and applies to all teams onboarded under the NITRO program

### Applicability

- **In scope:** All new code and all code modified in a PR (net-new features, bug fixes, refactors)
- **Out of scope:** Pre-existing legacy code that is not touched in a PR — exempt until the file/module is refactored
- **Measurement:** Coverage is calculated per-PR on the diff; whole-repo coverage is tracked but not gated

### Enforcement

| Phase | Mechanism |
|-------|-----------|
| **Now (Phase 1)** | TSA standard declared; teams responsible for self-enforcement |
| **Phase 2** | CI pipeline gate — PR fails automatically if coverage drops below 85% on changed files |
| **Phase 2** | PR Review Agent flags coverage violations in code review comments |

### Violations

| Severity | Condition |
|----------|-----------|
| 🔴 **Critical** | New code with < 50% coverage merged to main |
| 🟡 **High** | Modified code between 50–84% coverage |
| 🟢 **Medium** | Coverage regression on previously-covered code |

### Exceptions Process

Coverage exceptions follow the standard TSA exceptions process:
1. Document business justification (e.g., infrastructure/config code, generated code)
2. Get architecture board approval
3. Document in ADR

---

## Compliance Verification

When reviewing code or architecture, verify:

1. **Azure Services** — All services used are on the approved list
2. **Prohibited Patterns** — None are present
3. **Required Patterns** — All applicable ones are implemented
4. **Tech Stack** — C# (.NET 8+), TypeScript (React 18+), Azure SQL/PostgreSQL
5. **Secrets Management** — No hardcoded secrets, all use Key Vault
6. **Authentication** — Managed identities for service-to-service, Entra ID for users

## TSA Violation Severity

| Severity | Examples |
|----------|----------|
| 🔴 **Critical** | Hardcoded secrets, unapproved cloud services, IaaS usage, missing authentication |
| 🟡 **High** | Shared service accounts instead of managed identities, missing Key Vault, direct frontend-to-DB |
| 🟢 **Medium** | Missing health checks, incomplete observability, missing retry policies |
| ⚪ **Info** | Recommendations for improved architecture patterns |

## Exceptions Process

If a TSA rule cannot be met:
1. Document the business justification
2. Propose a compensating control
3. Get architecture board approval
4. Document the exception in architecture decision records (ADRs)
