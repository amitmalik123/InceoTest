---
name: 'mcp-integration'
description: 'Guide for using MCP (Model Context Protocol) servers with AssetMark Copilot agents — available servers, authentication setup, and tool usage patterns.'
user-invokable: false
---

# MCP Integration — Model Context Protocol

MCP (Model Context Protocol) extends GitHub Copilot agents with external tools and data sources. This skill documents available MCP servers, setup requirements, and usage patterns for AssetMark Copilot workflows.

## Available MCP Servers

### Overview Table

| Server | Purpose | Auth Required | Tools Provided | Use Cases |
|--------|---------|---------------|----------------|-----------|
| `azure` | Azure resource management and querying | `az login` + subscription ID | `list-resources`, `get-resource`, `search-resource-graph`, `list-resource-groups`, `get-resource-group` | Cost analysis, resource inventory, compliance auditing |
| `azure-devops` | Azure DevOps API (work items, pipelines, repos, PRs) | `az login` (org: `assetmark`) | `list_work_items`, `create_work_item`, `get_pipeline_runs`, `create_pull_request`, `get_repositories` | Sprint planning, deployment tracking, PR automation |

---

## Server Details

### azure

**Purpose:** Query Azure resources using Azure Resource Graph and management APIs.

**Tools:**
- `list-resources` — List all resources in a subscription
- `get-resource` — Get details of a specific resource
- `search-resource-graph` — Execute Kusto Query Language (KQL) queries against Azure Resource Graph
- `list-resource-groups` — List all resource groups
- `get-resource-group` — Get resource group details

**Authentication:** Azure CLI (`az login`) — no secrets in config

**Required Permissions:**
- `Reader` role on subscription or resource groups (read-only access)
- For cost queries: `Cost Management Reader` role

**Security Notes:**
- **Run `az login` before starting VS Code** — The server uses your active CLI session
- **Subscription ID is not a secret** — Safe to prompt via VS Code input variable
- **Least privilege** — Grant minimum role required (Reader for queries, never Contributor)

**Example Usage:**
```json
// .vscode/mcp.json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--subscription", "${input:azure_subscription_id}"]
    }
  },
  "inputs": [
    { "id": "azure_subscription_id", "type": "promptString", "description": "Azure Subscription ID (requires az login)" }
  ]
}
```

**When to Use:**
- Cost analysis and optimization reviews
- Compliance auditing (find resources missing tags, public endpoints)
- Resource inventory for documentation
- Identifying orphaned resources

**Agent Assignments:**
- ✅ `architect.agent.md` — Verify existing Azure resources before designing new services
- ✅ `cost-optimizer.agent.md` — Query resource SKUs, identify under-utilized resources

---

### azure-devops

**Purpose:** Automate Azure DevOps operations — query and create work items, manage pipelines, automate PR creation, and track sprints.

**Tools:**
- `list_work_items` — Query work items using WIQL (Work Item Query Language)
- `create_work_item` — Create new work items (User Stories, Tasks, Bugs)
- `update_work_item` — Update existing work item fields
- `get_work_item` — Get details of a specific work item
- `get_pipeline_runs` — List pipeline run history
- `queue_pipeline` — Trigger a pipeline run
- `get_repositories` — List repositories in a project
- `create_pull_request` — Create a pull request in Azure Repos
- `get_pull_request` — Get PR details
- `get_sprints` — List sprints in a project
- `get_iterations` — List iterations for backlog planning

**Authentication:** Azure CLI (`az login`) — no PAT required

**Required Permissions (via Azure AD / Entra ID):**
- `Work Items: Read & Write` — For querying and creating work items
- `Code: Read & Write` — For PR automation
- `Build: Read & Execute` — For pipeline operations
- `Project and Team: Read` — For sprint/iteration queries

**Security Notes:**
- **Run `az login` before starting VS Code** — The server uses your active CLI session
- **No secrets in config** — Org name is hardcoded (`assetmark`), no PAT needed
- **Least privilege** — Azure AD permissions are scoped per your account's project access

**Example Usage:**
```json
// .vscode/mcp.json
{
  "servers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp@latest"],
      "env": { "AZURE_DEVOPS_ORG": "assetmark" }
    }
  }
}
```

**When to Use:**
- Query existing work items during discovery (understand current backlog)
- Create tasks from implementation plans automatically
- Link specs/RFCs to work items for traceability
- Check pipeline status before deployment planning
- Automate PR creation for automated code changes
- Sprint planning and capacity tracking
- Release tracking (which work items are in which release)

**Agent Assignments:**
- ✅ `discovery.agent.md` — Query existing work items and requirements during discovery
- ✅ `spec-writer.agent.md` — Create/link work items from specifications
- ✅ `planner.agent.md` — Create tasks from implementation plans
- ✅ `deployment-planner.agent.md` — Check pipeline status, track releases, query sprint work

**Usage Patterns:**

**Pattern 1: Query Existing Work Items (Discovery)**
```typescript
// During discovery, find existing work items related to a feature
const workItems = await azureDevops.listWorkItems({
  wiql: `
    SELECT [System.Id], [System.Title], [System.State]
    FROM WorkItems
    WHERE [System.TeamProject] = 'AssetMark'
      AND [System.AreaPath] = 'AssetMark\\Accounts'
      AND [System.State] <> 'Closed'
    ORDER BY [System.ChangedDate] DESC
  `
});
```

**Pattern 2: Create Tasks from Implementation Plan (Planner)**
```typescript
// After generating implementation plan, create Azure Boards tasks
const task = await azureDevops.createWorkItem({
  project: 'AssetMark',
  workItemType: 'Task',
  title: 'TASK-001: Create AccountService with validation',
  description: 'Implement AccountService.CreateAccount with input validation...',
  assignedTo: 'developer@assetmark.com',
  iteration: 'Sprint 42',
  areaPath: 'AssetMark\\Accounts',
  parent: 12345  // Link to parent User Story
});
```

**Pattern 3: Check Pipeline Status (Deployment Planner)**
```typescript
// Before planning deployment, check latest pipeline runs
const runs = await azureDevops.getPipelineRuns({
  project: 'AssetMark',
  pipelineId: 123,
  top: 5
});

const latestRun = runs[0];
if (latestRun.status !== 'completed' || latestRun.result !== 'succeeded') {
  // Warn that deployment may be risky
}
```

**Pattern 4: Create PR for Automated Changes**
```typescript
// After generating code changes, create PR automatically
const pr = await azureDevops.createPullRequest({
  project: 'AssetMark',
  repository: 'assetmark-api',
  sourceBranch: 'feature/auto-generated-endpoints',
  targetBranch: 'develop',
  title: 'feat(api): add auto-generated CRUD endpoints',
  description: 'Auto-generated by SpecWriter agent...\n\nAB#12345',
  workItemRefs: [12345]
});
```

---

## Setup Instructions

### Prerequisites

**All MCP Servers:**
- VS Code with GitHub Copilot extension installed
- GitHub Copilot subscription (Pro or Enterprise)

**azure:**
- Node.js 18+ installed (`node --version` to verify)

### Step 1: Run `az login`

Both MCP servers use Azure CLI authentication. Before starting VS Code, run:

```bash
az login
az account set --subscription "<your-subscription-id>"
```

No PATs or secrets needed. Authentication flows through your active Azure CLI session.

### Step 2: Create `.vscode/mcp.json`

The `.vscode/mcp.json` file in the repo root defines available MCP servers. This file is **committed to the repo** — no secrets, no input variables for auth.

```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--subscription", "${input:azure_subscription_id}"]
    },
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp@latest"],
      "env": { "AZURE_DEVOPS_ORG": "assetmark" }
    }
  },
  "inputs": [
    { "id": "azure_subscription_id", "type": "promptString", "description": "Azure Subscription ID (requires az login)" }
  ]
}
```

VS Code will prompt for the subscription ID once at startup (it's not a secret — just routing). Auth comes from `az login`.

### Step 3: Enable MCP in VS Code Settings

Open VS Code Settings (Cmd+, / Ctrl+,) and search for "MCP". Ensure:

- ✅ `GitHub Copilot > MCP: Enabled` is checked
- ✅ `GitHub Copilot > MCP: Auto Start` is checked (optional, starts servers on demand)

### Step 4: Assign MCP Servers to Agents

In each agent's YAML frontmatter, add the `mcp-servers` field:

```yaml
---
name: 'MyAgent'
description: '...'
model: 'Claude Sonnet 4.6 (copilot)'
tools: ['read', 'search', 'azure/*']
---
```

**Principle: Least Privilege**
Only assign MCP servers that the agent actually needs. Don't give every agent access to every server.

---

## Usage Patterns

### Pattern 1: Cost Optimization Review (azure)

**Scenario:** Cost optimizer reviews all App Service Plans in a subscription to find over-provisioned instances.

**Agent:** `cost-optimizer.agent.md`

**Workflow:**
1. Agent calls `search-resource-graph` with KQL query:
   ```kql
   Resources
   | where type == 'microsoft.web/serverfarms'
   | project name, sku, location, resourceGroup
   ```
2. MCP returns all App Service Plans
3. Agent analyzes SKU sizes (P3v3, P2v3, etc.)
4. Agent cross-references with CPU/memory metrics (via Application Insights)
5. Agent reports over-provisioned plans with cost savings estimate

**Why MCP vs Azure CLI:**
- No need to authenticate separately (uses existing Azure session)
- Structured JSON output (no parsing Azure CLI text)
- Faster queries via Resource Graph (vs iterating resources)

---

## Troubleshooting

### Error: "MCP server not found"

**Cause:** MCP server not defined in `.vscode/mcp.json`

**Fix:**
1. Verify server name matches exactly (case-sensitive)
2. Ensure `.vscode/mcp.json` exists in repo root
3. Reload VS Code window (Cmd+Shift+P → "Reload Window")

---

### Error: "Failed to start MCP server: command not found"

**Cause:** Missing dependency (Node.js or Docker)

**Fix:**
- For `azure`: Install Node.js 18+ (`brew install node` / `apt install nodejs`)

---

### Error: "Azure subscription not found"

**Cause:** Invalid subscription ID or missing permissions

**Fix:**
1. Verify subscription ID: `az account show --query id -o tsv`
2. Ensure you have `Reader` role: `az role assignment list --assignee YOUR_EMAIL --subscription YOUR_SUB_ID`
3. Re-authenticate: `az login`

---

### Performance: MCP server slow to start

**Cause:** Docker image pull or npm package install on first run

**Fix:**
- **npm servers:** Pre-cache packages:
  ```bash
  npx -y @azure/mcp@latest --version
  ```

---

## Security Best Practices

### 1. Never Commit Secrets

❌ **Bad:**
```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--subscription", "12345678-1234-1234-1234-123456789abc"]
    }
  }
}
```

✅ **Good:**
```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--subscription", "${input:azure_subscription_id}"]
    }
  },
  "inputs": [
    { "id": "azure_subscription_id", "type": "promptString", "description": "Azure Subscription ID (requires az login)" }
  ]
}
```

Auth via `az login` — the subscription ID is routing, not a secret.

### 2. Least Privilege: Assign Only Required MCP Servers

❌ **Bad:** Every agent has access to all servers
```yaml
mcp-servers:
  - azure
  - azure-devops
```

✅ **Good:** Agent only has servers it needs
```yaml
# discovery.agent.md
mcp-servers:
  - azure-devops  # Only needs Azure DevOps, not Azure APIs
```

### 3. Use Managed Identity (Azure)

When running in Azure environments (Azure DevOps agents, Container Apps), prefer Managed Identity over service principals:
- No credentials to manage or rotate
- Automatic authentication
- Fine-grained RBAC via Azure AD roles

### 4. Audit MCP Server Usage

- Review `.github/agents/*.agent.md` frontmatter regularly
- Remove unused MCP server assignments
- Monitor agent logs for unexpected API calls

---

## Adding New MCP Servers

### Step 1: Find MCP Server

Search for MCP servers:
- **Official MCP registry:** https://github.com/modelcontextprotocol/servers
- **npm packages:** Search for `mcp` keyword
- **Docker images:** Search GitHub Container Registry (`ghcr.io`)

### Step 2: Test Locally

Before adding to `.vscode/mcp.json`, test the server:

```bash
# stdio server (npx)
npx -y @namespace/mcp-server-name@latest --help

# Docker server
docker run -i --rm ghcr.io/org/mcp-server-name:latest --help
```

### Step 3: Add to `.vscode/mcp.json`

```json
{
  "servers": {
    "my-new-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@namespace/mcp-server-name@latest"],
      "env": {
        "API_KEY": "${input:my_api_key}"
      }
    }
  }
}
```

### Step 4: Document in This Skill

Add a new section under **Available MCP Servers** with:
- Purpose
- Tools provided
- Authentication requirements
- Example usage
- When to use
- Agent assignments

### Step 5: Validate with CI

Run validation script to ensure:
- JSON syntax is valid
- All referenced servers exist
- Agents only reference defined servers

```bash
python3 scripts/validate_mcp_config.py .
```

---

## MCP Resources

Beyond tools, MCP servers can expose **Resources** — structured data objects that can be attached to a chat prompt as context. Resources are ideal when you need to inject live data (database tables, resource inventories, API responses) without asking the agent to call a tool to fetch it.

### Using Resources in Chat

1. In the Chat panel, click **Add Context** (the paperclip icon)
2. Select **MCP Resources**
3. Browse available resources from connected servers
4. Select resources to attach as context before sending your prompt

Alternatively, run the command: `MCP: Browse Resources`

### When to Use Resources vs Tools

| Use Resources when... | Use Tools when... |
|----------------------|-------------------|
| You need read-only data as context | You need to take an action (create, update, delete) |
| The data changes infrequently | You need real-time query results |
| You want to attach structured data to a prompt | You want the agent to decide what to fetch |

### Example: Azure Resources as Context

```
[Attach MCP Resource: Azure Resource Inventory for assetmark-prod]
@architect "Given the current Azure resources above, design the new accounts service architecture without duplicating existing infrastructure."
```

---

## MCP Prompts

MCP servers can also expose **Prompts** — pre-written, parameterized prompt templates optimized for common tasks. Prompts from MCP servers work like AssetMark's own `/amk-*` slash commands.

### Using MCP Prompts

Type `/<server-name>.<prompt-name>` in the Chat input. For example:

```
/azure-devops.create-sprint-plan
/microsoftdocs.summarize-service-docs
```

### Difference from AssetMark `/amk-*` Prompts

| AssetMark Prompts (`/amk-*`) | MCP Server Prompts |
|-----------------------------|-------------------|
| Defined in `.github/prompts/` | Defined by the MCP server |
| Tailored to AssetMark workflows | General-purpose (Azure, ADO, etc.) |
| Full control over content | Controlled by server publisher |

Use AssetMark prompts as the primary entry point. Use MCP server prompts for generic platform tasks where no `/amk-*` prompt exists.

---

## MCP Apps

MCP Apps are **interactive UI components** rendered directly in the VS Code Chat panel by MCP servers. They can include forms, visualizations, drag-and-drop lists, and other rich interactions.

As of 2026, none of the four AssetMark MCP servers (azure, azure-devops, microsoftdocs, playwright) ship MCP Apps. This section documents the capability for future reference.

**When MCP Apps become available from a server:** They appear automatically inline in Chat when you invoke a relevant prompt or tool. No special invocation needed.

---

## Reference

- [MCP Specification](https://modelcontextprotocol.io/)
- [VS Code MCP Docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Available MCP Servers — GitHub Registry](https://github.com/mcp)
- [Azure MCP Server](https://github.com/Azure/azure-mcp)
- [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp)

## Coverage Standard

AssetMark enforces **85% minimum line and branch coverage**. All code produced or reviewed using this skill must maintain this threshold.
