# Example: Team Onboarding Workflow

A Copilot workflow for onboarding a new AssetMark team onto Copilot customizations.

## Strategy: Progressive Disclosure

```
Day 1:  Model selection + environment check (everyone picks Claude Sonnet 4.6)
Week 1: Instructions only (passive, no agent interaction required)
Week 2: Add review prompts (active, optional usage)
Week 3: Add agents with handoffs (full workflow)
Week 4: Team-specific customizations
```

## Day 1: Model Selection (Required First Step)

Every engineer on the team must set **Claude Sonnet 4.6** as their Copilot Chat model. This is the org-standard model, effective 2026-02-23.

**Steps:**
1. Open VS Code → Copilot Chat (`Ctrl+Alt+I` / `Cmd+Alt+I`)
2. Click the model selector at the top of the chat panel
3. Select **Claude Sonnet 4.6** from the dropdown
4. Done — setting persists per workspace

**Verify during kickoff:** Ask each developer to confirm their model shows "Claude Sonnet 4.6" in the chat header before proceeding to the workshop.

## Week 1: Instructions Only

Drop these into the team's repo — Copilot auto-applies them:

```
.github/
├── copilot-instructions.md              # AssetMark baseline (copy from assetmark-copilot)
└── instructions/
    ├── csharp.instructions.md           # applyTo: "**/*.cs"
    └── typescript.instructions.md       # applyTo: "**/*.ts,**/*.tsx"
```

**No training needed.** Copilot just starts following the standards silently.

## Week 2: Add Prompts

```
.github/
└── prompts/
    ├── amk-codereview.prompt.md         # /amk-codereview — run a review
    └── amk-testgen.prompt.md            # /amk-testgen — generate tests
```

**Quick team demo:** Show them `/amk-codereview` and `/amk-testgen` in a 5-min standup.

## Week 3: Add Agents

```
.github/
└── agents/
    ├── code-review.agent.md             # @code-review orchestrator
    └── planner.agent.md                 # @planner for new features
```

**Team workshop:** 30 min, show agent usage and handoff buttons.

## Week 4: Customize

Run `/amk-generate-instructions` to discover the team's specific patterns from their codebase and create custom `.instructions.md` files.

## Key Patterns Used
1. **Progressive disclosure** — don't overwhelm, layer complexity
2. **Instructions first** — zero-friction, auto-applied
3. **Prompts second** — opt-in, discoverable via `/`
4. **Agents last** — full workflow, trained usage
5. **Auto-discover conventions** — use existing code to generate standards
