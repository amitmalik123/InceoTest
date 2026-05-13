---
name: 'copilot-workflow-builder'
description: 'Build and maintain GitHub Copilot workflow artifacts (.github/ directory structures) for AssetMark repositories. Use when creating custom agents, skills, prompt files, instructions, or MCP server configurations. Provides templates, validation, and best practices aligned with the AssetMark TSA and AI Activation program.'
user-invokable: false
---

# Copilot Workflow Builder

## When to Use
- Creating new Copilot agents, skills, prompts, or instructions for an AssetMark repo
- Auditing or updating existing `.github/` Copilot configurations
- Scaffolding a new repo's Copilot setup from scratch
- Migrating from ad-hoc prompts to structured workflows

## Process

### 1. Assess Current State
Check the target repo for existing Copilot artifacts:
```
.github/copilot-instructions.md
.github/instructions/*.instructions.md
.github/agents/*.agent.md
.github/skills/*/SKILL.md
.github/prompts/*.prompt.md
.vscode/mcp.json
```

### 2. Identify Gaps
Compare against AssetMark's standard workflow structure:
- **Baseline:** `copilot-instructions.md` with security + code standards
- **Language-specific:** `.instructions.md` files scoped by `applyTo` glob
- **Agents:** At minimum, a reviewer agent for PR workflows

### 3. Generate Artifacts

#### Custom Agent Template
```markdown
---
description: "{What this agent does — shown as placeholder text}"
name: "{Agent Name}"
tools: [{list of allowed tools}]
model: "Claude Sonnet 4.6 (copilot)"
handoffs:
  - label: "{Button text for next step}"
    agent: "{target-agent-filename-without-extension}"
    prompt: "{Pre-filled prompt}"
    send: false
---
# {Agent Name} Instructions

## Role
{What this agent is and what it does}

## Constraints
{What this agent CANNOT do}

## Process
{Step-by-step workflow}
```

#### Agent Skill Template
```markdown
---
name: {skill-name}
description: "{What + When — specific enough for auto-activation}"
---
# {Skill Name}

## When to Use
{Trigger conditions}

## Process
{Step-by-step instructions}

## Scripts
{Reference to bundled scripts}
```

#### Prompt File Template
```markdown
---
description: "{What this prompt does}"
name: "{prompt-name}"
model: "Claude Sonnet 4.6 (copilot)"
tools:
  - "{tool1}"
  - "{tool2}"
---
# {Prompt Title}

{Instructions for the task}

## Input
${input:description}

## Steps
1. {Step 1}
2. {Step 2}

## Output
{Expected output format}
```

#### Scoped Instructions Template
```markdown
---
applyTo: "{glob-pattern}"
---
# {Language/Domain} Instructions

{Standards specific to this file type}
```

### 4. Configure MCP Servers

Configure MCP servers in `.vscode/mcp.json` as needed for the project.

### 5. Configure Agent Hooks (Optional but Recommended)

Agent hooks execute shell commands at lifecycle points during agent sessions (VS Code 1.109.3+). They are deterministic — unlike instructions, hooks guarantee outcomes regardless of how the agent was prompted.

**When to add hooks to a repo:**
- Any repo with production deployments → add security hook
- Repos with TypeScript/C# code → add formatting hook
- Repos with compliance requirements → add audit log hook

**Hook file location:** `.github/hooks/*.json` (shared with team, committed to repo)

**Hook JSON format:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "./scripts/hooks/my-hook.sh",
        "windows": "powershell -File scripts\\hooks\\my-hook.ps1",
        "timeout": 10
      }
    ]
  }
}
```

**Available lifecycle events:**
| Event | When | Common Use |
|-------|------|-----------|
| `PreToolUse` | Before any tool runs | Block dangerous commands, require approval |
| `PostToolUse` | After tool succeeds | Auto-format, audit log, trigger follow-up |
| `SessionStart` | Session begins | Inject project context |
| `Stop` | Session ends | Generate report, log summary |
| `UserPromptSubmit` | User submits prompt | Audit requests |
| `PreCompact` | Before context compaction | Save state |
| `SubagentStart` / `SubagentStop` | Subagent lifecycle | Track nested agents |

**Hook script must output JSON to stdout:**
```bash
# Allow (default — also works if script outputs nothing)
echo '{"continue":true}'

# Block a tool (PreToolUse only)
echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Reason here"}}'

# Require user confirmation (PreToolUse only)
echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Confirm this action"}}'
```

**Exit codes:** 0 = success, 2 = blocking error (stops agent), other = non-blocking warning

**Always provide both sh + ps1 implementations** — AssetMark developers are on Windows.

**AssetMark standard hooks (already in this repo — copy to new repos as needed):**
- `.github/hooks/security.json` + `scripts/hooks/security-check.{sh,ps1}` — blocks destructive shell/SQL
- `.github/hooks/formatting.json` + `scripts/hooks/format-changed-files.{sh,ps1}` — auto-runs Prettier + dotnet-format
- `.github/hooks/audit-log.json` + `scripts/hooks/audit-log.{sh,ps1}` + `session-summary.{sh,ps1}` — NDJSON compliance log

**⚠️ Preview:** Hooks are VS Code 1.109.3 Preview. Silently ignored on older versions — safe to include in repo.

### 6. Validate
Before delivery, verify:
- All frontmatter fields are valid
- All handoff targets exist
- All tool references are valid
- No secrets in any file
- Model identifiers are valid Copilot models — program standard is `Claude Sonnet 4.6 (copilot)` for all agents and prompts
- Hook scripts have both `.sh` and `.ps1` implementations if hooks are included
- Hook scripts are executable (`chmod +x`) and output valid JSON

## References
- [VS Code Copilot Customization](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Custom Agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [MCP Servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Agent Hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)

## Examples

See `examples/` directory for complete working configurations:
- `examples/api-service/` — Full workflow for an API service repo
- `examples/data-pipeline/` — Workflow for data processing repos

## Coverage Standard

AssetMark enforces **85% minimum line and branch coverage**. All code produced or reviewed using this skill must maintain this threshold.
