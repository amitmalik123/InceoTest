---
name: 'review-output-format'
description: 'Standard JSON output format and severity classification for all code review agents'
user-invokable: false
---

# Review Output Format

This skill defines the standard JSON output format and severity classification used by all code review agents (C#, TypeScript, SQL, Frontend Assets).

## Output Format

Return findings as structured JSON for the orchestrator to merge:

```json
{
  "files_reviewed": ["path/to/file.ext"],
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "file": "path/to/file.ext",
      "line": 42,
      "title": "Issue title",
      "issue": "Description of the issue",
      "problem": "Why this matters",
      "suggested_fix": "Code suggestion or guidance"
    }
  ],
  "positive_aspects": [
    "What was done well"
  ]
}
```

## Severity Classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security vulnerabilities, data loss risks, breaking changes, code that will crash in production | SQL injection, missing auth, XSS vulnerabilities, unhandled exceptions that crash the app, data exposure |
| **High** | **Bugs that will cause runtime errors**, performance issues causing timeouts, accessibility blockers (WCAG A), missing authorization | Null reference exceptions, off-by-one errors, missing await, N+1 queries, resource leaks, unhandled promise rejections |
| **Medium** | Code quality issues, **potential bugs** (edge cases), maintainability concerns, missing type safety | Missing null checks (low traffic paths), code smells, high complexity, incomplete dependency arrays, `any` types |
| **Low** | Style suggestions, minor improvements, documentation, naming conventions | Comment improvements, minor DRY violations, code organization, property ordering |

## Bug Severity Guidelines

Use this decision tree to classify bug severity:

- **Will crash in production** → Critical or High
- **Could crash under certain conditions** → High or Medium
- **Reduces reliability but won't crash** → Medium
- **Makes code harder to maintain** → Low or Medium

## Language-Specific Critical Issues

### Security (All Languages)
- SQL injection / XSS / injection vulnerabilities → Critical
- Hardcoded secrets or API keys → Critical
- Missing authentication/authorization → Critical
- Unsanitized user input → Critical
- Data exposure / PII leakage → Critical

### C# / .NET
- Unhandled exceptions that crash the app → Critical
- `.Result` or `.Wait()` causing deadlocks → High
- Missing `IDisposable` cleanup → High
- Null reference without check after `FirstOrDefault()` → High

### TypeScript / React
- Unhandled promise rejections → High
- Memory leaks (missing cleanup in useEffect) → High
- Missing null/undefined checks after `find()` → High
- XSS via `dangerouslySetInnerHTML` without sanitization → Critical

### SQL
- SQL injection via string concatenation → Critical
- Missing WHERE clause on UPDATE/DELETE → Critical
- Missing indexes on large tables causing timeouts → High

### CSS / HTML
- WCAG A violations (complete barrier to access) → Critical
- Missing alt text on informative images → Critical
- Keyboard traps → Critical
- Color contrast failures (WCAG AA) → High

## Usage in Review Agents

Review agents should:

1. **Return valid JSON** - The orchestrator expects this exact format
2. **Use consistent severity levels** - Follow the classification table above
3. **Provide actionable feedback** - Include specific file, line, and suggested fix
4. **Always include positive aspects** - Acknowledge good practices
5. **Be concise** - Keep issue descriptions focused and clear


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
