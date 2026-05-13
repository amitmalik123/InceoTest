---
name: 'assetmark-stack'
description: 'AssetMark technology stack reference — languages, frameworks, databases, Azure services, architecture patterns, and testing standards'
user-invokable: false
---

# AssetMark Technology Stack

This skill defines the complete technology stack, architecture patterns, and development standards for AssetMark applications.

## Languages & Frameworks

### Backend: C# with .NET 8+
- **Version:** .NET 8 or later (LTS releases preferred)
- **Language Features:**
  - Nullable reference types enabled
  - Async/await throughout
  - Records for DTOs and value objects
  - Pattern matching where appropriate
- **Project Structure:** Solution per bounded context with layered architecture

### Frontend: TypeScript with React 18+
- **Version:** React 18+ with TypeScript 5+
- **Language Features:**
  - Strict mode enabled (`"strict": true`)
  - No `any` types (use `unknown` with type guards)
  - Functional components with hooks only (no class components)
- **Build Tool:** Vite (preferred) or Create React App
- **State Management:** React Context + hooks or Zustand (avoid Redux unless justified)

### Database: T-SQL
- **Primary:** T-SQL for Azure SQL Database
- **PostgreSQL:** PL/pgSQL for PostgreSQL workloads
- **Query Patterns:** Stored procedures for complex logic, parameterized queries always

## Databases

### Azure SQL Database (Primary)
- **Edition:** Standard (S2+) or Premium for production
- **Features:**
  - Geo-replication for DR
  - Automated backups (point-in-time restore)
  - Always Encrypted for sensitive columns (optional)
  - Row-level security for multi-tenant scenarios
- **Access:** Managed Identity authentication required (no SQL auth in production)

### PostgreSQL (Azure Database for PostgreSQL - Flexible Server)
- **Use Cases:** Open-source requirement, JSONB storage needs, PostGIS geospatial
- **Version:** PostgreSQL 14+ (Flexible Server)
- **Access:** Managed Identity or Azure AD authentication

### Cosmos DB (NoSQL)
- **Use Cases:** Document storage, high-scale read/write, global distribution
- **API:** Core (SQL API) preferred
- **Consistency:** Session consistency (default) unless stronger required

## Cloud Platform: Azure PaaS Only

### Compute
- **Azure Container Apps** — Microservices, auto-scaling, serverless containers
- **Azure Functions** — Event-driven workloads (Consumption plan)
- **Azure App Service** — Legacy apps, web apps with minimal containerization effort
- **❌ VMs / IaaS** — Not allowed (use PaaS services only)

### AI & Machine Learning
- **Azure AI Studio** — Prompt flow, evaluation, LLM orchestration
- **Azure OpenAI Service** — GPT-4, GPT-4o, GPT-3.5-turbo, embeddings
- **Models:** `gpt-4o` (default), `gpt-4-turbo` (complex reasoning), `text-embedding-3-small` (embeddings)
- **Prompt Engineering:** Use system/user message separation, structured outputs

### Identity & Access
- **Azure AD / Entra ID** — User authentication via OIDC/OAuth2
- **Managed Identities** — Service-to-service authentication (system-assigned preferred)
- **Authentication Libraries:**
  - C#: Microsoft.Identity.Web
  - TypeScript: @azure/msal-browser, @azure/msal-react

### Secrets Management
- **Azure Key Vault** — All secrets, connection strings, API keys, certificates
- **Access:** Managed Identity with least-privilege RBAC
- **Configuration:** Use `@Microsoft.KeyVault(SecretUri=...)` in appsettings.json

### Integration & Messaging
- **Azure Service Bus** — Reliable messaging (queues, topics/subscriptions)
- **Azure Event Grid** — Event-driven architectures, reactive systems
- **Azure API Management** — API gateway for external-facing APIs

### Monitoring & Observability
- **Application Insights** — Application telemetry, distributed tracing, log analytics
- **Azure Monitor** — Infrastructure monitoring, alerts
- **Log Analytics** — Centralized logging with Kusto queries
- **Correlation IDs:** Pass through headers for distributed tracing (`X-Correlation-ID`)

## CI/CD

### Azure DevOps Pipelines
- **Pipelines:** `azure-pipelines.yml` in repo root, templates in `pipelines/` directory
- **Secrets:** Store in Azure Key Vault (linked variable groups)
- **Branching:**
  - `main` — Production-ready code
  - `develop` — Integration branch
  - Feature branches: `feature/description` or `feature/AB-12345-description`
- **Pull Requests:** Required for all changes to `main` and `develop` (Azure Repos branch policies)
- **Work Item Linking:** All commits must reference Azure Boards work items (`AB#12345`)

### Deployment
- **Environments:** dev → staging → production
- **IaC:** Bicep templates for Azure resources (preferred) or ARM templates
- **Container Registry:** Azure Container Registry (ACR) with managed identity pull

## Architecture Patterns

### Clean Architecture (Backend)
Organize .NET solutions in layers:

```
Solution.sln
├── Domain/              # Entities, value objects, domain logic
├── Application/         # Use cases, DTOs, interfaces
│   ├── Commands/       # CQRS write operations
│   ├── Queries/        # CQRS read operations
│   └── Validators/     # FluentValidation rules
├── Infrastructure/      # Data access, external services, Azure SDKs
│   ├── Persistence/    # EF Core DbContext, repositories
│   └── Services/       # External API clients, Azure service wrappers
└── API/                # Controllers, middleware, startup
    ├── Controllers/
    └── Program.cs
```

**Key Principles:**
- **Dependency Inversion:** Domain has no dependencies; Application depends on Domain; Infrastructure depends on Application
- **Business logic in Domain/Application** — Not in controllers or infrastructure
- **Interfaces in Application** — Implementations in Infrastructure

### CQRS with MediatR
Use MediatR for request/response pattern:

```csharp
// Command (write operation)
public record CreateAccountCommand(string Name) : IRequest<int>;

public class CreateAccountHandler : IRequestHandler<CreateAccountCommand, int>
{
    private readonly AppDbContext _db;
    public CreateAccountHandler(AppDbContext db) => _db = db;

    public async Task<int> Handle(CreateAccountCommand request, CancellationToken ct)
    {
        var account = new Account { Name = request.Name };
        _db.Accounts.Add(account);
        await _db.SaveChangesAsync(ct);
        return account.Id;
    }
}

// Controller
[HttpPost]
public async Task<IActionResult> CreateAccount(CreateAccountRequest request)
{
    var command = new CreateAccountCommand(request.Name);
    var id = await _mediator.Send(command);
    return CreatedAtAction(nameof(GetAccount), new { id }, id);
}
```

**Benefits:**
- Clear separation of commands (writes) and queries (reads)
- Testable handlers
- Cross-cutting concerns via MediatR pipeline behaviors (validation, logging, transactions)

### API Design
- **REST conventions** — Use HTTP verbs correctly (GET, POST, PUT, DELETE)
- **Versioning:** URL path versioning (`/api/v1/`, `/api/v2/`)
- **Response format:** JSON with camelCase property names
- **Error responses:** RFC 7807 Problem Details
- **Pagination:** Use `skip` and `take` query parameters
- **Filtering:** Query string parameters (e.g., `?status=active`)

### Resilience Patterns
Use **Polly** library for resilience:

```csharp
// Retry with exponential backoff
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));

// Circuit breaker
var circuitBreakerPolicy = Policy
    .Handle<HttpRequestException>()
    .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30));

// Combine policies
var resilientPolicy = Policy.WrapAsync(retryPolicy, circuitBreakerPolicy);
await resilientPolicy.ExecuteAsync(() => _httpClient.GetAsync(url));
```

## Testing Standards

### C# / .NET Testing
- **Framework:** xUnit (preferred) or NUnit
- **Assertions:** FluentAssertions for readable assertions
- **Mocking:** NSubstitute (preferred) or Moq
- **Test Naming:** `MethodName_Scenario_ExpectedResult` or `When_Scenario_Should_ExpectedResult`
- **Test Organization:** Mirror production code structure

**Example:**
```csharp
public class AccountServiceTests
{
    [Fact]
    public async Task CreateAccount_WithValidData_ShouldReturnAccountId()
    {
        // Arrange
        var mockRepo = Substitute.For<IAccountRepository>();
        var service = new AccountService(mockRepo);

        // Act
        var result = await service.CreateAccount("Test Account");

        // Assert
        result.Should().BeGreaterThan(0);
        await mockRepo.Received(1).AddAsync(Arg.Any<Account>());
    }
}
```

### TypeScript / React Testing
- **Framework:** Jest + React Testing Library
- **Mocking:** Jest mocks + MSW (Mock Service Worker) for API mocking
- **Test Naming:** Descriptive strings (e.g., `"should display error when API fails"`)
- **Test File Location:** Co-located with components (`ComponentName.test.tsx`)

**Example:**
```typescript
import { render, screen } from '@testing-library/react';
import { AccountList } from './AccountList';

test('should display loading state initially', () => {
  render(<AccountList />);
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});

test('should display accounts when loaded', async () => {
  render(<AccountList />);
  const accountName = await screen.findByText('Test Account');
  expect(accountName).toBeInTheDocument();
});
```

### Test Coverage Targets
- **Unit Tests:** 85%+ coverage for business logic (AssetMark mandate)
- **Integration Tests:** Critical paths (auth, payment flows, data persistence)
- **E2E Tests:** Playwright for critical user journeys (login, account creation, etc.)

## Development Tools

### IDEs & Editors
- **Visual Studio 2022** — C# development (Community, Professional, or Enterprise)
- **Visual Studio Code** — TypeScript/React development + C# lightweight tasks
- **Extensions:**
  - C#: C# Dev Kit, IntelliCode
  - TypeScript: ESLint, Prettier, TypeScript and JavaScript Language Features

### Code Quality
- **Linting:**
  - C#: Built-in Roslyn analyzers + StyleCop
  - TypeScript: ESLint with TypeScript plugin
- **Formatting:**
  - C#: EditorConfig for consistent style
  - TypeScript: Prettier
- **Static Analysis:** SonarQube or SonarCloud (if available)

### Package Management
- **C#:** NuGet (use central package management for multi-project solutions)
- **TypeScript:** npm (use `package-lock.json` for consistent builds)

## Key Libraries & Frameworks

### C# / .NET
- **MediatR** — CQRS pattern, request/response handling
- **FluentValidation** — Input validation
- **AutoMapper** — Object-to-object mapping (use sparingly)
- **Entity Framework Core** — ORM for SQL databases
- **Polly** — Resilience and transient fault handling
- **Serilog** — Structured logging
- **Microsoft.Identity.Web** — Azure AD authentication

### TypeScript / React
- **React Router** — Client-side routing
- **Zod** — Runtime type validation and parsing
- **TanStack Query (React Query)** — Server state management, caching
- **Axios** — HTTP client (or native `fetch` with error handling)
- **date-fns** — Date manipulation (lighter alternative to Moment.js)
- **@azure/msal-react** — Azure AD authentication

## Performance Best Practices

### C# / .NET
- **Async all the way** — No blocking on async (no `.Result` or `.Wait()`)
- **EF Core:**
  - Use `AsNoTracking()` for read-only queries
  - Avoid N+1 queries (use eager loading with `.Include()`)
  - Use projections (`Select`) instead of loading full entities
- **Caching:** Use `IMemoryCache` or `IDistributedCache` (Azure Cache for Redis)
- **Response compression:** Enable Brotli/GZip compression

### TypeScript / React
- **Code splitting** — Lazy load routes and large components
- **Memoization** — Use `React.memo`, `useMemo`, `useCallback` appropriately
- **Virtualization** — Use `react-window` or `react-virtualized` for large lists
- **Bundle optimization** — Tree shaking, code splitting, dynamic imports

## Security Reminders
- **No hardcoded secrets** — Use Azure Key Vault
- **Managed identities** — For all service-to-service auth
- **Input validation** — On all API endpoints
- **Output encoding** — React handles by default, but no `dangerouslySetInnerHTML` without sanitization
- **Parameterized queries** — Always (EF Core handles this)
- **TLS 1.2+** — For all connections
- **Correlation IDs** — For distributed tracing

## Reference Documentation
- **.NET:** [Microsoft Learn - .NET](https://learn.microsoft.com/dotnet/)
- **React:** [React Docs](https://react.dev/)
- **Azure:** [Microsoft Learn - Azure](https://learn.microsoft.com/azure/)
- **TypeScript:** [TypeScript Handbook](https://www.typescriptlang.org/docs/)
