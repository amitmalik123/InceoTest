---
name: 'debugging'
description: 'Structured debugging checklists for .NET runtime errors. Use when encountering NullReferenceException, async deadlocks, TaskCanceledException, EF Core ObjectDisposedException, N+1 queries, HTTP 4xx/5xx errors, DI registration issues, configuration binding failures, JSON serialization errors, FluentValidation failures, EF migrations, performance bottlenecks, or React/TypeScript frontend issues. Provides systematic investigation with ranked causes and quick fixes.'
user-invokable: false
---

# Debugging Skill

Structured debugging checklists for common .NET error patterns.

## Purpose

This skill provides the `@Debugger` agent with systematic investigation procedures for diagnosing and resolving common runtime errors in AssetMark's .NET applications.

## How the @Debugger Agent Uses These Checklists

When the `@Debugger` agent encounters an error:

1. **Error Classification** - Identifies the error type from stack trace or symptoms
2. **Checklist Selection** - Loads the appropriate checklist for that error category
3. **Systematic Investigation** - Works through causes ranked by likelihood
4. **Root Cause Identification** - Applies investigation steps until cause is found
5. **Resolution** - Applies quick fixes and recommends prevention patterns

## Available Checklists

| Checklist | Error Types | When to Use |
|-----------|-------------|-------------|
| [null-reference.md](checklists/null-reference.md) | `NullReferenceException`, null warnings | Object is null when accessed |
| [async-issues.md](checklists/async-issues.md) | Deadlocks, `TaskCanceledException`, context errors | Async/await problems |
| [ef-core-issues.md](checklists/ef-core-issues.md) | `ObjectDisposedException`, tracking conflicts, N+1 | Entity Framework Core issues |
| [http-errors.md](checklists/http-errors.md) | 4xx/5xx status codes, timeouts, auth failures | HTTP/API communication errors |
| [di-issues.md](checklists/di-issues.md) | `InvalidOperationException`, missing registrations | Dependency injection problems |
| [config-issues.md](checklists/config-issues.md) | Missing settings, binding failures | Configuration and appsettings issues |
| [json-serialization.md](checklists/json-serialization.md) | `JsonException`, circular references, null handling | JSON serialization/deserialization |
| [validation-issues.md](checklists/validation-issues.md) | FluentValidation errors, 400 Bad Request | Input validation failures |
| [migration-issues.md](checklists/migration-issues.md) | EF migrations, schema conflicts | Database migration problems |
| [performance-issues.md](checklists/performance-issues.md) | Slow queries, memory leaks, high CPU | Performance bottlenecks |
| [frontend-issues.md](checklists/frontend-issues.md) | React errors, TypeScript issues, state problems | Frontend debugging |

## Checklist Structure

Each checklist follows a consistent format:

1. **Common Causes** - Ranked by likelihood based on AssetMark codebase patterns
2. **Investigation Steps** - Systematic diagnostic procedures
3. **Quick Fixes** - Immediate solutions for each cause
4. **Prevention Patterns** - Long-term fixes to prevent recurrence

## Usage Example

```
@Debugger I'm getting a NullReferenceException in my service layer
```

The agent will:
1. Load `checklists/null-reference.md`
2. Ask clarifying questions about the context
3. Guide through investigation steps
4. Propose targeted fixes

## Adding New Checklists

When adding a new error pattern checklist:

1. Create `checklists/{error-type}.md`
2. Follow the four-section structure (Causes, Investigation, Fixes, Prevention)
3. Rank causes by likelihood in AssetMark's codebase
4. Include code examples using AssetMark conventions
5. Update this SKILL.md index table


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
