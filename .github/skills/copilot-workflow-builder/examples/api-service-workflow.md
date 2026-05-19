# Example: API Service Workflow

A minimal Copilot workflow for an ASP.NET Core API service repo.

## File Structure

```
.github/
├── copilot-instructions.md
├── instructions/
│   ├── csharp-api.instructions.md      # applyTo: "**/*.cs"
│   └── sql-queries.instructions.md     # applyTo: "**/*.sql"
├── agents/
│   ├── api-reviewer.agent.md           # Read-only code review
│   └── endpoint-scaffolder.agent.md    # Creates new endpoints
├── prompts/
│   ├── new-endpoint.prompt.md          # /new-endpoint scaffold
│   └── review-pr.prompt.md             # /review-pr trigger
└── AGENTS.md
.vscode/
└── mcp.json                            # Context7 + Microsoft Learn
```

## Agent: api-reviewer.agent.md
```yaml
---
name: 'API Reviewer'
description: 'Review ASP.NET Core API endpoints for correctness, security, and adherence to AssetMark conventions'
model: 'Claude Sonnet 4.6 (copilot)'
tools: ['search/codebase', 'read/readFile', 'search', 'read/problems']
---
```
- Read-only (no `editFiles`)
- Checks: auth attributes, input validation, response patterns, error handling
- References `instructions/csharp-api.instructions.md`

## Agent: endpoint-scaffolder.agent.md
```yaml
---
name: 'Endpoint Scaffolder'
description: 'Create new API endpoints following AssetMark conventions with controller, service, DTOs, and tests'
model: 'Claude Sonnet 4.6 (copilot)'
tools: ['search/codebase', 'edit/editFiles', 'read/readFile', 'search', 'execute/runInTerminal', 'execute/getTerminalOutput']
handoffs:
  - label: 'Review the new endpoint'
    agent: 'api-reviewer'
    prompt: 'Review the newly created endpoint: '
    send: false
---
```
- Full write access for scaffolding
- Hands off to reviewer after creation

## Key Patterns Used
1. **Read-only reviewer** — prevents accidental code changes during review
2. **Handoff chain** — scaffold → review is natural workflow
3. **Scoped instructions** — C# instructions only apply to `.cs` files
4. **MCP for docs** — Context7 + Microsoft Learn for API design guidance
