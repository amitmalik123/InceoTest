---
name: 'code-review-workflow'
description: 'Orchestration logic for delegating code reviews to type-specific agents and merging findings into a unified report'
user-invokable: false
---

# Code Review Workflow

This skill defines the orchestration workflow for the code review agent — how to delegate to type-specific reviewers, merge findings, and produce a unified actionable report.

## Architecture Rationale

**Problem:** Monolithic code review agents load all instructions (C#, TypeScript, SQL, CSS, etc.) into a single context, wasting tokens and limiting depth.

**Solution:** Delegate to specialized agents:
- **C# Review Agent** — Loads only C#, .NET, security, architecture instructions
- **TypeScript Review Agent** — Loads only TypeScript, React, accessibility instructions
- **SQL Review Agent** — Loads only SQL, database, security instructions
- **Frontend Assets Review Agent** — Loads only CSS, HTML, accessibility instructions

**Benefits:**
- ~40-50% less context per agent
- Parallel execution of type-specific reviews
- Each agent sees all files of its type together (cross-file analysis)
- Unified output report for developer

## Review Workflow Steps

### Step 0: Setup Output Location

Before starting the review:

1. **Check if `.codereview/` folder exists** - If not, create it in the project root
2. **Check `.gitignore`** - If `.codereview` or `.codereview/` is NOT in `.gitignore`, add it:
   ```
   # Code review reports (auto-generated)
   .codereview/
   ```

### Step 1: Determine Review Scope

Ask the user to specify what code should be reviewed:

**Available Review Scopes:**
1. **Staged/Modified Changes** - Use the `search/changes` tool to detect files that are staged or modified. Do NOT run `git diff --staged` or any git terminal commands — use `search/changes` instead. If it returns no results, ask the user which files to review.
2. **Branch Changes** - Review all changes in current branch vs main/master
3. **Specific Files** - User provides file paths or glob patterns (e.g., `src/Controllers/*.cs`)
4. **Directory** - Review all code in a specific directory
5. **Full Codebase** - Comprehensive review (note: may take longer for large repos)

**Prompt:** "What would you like me to review? Please choose a scope or provide specific file paths."

### Step 2: Discover and Group Files by Type

Based on the scope, identify all files and group them by reviewer:

| File Pattern | Delegate To |
|--------------|-------------|
| `**/*.cs`, `**/*.csproj` | `@CSharpReview` |
| `**/*.ts`, `**/*.tsx`, `**/*.js`, `**/package.json` | `@TypeScriptReview` |
| `**/*.sql` | `@SQLReview` |
| `**/*.css`, `**/*.scss`, `**/*.html` | `@FrontendAssetsReview` |
| `**/*.md` | Review directly (simple documentation check) |

**Exclude from review:**
- `node_modules/`
- `bin/`
- `obj/`
- `dist/`
- `build/`
- `.git/`
- `.codereview/`
- `*.min.js`, `*.min.css` (minified files)

### Step 3: Spawn Type-Specific Agents (Parallel)

For each file group, spawn the appropriate agent **in parallel** using the `agent` tool.

**Delegation format:**
```
@CSharpReview Review these C# files for issues:
- path/to/File1.cs
- path/to/File2.cs
- path/to/Project.csproj

@TypeScriptReview Review these TypeScript/React files for issues:
- src/components/Button.tsx
- src/hooks/useAuth.ts
- package.json

@SQLReview Review these SQL files for issues:
- migrations/001_CreateTables.sql
- stored-procedures/GetAccounts.sql

@FrontendAssetsReview Review these CSS/SCSS/HTML files for issues:
- styles/main.scss
- public/index.html
```

**Expected Response Format:**
Each agent returns JSON findings:
```json
{
  "files_reviewed": ["path/to/file.cs"],
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "file": "path/to/file.cs",
      "line": 42,
      "title": "Issue title",
      "issue": "Description",
      "problem": "Why it matters",
      "suggested_fix": "Code suggestion"
    }
  ],
  "positive_aspects": ["What was done well"]
}
```

### Step 4: Merge All Findings

Collect findings from all agents and:

1. **Combine** — Merge all `findings` arrays into one list
2. **Sort** — Order by severity: Critical > High > Medium > Low
3. **Deduplicate** — If multiple agents report the same issue, keep the most detailed one
4. **Merge positive aspects** — Combine all `positive_aspects` arrays
5. **Cross-cutting concerns** — Identify patterns across multiple file types (e.g., missing auth on both frontend and backend)

### Step 5: Generate Unified Report

Write to: `.codereview/YYYY-MM-DD-HHmm-[ComponentName]-review.md`

**Filename format:**
- `YYYY-MM-DD` = Current date (e.g., 2025-02-09)
- `HHmm` = Current time in 24-hour format (e.g., 1430 for 2:30 PM)
- `[ComponentName]` = Primary component being reviewed (e.g., `PermissionsController` or `UserFeature`)

**Report structure:**

```markdown
# [Component Name] — Code Review (YYYY-MM-DD HH:mm)

## 1. Executive Summary

- **Files reviewed**: X C# files, Y TypeScript files, Z SQL files
- **Scope**: Brief description of what was reviewed
- **Overall assessment**: Summary of code quality and main concerns
- **Recommendation**: Approve / Approve with Comments / Request Changes / Block

---

## 2. Issue Categories

### 🚨 Critical Issues
(Only include if critical issues exist)

**Summary:** [Brief explanation of critical issues found]

1. **[Issue Title]** (file.cs:42) - Critical
   - **Issue:** [Description]
   - **Problem:** [Why it matters]
   - **Suggested Fix:** [Code or guidance]

### ⚠️ High Priority Issues
(Only include if high issues exist)

### 📝 Medium Priority Issues
(Only include if medium issues exist)

### 💡 Low Priority (Nice to Have)
(Only include if low issues exist)

---

## 🔒 Security Considerations
(Only if security issues found - merged from all agents)

- [Security finding 1]
- [Security finding 2]

## ✅ Testing Gaps
(Only if testing gaps found - merged from all agents)

- [Missing test coverage area 1]
- [Missing test coverage area 2]

## 🌟 Positive Aspects
(Always include - merged from all agents)

- [Good practice 1]
- [Good practice 2]

---

## 📋 Summary Checklist for Developer

### Must Fix Before Merge (Critical)
- [ ] [Critical issue 1] (file:line)
- [ ] [Critical issue 2] (file:line)

### Should Fix Before Merge (High Priority)
- [ ] [High issue 1] (file:line)
- [ ] [High issue 2] (file:line)

### Recommended Improvements (Medium)
- [ ] [Medium issue 1] (file:line)
- [ ] [Medium issue 2] (file:line)

### Nice to Have (Low)
- [ ] [Low issue 1] (file:line)

---

## 🎓 Recommendations for Next Steps

1. [Prioritized action item 1]
2. [Prioritized action item 2]
3. [Suggestion for future improvements]

## Overall Assessment

[Narrative summary of the code quality, key strengths, and areas for improvement. Should be 2-4 paragraphs providing context beyond the checklist.]

---

*Review completed by CodeReview orchestrator. Generated by [AgentName] at [Timestamp].*
*End of report.*
```

**Report Guidelines:**

1. **Be Concise** — Exclude empty sections. If no critical issues, don't include "Critical Issues" section.
2. **Be Constructive** — Explain WHY something is an issue, not just WHAT
3. **Be Actionable** — Every issue should have a clear suggested fix
4. **Prioritize** — Critical and High issues at the top, Low at the bottom
5. **Acknowledge good work** — Always include Positive Aspects section

## Agent Delegation Map

| Agent | File Types | Instructions Loaded |
|-------|------------|---------------------|
| `@CSharpReview` | `.cs`, `.csproj` | csharp, security, architecture, testing, documentation, performance, api-design, code-quality, dependencies, file-organization |
| `@TypeScriptReview` | `.ts`, `.tsx`, `.js`, `package.json` | typescript, security, accessibility, code-quality, testing, performance, dependencies, documentation, file-organization |
| `@SQLReview` | `.sql` | sql, security, performance |
| `@FrontendAssetsReview` | `.css`, `.scss`, `.html` | accessibility, code-quality, performance |

**Note:** All agents include:
- Enhanced bug & logic detection
- Edge case handling
- Memory leak detection
- Code smell patterns
- Security vulnerability scanning

## Cross-Cutting Concerns Detection

When merging findings, identify patterns that span multiple file types:

### Missing Authorization
- Backend: No `[Authorize]` attribute on controller action
- Frontend: No auth check before rendering component
- **Combined finding:** End-to-end authorization gap

### Data Validation Gap
- Frontend: No input validation
- Backend: No DTO validation with FluentValidation
- SQL: No constraints on table columns
- **Combined finding:** Data integrity risk

### Performance Issues
- Backend: N+1 query in EF Core
- Frontend: Component re-renders on every state change
- **Combined finding:** End-to-end performance concern

### Accessibility Issues
- HTML: Missing semantic elements
- CSS: Insufficient color contrast
- TypeScript: No keyboard navigation support
- **Combined finding:** Complete accessibility barrier

## Feedback Only Mode

**The orchestrator and all sub-agents are READ-ONLY reviewers.**

**Never:**
- Apply fixes to user code
- Offer to apply or implement fixes
- Modify any source code files (except `.codereview/` folder and `.gitignore`)
- Ask if the user wants you to fix issues

**Always:**
- Provide clear explanations of issues
- Suggest specific fixes for the developer to implement manually
- Acknowledge good practices
- Prioritize issues so developer knows what matters most

## Error Handling

If a type-specific agent fails:
1. Log the error in the report
2. Continue with other agents
3. Mark the failed file type as "Not Reviewed" in the report
4. Include a note: "⚠️ [FileType] review failed - please run manually"

## Performance Optimization

For large codebases (>100 files):
- Recommend scoped review instead of full codebase
- Process file groups in batches of 20-30 files per agent
- Use streaming if available to show progress

## Output File Management

- Keep last 10 review reports in `.codereview/`
- Older reports can be archived or deleted
- Report filenames sorted by date allow easy chronological browsing
- Add `.codereview/` to `.gitignore` so reports don't pollute version control

## Coverage Standard

AssetMark enforces **85% minimum line and branch coverage**. All code produced or reviewed using this skill must maintain this threshold.
