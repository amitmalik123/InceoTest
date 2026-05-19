---
name: 'spec-driven-dev'
description: 'End-to-end spec-driven development workflow — from discovery through specification, architecture, planning, and implementation handoff. Includes templates, checklists, and handoff protocols.'
user-invokable: false
---

# Spec-Driven Development Workflow

This skill defines the end-to-end workflow for building features at AssetMark using a spec-driven approach. The workflow emphasizes **clarity before code** — requirements, specifications, and architecture decisions are documented and approved before implementation begins.

## Workflow Overview

```
Discovery → Spec → Architecture → Plan → Implement → Review → Test
  @discovery   @spec-writer  @architect   @planner  @cca-implementer  @code-review  @qa-engineer
```

**Philosophy:**
- **Think first, code later** — Understand the problem before proposing solutions
- **Document decisions** — Create artifacts that serve as living documentation
- **Iterate early** — Cheaper to change a spec than code
- **Trace requirements** — Every line of code maps back to a requirement

## Workflow Stages

### Stage 1: Discovery

**Agent:** `@discovery`
**Input:** Vague idea, Jira ticket, stakeholder request
**Output:** Requirements document (`/spec/requirements-{name}.md`)

**Purpose:** Transform vague ideas into structured requirements through conversation and exploration.

**Process:**
1. Read user input (idea, ticket, description)
2. Ask 3-7 clarifying questions (users, problem, scope, constraints)
3. Explore codebase for existing patterns
4. Identify risks and unknowns
5. Produce structured requirements document

**Key Questions:**
- **Users:** Who are the end users? What personas? Technical level?
- **Problem:** What problem does this solve? Current workaround?
- **Scope:** What's in scope? What's explicitly out of scope?
- **Constraints:** Timeline? Budget? Technical? Regulatory (TSA)?
- **Dependencies:** What systems integrate? What teams involved?
- **Success:** How do we know this is done? What metrics matter?

**Output Artifact:** `/spec/requirements-{feature-name}.md`

**Handoff Checklist:**
- [ ] Requirements document complete with all 10 sections
- [ ] Open questions resolved or assigned owners
- [ ] Stakeholders identified and approval chain defined
- [ ] TSA compliance concerns flagged (if any)
- [ ] Risks identified with likelihood and impact

**Next Stage:** Spec (hand off to `@spec-writer`)

---

### Stage 2: Specification

**Agent:** `@spec-writer`
**Input:** Requirements document or feature description
**Output:** Formal specification (`/spec/spec-{purpose}-{name}.md`)

**Purpose:** Transform requirements into formal, testable, AI-ready specifications.

**Process:**
1. Ingest requirements (read requirements doc or ask clarifying questions)
2. Analyze codebase for existing patterns and integration points
3. Draft specification using template (REQ-xxx, AC-xxx, data contracts)
4. Refine with user feedback
5. Finalize and save to `/spec/` directory

**Specification Elements:**
- **Numbered requirements:** REQ-001, REQ-002 (functional requirements)
- **Security requirements:** SEC-001, SEC-002
- **Constraints:** CON-001, CON-002
- **Non-functional requirements:** NFR-001, NFR-002 (performance, scalability)
- **Acceptance criteria:** AC-001, AC-002 (Given-When-Then format)
- **Data contracts:** API schemas, database schemas, integration contracts
- **Test strategy:** Unit, integration, E2E coverage plan
- **User stories:** US-001, US-002 (As a {persona}, I want {goal}, so that {benefit})

**Output Artifact:** `/spec/spec-{purpose}-{name}.md`

**Naming Convention:**
- `spec-feature-account-creation.md` (new feature)
- `spec-bugfix-validation-error.md` (bug fix)
- `spec-refactor-payment-service.md` (refactor)
- `spec-architecture-event-driven.md` (architectural change)

**Handoff Checklist:**
- [ ] All requirements have unique IDs (REQ-, SEC-, CON-, NFR-)
- [ ] All acceptance criteria use Given-When-Then format (AC-)
- [ ] Data contracts defined (API request/response, database schema)
- [ ] Test strategy outlined (unit, integration, E2E)
- [ ] Spec maps to requirements document (if applicable)
- [ ] Spec status: Draft → Review → Approved

**Next Stage:** Architecture (if architectural decisions needed) or Planning (if straightforward implementation)

---

### Stage 3: Architecture

**Agent:** `@architect`
**Input:** Specification or requirements document
**Output:** RFC document (`/docs/rfc/rfc-{number}-{name}.md`)

**Purpose:** Make technical design decisions — Azure service selection, data flow, integration patterns, TSA compliance.

**When to use this stage:**
- New services or significant architectural changes
- Azure service selection required
- Integration patterns need to be defined
- Performance/scale concerns require architectural decisions

**Skip this stage if:**
- Straightforward implementation (existing patterns apply)
- No Azure service selection needed
- No architectural decisions required

**Process:**
1. Understand context (read spec, requirements, explore codebase)
2. Identify architectural decisions (compute, database, messaging, caching)
3. Research options (Azure services, patterns, best practices)
4. Evaluate trade-offs (cost, performance, security, TSA compliance)
5. Propose architecture with multiple options
6. Review and iterate

**RFC Elements:**
- **Summary:** 1-2 sentence overview
- **Motivation:** Why are we making this change?
- **Proposed design:** Architecture overview, data flow, Azure services, API/DB design
- **Alternatives considered:** Trade-off matrix (Option A vs B vs C)
- **Security considerations:** Auth, encryption, PII, audit
- **Performance considerations:** Caching, scaling, load balancing
- **Cost estimate:** Monthly operational cost
- **Migration/rollout plan:** Phased deployment
- **Risks & mitigations:** What could go wrong? How to mitigate?
- **Open questions:** What needs answers?
- **Decision:** Recommended approach

**Output Artifact:** `/docs/rfc/rfc-{number}-{name}.md`

**Naming Convention:**
- `rfc-001-event-driven-notifications.md`
- `rfc-042-account-service-architecture.md`

**Handoff Checklist:**
- [ ] All Azure services listed with cost estimates
- [ ] TSA compliance verified (hand off to `@tsa-checker`)
- [ ] Security reviewed (hand off to `@security-reviewer`)
- [ ] Trade-off matrices complete (2-3 options per decision)
- [ ] Cost estimate provided (rough order of magnitude)
- [ ] Risks identified with mitigations
- [ ] RFC status: Draft → Review → Approved

**Next Stage:** Planning (hand off to `@planner`)

---

### Stage 4: Planning

**Agent:** `@planner`
**Input:** Specification and/or RFC
**Output:** Implementation plan (`/plan/{purpose}-{component}-{version}.md`)

**Purpose:** Break work into atomic tasks with dependencies, acceptance criteria, and effort estimates.

**Process:**
1. Understand request (read spec, RFC, or feature description)
2. Analyze codebase (existing implementations, patterns)
3. Research (Azure docs, best practices)
4. Design approach (phases, tasks, dependencies)
5. Break down tasks (TASK-xxx with acceptance criteria)
6. Identify risks and mitigations

**Implementation Plan Elements:**
- **Summary:** 1-2 sentence overview
- **Architecture overview:** Reference RFC for details
- **Phases:** MVP, Enhancements, Optimizations
- **Tasks:** TASK-001, TASK-002 (atomic, with dependencies)
- **Task structure:**
  ```
  TASK-001: {description}
  - File(s): {paths}
  - Action: create | modify | delete
  - Dependencies: None (or TASK-xxx)
  - Spec Requirements: REQ-xxx
  - Acceptance: {how to verify}
  - Estimated Effort: {hours/days}
  ```
- **Parallel vs sequential:** Explicit dependency graph
- **Phase completion criteria:** Measurable gates
- **Data model changes:** New tables, migrations
- **API changes:** New/modified endpoints
- **Security considerations:** Auth, PII, audit
- **Testing strategy:** Unit, integration, E2E
- **Risks & mitigations:** Technical, integration, timeline risks

**Output Artifact:** `/plan/{purpose}-{component}-{version}.md`

**Naming Convention:**
- `feature-account-creation-1.md` (new feature)
- `bugfix-validation-error-1.md` (bug fix)
- `refactor-payment-service-1.md` (refactor)

**Handoff Checklist:**
- [ ] Tasks are atomic (1-5 days max)
- [ ] All tasks have TASK-xxx IDs
- [ ] All tasks map to spec requirements (REQ-xxx)
- [ ] Dependencies explicit (parallel vs sequential)
- [ ] Acceptance criteria defined for each task
- [ ] Phase completion gates measurable
- [ ] Effort estimates realistic
- [ ] Plan status: Draft → In Progress → Complete

**Next Stage:** Implementation (development team) and Testing (hand off to `@qa-engineer` for test plan)

---

### Stage 5: Implementation

**Agent:** Development team (or `@cca-implementer` for code generation)
**Input:** Implementation plan
**Output:** Working code, tests, deployment

**Purpose:** Build the feature according to the plan.

**Process:**
1. Follow task sequence from implementation plan
2. Write code to meet acceptance criteria
3. Write tests (unit, integration, E2E)
4. Run tests and verify acceptance criteria met
5. Update plan status (mark tasks complete)

**Development Workflow:**
- Follow TASK-xxx sequence
- Check off acceptance criteria as you complete each task
- If blocked, update plan with blockers
- If design needs to change, update spec/RFC/plan

**Handoff Checklist:**
- [ ] All TASK-xxx items complete
- [ ] Unit tests passing (85% coverage — AssetMark mandate)
- [ ] Integration tests passing
- [ ] E2E tests passing (critical paths)
- [ ] Code follows AssetMark conventions (see `@.github/skills/assetmark-stack/SKILL.md`)
- [ ] Ready for code review

**Next Stage:** Code Review (hand off to `@code-review`)

---

### Stage 6: Code Review

**Agent:** `@code-review`
**Input:** Staged changes, branch, or directory
**Output:** Code review report (`.codereview/YYYY-MM-DD-HHmm-review.md`)

**Purpose:** Validate implementation quality, security, and adherence to standards.

**Process:**
1. Scope review (staged, branch, files, directory)
2. Delegate to type-specific agents (C#, TypeScript, SQL, frontend assets)
3. Merge findings, sort by severity, deduplicate
4. Write unified review report

**Review Focus:**
- **Correctness:** Does code meet spec requirements (REQ-xxx)?
- **Security:** Authentication, authorization, PII handling, input validation
- **Performance:** Meets NFRs (latency, throughput)
- **Maintainability:** Readable, follows conventions, documented
- **Test coverage:** Adequate unit/integration/E2E tests

**Handoff Checklist:**
- [ ] Code review complete
- [ ] Critical/high issues resolved
- [ ] Security review complete (deep dive with `@security-reviewer` if needed)
- [ ] TSA compliance verified (`@tsa-checker`)
- [ ] Ready for QA

**Next Stage:** QA Testing (hand off to `@qa-engineer`)

---

### Stage 7: QA Testing

**Agent:** `@qa-engineer`
**Input:** Implementation plan, spec, deployed feature
**Output:** Test plan, test results, bug reports

**Purpose:** Verify feature meets acceptance criteria and quality standards.

**Process:**
1. Review spec and implementation plan
2. Generate test plan (unit, integration, E2E, performance)
3. Execute tests
4. Report bugs (if any)
5. Verify bug fixes
6. Sign off on quality

**Testing Focus:**
- **Acceptance criteria:** All AC-xxx from spec are met
- **Functional requirements:** All REQ-xxx are satisfied
- **Non-functional requirements:** All NFR-xxx are met (performance, security, accessibility)
- **Edge cases:** Boundary conditions, error scenarios
- **Regression:** Existing functionality not broken

**Handoff Checklist:**
- [ ] Test plan complete (maps to AC-xxx)
- [ ] All tests passing
- [ ] No critical/high bugs
- [ ] Performance NFRs met (load testing)
- [ ] Accessibility compliance (if UI changes)
- [ ] Ready for production deployment

**Next Stage:** Deployment to production

---

## Artifact Directory Structure

Organize spec-driven artifacts in the repository:

```
/spec/                           — Specification documents
  requirements-{name}.md         — Requirements from discovery
  spec-feature-{name}.md         — Formal specifications
  spec-bugfix-{name}.md
  spec-refactor-{name}.md

/plan/                           — Implementation plans
  feature-{component}-1.md       — Implementation plans with TASK-xxx
  bugfix-{component}-1.md
  infrastructure-{component}-1.md

/docs/rfc/                       — Architecture decision records
  rfc-001-{name}.md              — RFCs with trade-off analysis
  rfc-042-{name}.md

/.codereview/                    — Code review reports
  YYYY-MM-DD-HHmm-review.md      — Generated review reports
```

## Naming Conventions

### Requirements Documents
- **Format:** `requirements-{feature-name}.md`
- **Examples:**
  - `requirements-account-creation.md`
  - `requirements-user-authentication.md`

### Specification Documents
- **Format:** `spec-{purpose}-{name}.md`
- **Purpose values:** `feature`, `bugfix`, `refactor`, `architecture`
- **Examples:**
  - `spec-feature-account-creation.md`
  - `spec-bugfix-validation-error.md`
  - `spec-refactor-payment-service.md`
  - `spec-architecture-event-driven.md`

### RFC Documents
- **Format:** `rfc-{number}-{name}.md`
- **Numbering:** Sequential (001, 002, 042, etc.)
- **Examples:**
  - `rfc-001-event-driven-notifications.md`
  - `rfc-042-account-service-architecture.md`

### Implementation Plans
- **Format:** `{purpose}-{component}-{version}.md`
- **Purpose values:** `feature`, `bugfix`, `refactor`, `infrastructure`
- **Version:** Incremental (1, 2, 3, etc.)
- **Examples:**
  - `feature-account-creation-1.md`
  - `bugfix-validation-error-1.md`
  - `refactor-payment-service-1.md`
  - `infrastructure-azure-migration-1.md`

## Handoff Protocols

Each stage has clear handoff criteria to ensure quality gates.

### Discovery → Spec

**Prerequisites:**
- [ ] Requirements document complete with all 10 sections
- [ ] Open questions resolved or assigned owners
- [ ] Stakeholders identified
- [ ] TSA compliance concerns flagged

**Handoff:**
```
@spec-writer Generate a formal specification from the requirements document above: /spec/requirements-{name}.md
```

### Spec → Architecture

**Prerequisites:**
- [ ] All REQ-/AC- IDs assigned
- [ ] Data contracts defined
- [ ] Test strategy outlined
- [ ] Spec status: Approved

**Handoff:**
```
@architect Design the architecture for the specification above: /spec/spec-{name}.md
```

**Note:** Skip architecture stage if no architectural decisions needed (straightforward implementation).

### Spec → Planning (Direct)

If no architectural decisions needed, skip to planning:

**Prerequisites:**
- [ ] Spec approved
- [ ] No Azure service selection needed
- [ ] Existing patterns apply

**Handoff:**
```
@planner Create an implementation plan for the specification above: /spec/spec-{name}.md
```

### Architecture → Planning

**Prerequisites:**
- [ ] RFC approved
- [ ] Azure services selected
- [ ] Security reviewed
- [ ] Cost estimated
- [ ] TSA compliance verified

**Handoff:**
```
@planner Create an implementation plan for the architecture above: /docs/rfc/rfc-{number}-{name}.md
Reference spec: /spec/spec-{name}.md
```

### Planning → Implementation

**Prerequisites:**
- [ ] Tasks atomic (1-5 days max)
- [ ] Dependencies mapped
- [ ] Acceptance criteria per task
- [ ] Plan status: Approved

**Handoff:**
Development team starts TASK-001 from `/plan/{purpose}-{component}-{version}.md`

### Planning → QA

**Prerequisites:**
- [ ] Implementation plan approved

**Handoff:**
```
@qa-engineer Generate a test plan for the implementation plan above: /plan/{purpose}-{component}-{version}.md
Map tests to acceptance criteria (AC-xxx)
```

### Implementation → Code Review

**Prerequisites:**
- [ ] All TASK-xxx complete
- [ ] Tests passing
- [ ] Code follows conventions

**Handoff:**
```
@code-review Review the implementation of: {feature name}
Scope: staged | branch | files | directory
```

### Code Review → QA

**Prerequisites:**
- [ ] Code review complete
- [ ] Critical/high issues resolved
- [ ] Security and TSA compliance verified

**Handoff:**
QA engineer executes test plan and verifies acceptance criteria

## Traceability

Every artifact is traceable back to requirements:

```
US-001 (User Story)
  ↓
REQ-001, REQ-002 (Requirements)
  ↓
AC-001, AC-002 (Acceptance Criteria)
  ↓
TASK-001, TASK-002 (Implementation Tasks)
  ↓
Test Cases (Unit, Integration, E2E)
  ↓
Code (Implementation)
```

**How to maintain traceability:**
1. **Spec:** Map REQ-xxx to user stories (US-xxx)
2. **Spec:** Map AC-xxx to REQ-xxx
3. **Plan:** Map TASK-xxx to REQ-xxx
4. **Tests:** Map test cases to AC-xxx
5. **Code:** Reference TASK-xxx in commit messages

**Example commit message:**
```
feat: implement account creation endpoint (TASK-002)

- Add POST /api/accounts endpoint
- Implement AccountService.CreateAccount
- Add validation for account name
- Add audit logging

Implements REQ-001, REQ-002 from spec-feature-account-creation.md
Satisfies AC-001, AC-002
```

## Best Practices

### DO:
✅ **Think first, code later** — Document requirements, spec, architecture before implementation
✅ **Iterate early** — Cheaper to change a spec than refactor code
✅ **Ask questions** — Discovery should be a conversation, not a checklist
✅ **Present options** — Architect should show trade-offs, not just one solution
✅ **Break down tasks** — Planner should create atomic tasks (1-5 days)
✅ **Map to requirements** — Every task, test, and line of code traces back to REQ-xxx
✅ **Define acceptance criteria** — Every REQ-xxx has testable AC-xxx
✅ **Use Given-When-Then** — Acceptance criteria should be clear and testable
✅ **Flag risks early** — Discovery, Architect, and Planner should identify risks proactively
✅ **Verify TSA compliance** — Check at Discovery, Architecture, Planning stages

### DON'T:
❌ Skip the conversation phase in discovery
❌ Write code before spec is approved
❌ Propose only one architectural option (show trade-offs)
❌ Create tasks larger than 5 days (break them down)
❌ Skip acceptance criteria
❌ Forget to map tasks to requirements
❌ Ignore TSA compliance until production
❌ Skip testing stages
❌ Leave open questions unresolved
❌ Deploy without code review and QA sign-off

## Prompts

Use these prompts to trigger workflow stages:

- `/amk-discovery` — Start discovery session
- `/amk-spec` — Generate specification from requirements
- `/amk-architecture` — Generate RFC from specification
- (Use `@planner`, `@code-review`, `@qa-engineer` directly for later stages)

## Summary

Spec-driven development ensures **clarity before code**. By following this workflow, teams:
- **Reduce rework** — Requirements and design are validated before implementation
- **Improve traceability** — Every line of code maps back to a requirement
- **Increase quality** — Clear acceptance criteria and testing strategy from the start
- **Manage risk** — Risks identified early, mitigations planned
- **Ensure compliance** — TSA constraints checked at every stage

**Workflow:** Discovery → Spec → Architecture → Plan → Implement → Review → Test
**Artifacts:** Requirements, Specifications, RFCs, Implementation Plans, Code, Tests
**Handoffs:** Clear gates between stages with approval criteria
