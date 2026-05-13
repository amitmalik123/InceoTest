---
description: 'Azure Repos Git conventions and branching strategy for AssetMark development'
applyTo: '**'
---

# Azure Repos — AssetMark Git Conventions

This document defines Git conventions, branching strategy, PR workflows, and code review practices for Azure Repos at AssetMark. All repositories must follow these standards to ensure code quality, traceability, and compliance.

## Branching Strategy

AssetMark uses **trunk-based development with feature flags** for most projects. This allows for continuous integration, simplified merges, and safer releases.

### Branch Structure

```
main (production-ready, protected)
  ├── develop (integration branch, protected)
  │    ├── feature/user-authentication
  │    ├── feature/dashboard-redesign
  │    └── bugfix/validation-error
  ├── release/1.5.0 (release preparation)
  └── hotfix/critical-security-patch (production fixes)
```

### Branch Types

#### `main` — Production-Ready Code

- **Purpose:** Represents code currently in production
- **Merges from:** `release/*` branches (after QA approval), `hotfix/*` branches (emergency fixes)
- **Protection:** Branch policies enforced (see below)
- **Deployment:** Automatic deployment to production (via CI/CD pipeline)
- **Lifetime:** Permanent

**Rules:**
- ✅ All code must pass CI/CD pipeline (build, test, security scan)
- ✅ Minimum 2 reviewers required for PR approval
- ✅ Work item linking required (Azure Boards)
- ✅ Comment resolution required before merge

#### `develop` — Integration Branch

- **Purpose:** Integration branch for active development
- **Merges from:** `feature/*`, `bugfix/*` branches
- **Merges to:** `release/*` branches (for release preparation)
- **Protection:** Branch policies enforced (see below)
- **Deployment:** Automatic deployment to Dev environment
- **Lifetime:** Permanent

**Rules:**
- ✅ All code must pass CI/CD pipeline
- ✅ Minimum 1 reviewer required for PR approval
- ✅ Work item linking required
- ✅ Comment resolution required before merge

#### `feature/*` — New Feature Development

- **Purpose:** Develop new features
- **Branched from:** `develop`
- **Merges to:** `develop` (via PR)
- **Naming convention:** `feature/short-description` or `feature/AB-12345-description` (with work item ID)
- **Lifetime:** Short-lived (delete after merge)

**Examples:**
- `feature/user-authentication`
- `feature/AB-1234-dashboard-redesign`
- `feature/export-to-excel`

**Rules:**
- Keep feature branches short-lived (< 1 week if possible)
- Rebase frequently from `develop` to avoid merge conflicts
- Use feature flags for incomplete features (merge to `develop` early, disable in production)

#### `bugfix/*` — Bug Fixes

- **Purpose:** Fix bugs discovered in Dev/Staging
- **Branched from:** `develop`
- **Merges to:** `develop` (via PR)
- **Naming convention:** `bugfix/short-description` or `bugfix/AB-12345-description`
- **Lifetime:** Short-lived (delete after merge)

**Examples:**
- `bugfix/validation-error`
- `bugfix/AB-5678-date-formatting`
- `bugfix/null-reference-exception`

#### `release/*` — Release Preparation

- **Purpose:** Prepare code for production release (final testing, versioning, release notes)
- **Branched from:** `develop`
- **Merges to:** `main` (after QA approval) AND `develop` (to sync any release-specific changes)
- **Naming convention:** `release/X.Y.Z` (semantic versioning)
- **Lifetime:** Short-lived (delete after merge to `main`)

**Examples:**
- `release/1.5.0`
- `release/2.0.0`

**Workflow:**
1. Branch from `develop`: `git checkout -b release/1.5.0 develop`
2. Bump version numbers, update release notes
3. Deploy to Staging for QA testing
4. Fix critical bugs in the release branch (cherry-pick to `develop` if needed)
5. Merge to `main` (via PR) when QA approves
6. Merge to `develop` (to sync any release-specific changes)
7. Tag the release: `git tag -a v1.5.0 -m 'Release 1.5.0'`
8. Delete the release branch

#### `hotfix/*` — Production Emergency Fixes

- **Purpose:** Fix critical bugs in production
- **Branched from:** `main`
- **Merges to:** `main` (via PR) AND `develop` (to sync the fix)
- **Naming convention:** `hotfix/short-description` or `hotfix/AB-12345-description`
- **Lifetime:** Short-lived (delete after merge)

**Examples:**
- `hotfix/security-vulnerability`
- `hotfix/AB-9999-data-loss-bug`
- `hotfix/payment-processing-error`

**Workflow:**
1. Branch from `main`: `git checkout -b hotfix/security-vulnerability main`
2. Fix the bug
3. Test thoroughly (regression testing)
4. Merge to `main` (via PR, expedited approval)
5. Merge to `develop` (to prevent regression)
6. Deploy to production immediately
7. Tag the hotfix: `git tag -a v1.5.1 -m 'Hotfix: Security vulnerability'`
8. Delete the hotfix branch

---

## Branch Policies

### Required Policies for `main`

Configure these policies in Azure Repos:

1. **Require Pull Request**
   - All changes to `main` must go through PR (no direct commits)

2. **Minimum Reviewers: 2**
   - At least 2 reviewers must approve
   - Original author cannot approve their own PR

3. **Build Validation**
   - CI/CD pipeline must pass (build, test, security scan)
   - Pipeline: `azure-pipelines-ci.yml`

4. **Work Item Linking Required**
   - PR must link to at least one Azure Boards work item (User Story, Bug, Task)

5. **Comment Resolution Required**
   - All PR comments must be resolved before merge

6. **Enforce Merge Strategy: Squash Merge**
   - Keeps commit history clean (one commit per PR)

7. **Limit Merge Types**
   - Allow: Squash merge
   - Block: Basic merge, rebase merge (to enforce clean history)

### Required Policies for `develop`

1. **Require Pull Request**
2. **Minimum Reviewers: 1**
3. **Build Validation**
4. **Work Item Linking Required**
5. **Comment Resolution Required**
6. **Enforce Merge Strategy: Squash Merge**

### Setup Instructions

1. Go to Azure Repos → Branches
2. Click `...` next to `main` → Branch policies
3. Enable the following:
   - ✅ **Require a minimum number of reviewers:** 2
   - ✅ **Check for linked work items:** Required
   - ✅ **Check for comment resolution:** Required
   - ✅ **Build validation:** Add `azure-pipelines-ci.yml`
   - ✅ **Limit merge types:** Squash merge only

---

## Commit Conventions

Use **Conventional Commits** for all commit messages. This enables automatic changelog generation and semantic versioning.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Changelog Section |
|------|-------------|-------------------|
| `feat` | New feature | Features |
| `fix` | Bug fix | Bug Fixes |
| `refactor` | Code refactoring (no functional change) | (not in changelog) |
| `docs` | Documentation changes | (not in changelog) |
| `test` | Add/update tests | (not in changelog) |
| `chore` | Build process, dependencies, tooling | (not in changelog) |
| `perf` | Performance improvements | Performance |
| `style` | Code formatting (no logic change) | (not in changelog) |
| `ci` | CI/CD changes | (not in changelog) |
| `revert` | Revert previous commit | (special handling) |

### Scope (Optional)

The scope indicates what part of the codebase is affected:

- `api` — API endpoints
- `ui` — User interface
- `db` — Database changes
- `auth` — Authentication/authorization
- `payment` — Payment processing
- `reporting` — Reporting features

**Examples:**
- `feat(api): add account creation endpoint`
- `fix(ui): resolve validation error on checkout page`
- `refactor(db): optimize account query performance`

### Subject

- Use **imperative mood** ("add feature" not "added feature")
- Keep to **50 characters** or less
- **No period** at the end
- **Lowercase** (unless proper noun)

❌ **Bad:**
- `Added the new feature.`
- `Fixing bug`
- `Update`

✅ **Good:**
- `add user authentication feature`
- `fix validation error on checkout page`
- `refactor account service for better testability`

### Body (Optional)

- Explain **what** changed and **why** (not how — the code shows how)
- Wrap at **72 characters** per line
- Leave one blank line between subject and body

**Example:**
```
feat(api): add account creation endpoint

This endpoint allows advisors to create new client accounts
via the API. Previously, accounts could only be created
through the UI, which was inefficient for bulk imports.

The endpoint validates account data, checks for duplicates,
and publishes an event to the CRM sync queue.
```

### Footer (Optional)

Use the footer for:
- **Azure Boards work item linking:** `AB#12345`
- **Breaking changes:** `BREAKING CHANGE: <description>`
- **Issue references:** `Closes AB#12345`

**Example:**
```
feat(api): change authentication flow to OAuth2

BREAKING CHANGE: The /api/auth/login endpoint no longer accepts
username/password. Clients must use OAuth2 authorization code flow.

AB#12345
```

### Work Item Linking

**Always reference Azure Boards work items** in commits:

```
feat(api): add account creation endpoint

AB#12345
```

**Syntax:**
- `AB#12345` — Links to work item 12345
- `Closes AB#12345` — Links and auto-closes work item on merge to `main`
- `Fixes AB#12345` — Same as `Closes`
- `Related to AB#12345` — Links without closing

**Why:**
- Traceability (which commits implement which features)
- Automatic work item updates (status changes on PR merge)
- Compliance (audit trail for regulatory requirements)

---

## Pull Request Conventions

### PR Title

PR titles should match the commit convention:

```
<type>(<scope>): <description>
```

**Examples:**
- `feat(api): add account creation endpoint`
- `fix(ui): resolve validation error on checkout page`
- `refactor(db): optimize account query performance`

**Why:**
- Consistent with commit messages (since we use squash merge)
- Enables automatic changelog generation
- Clear PR purpose at a glance

### PR Description Template

Use this template for all PRs:

```markdown
## What changed?
{Brief description of the changes}

## Why?
{Business context, problem being solved, or improvement being made}

## How to test?
{Step-by-step instructions for reviewers to verify the changes}

1. ...
2. ...
3. ...

## Screenshots (if UI changes)
{Attach screenshots or screen recordings}

## Checklist
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Documentation updated (if needed)
- [ ] Breaking changes documented (if any)
- [ ] Security review completed (if handling PII or auth)
- [ ] Performance tested (if high-traffic endpoint)

## Linked Work Items
AB#12345, AB#67890
```

### PR Size

**Keep PRs small** — aim for < 400 lines of code changed.

**Why:**
- Faster reviews (easier to review 200 lines than 2000)
- Fewer bugs (smaller changes = less risk)
- Easier rollback (if something breaks)

**If PR is large:**
- Break into multiple PRs (feature A, then feature B)
- Use feature flags to merge incomplete work (disable in production)

### Reviewers

**Add appropriate reviewers:**
- **Code owners** — Auto-assigned via `CODEOWNERS` file
- **Domain experts** — For complex business logic
- **Security team** — For auth/PII changes
- **DBA** — For database schema changes

**Assign reviewers explicitly:**
- Go to PR → Reviewers → Add
- Don't rely on auto-assignment for critical changes

---

## Code Review in Azure Repos

### Review Workflow

1. **Reviewer gets notification** (email, Azure DevOps notification)
2. **Reviewer reads PR description** (understand context)
3. **Reviewer examines code changes** (logic, tests, style)
4. **Reviewer leaves comments** (suggestions, questions, concerns)
5. **Author responds to comments** (clarifications, fixes)
6. **Reviewer marks threads as resolved** (when satisfied)
7. **Reviewer approves PR** (or requests changes)

### Comment Types

**Thread-based comments:**
- **General comment** — Applies to the entire PR
- **File comment** — Applies to a specific file
- **Line comment** — Applies to a specific line of code

**Comment actions:**
- **Active** — Unresolved issue (must address before merge)
- **Resolved** — Issue addressed or dismissed
- **Won't fix** — Issue acknowledged but not blocking (document why)

### Review States

| State | Meaning | Next Step |
|-------|---------|-----------|
| **Approved** | Changes look good, ready to merge | Author can merge |
| **Approved with suggestions** | Good overall, minor non-blocking suggestions | Author can merge after addressing (optional) |
| **Wait for author** | Changes requested, cannot merge yet | Author must address comments |
| **Rejected** | Fundamental issues, needs major rework | Author must rework and resubmit |

### Comment Resolution

**All comments must be resolved before merge:**
- Author resolves comments after addressing (or marks "Won't fix" with rationale)
- Reviewer can resolve their own comments if satisfied

**"Won't fix" rationale examples:**
- "Style preference, not blocking"
- "Out of scope for this PR, will address in AB#99999"
- "Discussed offline, agreed to keep as-is"

### Code Review Checklist

Reviewers should check:

**Functionality:**
- [ ] Code does what the PR description claims
- [ ] Edge cases are handled
- [ ] Error handling is present and appropriate

**Tests:**
- [ ] Unit tests cover new/changed logic
- [ ] Integration tests cover API endpoints
- [ ] Test names are clear and descriptive

**Security:**
- [ ] No secrets in code (use Key Vault)
- [ ] Input validation is present
- [ ] PII is encrypted (if applicable)
- [ ] Authentication/authorization is enforced

**Performance:**
- [ ] No N+1 queries (database)
- [ ] Caching is used where appropriate
- [ ] Large datasets are paginated

**Style & Maintainability:**
- [ ] Code follows AssetMark conventions (see `.editorconfig`)
- [ ] Variable/method names are clear
- [ ] Complex logic has comments explaining "why"
- [ ] No commented-out code (use Git history instead)

**Documentation:**
- [ ] API changes are documented (Swagger/OpenAPI)
- [ ] README updated (if setup instructions changed)
- [ ] Architecture docs updated (if design changed)

---

## Merge Strategies

### Squash Merge (Preferred)

**What it does:**
- Combines all commits in the PR into a single commit
- Uses PR title as the commit message
- Keeps `main` history clean (one commit per feature)

**When to use:**
- Default for all PRs to `main` and `develop`

**Example:**
```
Before squash:
  - feat: add account endpoint
  - fix typo
  - address PR comments
  - fix tests

After squash:
  feat(api): add account creation endpoint
```

### Rebase Merge (Not Recommended)

**What it does:**
- Replays all commits from the PR onto the target branch
- Preserves original commit messages
- Can create cluttered history

**When to use:**
- Only for PRs with clean, atomic commits
- Not recommended for AssetMark (use squash instead)

### Basic Merge (Blocked)

**What it does:**
- Creates a merge commit
- Preserves all commits and branch structure
- Can create messy history ("merge hell")

**When to use:**
- **Never** — blocked by branch policies

---

## Git Best Practices

### Commit Frequency

**Commit early and often:**
- Commit logical units of work (one feature/fix per commit)
- Push to your feature branch daily (backup + visibility)
- Don't wait until PR is "perfect" to push

### Commit Atomicity

**Each commit should be self-contained:**
- Builds successfully
- Tests pass
- Represents a single logical change

❌ **Bad:**
- Commit 1: Half of feature A
- Commit 2: Other half of feature A + typo fix + unrelated change

✅ **Good:**
- Commit 1: Feature A (complete, tested)
- Commit 2: Typo fix
- Commit 3: Unrelated change

### Rebase vs Merge

**Use rebase to update feature branches:**
```bash
# Update feature branch with latest changes from develop
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
```

**Why rebase:**
- Keeps history linear (easier to read)
- Avoids unnecessary merge commits

**When to merge:**
- When updating `develop` or `main` (use PR, not direct merge)

### Branching from Branches

**Avoid branching from feature branches:**

❌ **Bad:**
```
develop
  └── feature/A
       └── feature/B  # Dependent on feature/A
```

✅ **Good:**
```
develop
  ├── feature/A
  └── feature/B  # Independent, can merge separately
```

**If you must:**
- Wait for feature/A to merge to `develop`
- Then branch feature/B from `develop`

---

## Git LFS (Large File Storage)

Use Git LFS for **large binary files** (images, compiled assets, videos).

**Setup:**
```bash
# Install Git LFS
git lfs install

# Track specific file types
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.pdf"
git lfs track "*.mp4"

# Commit .gitattributes
git add .gitattributes
git commit -m "chore: configure Git LFS for images and PDFs"
```

**Why Git LFS:**
- Binary files don't compress well in Git
- Large files slow down clones and fetches
- Git LFS stores pointers in Git, actual files in LFS storage

**File size threshold:**
- Files > 1 MB should use Git LFS
- Files < 1 MB can be committed normally

---

## Security

### No Secrets in Repos

**Never commit secrets:**
- API keys
- Connection strings
- Passwords
- Certificates
- Private keys

**Use `.gitignore` to prevent accidental commits:**
```gitignore
# .gitignore
appsettings.Development.json
appsettings.Local.json
*.pfx
*.pem
.env
.env.local
secrets.json
```

**Scan for credentials with CredScan:**
- Azure DevOps pipeline task: `CredScan@3`
- Runs on every PR to detect secrets
- Blocks merge if secrets detected

**If you commit a secret accidentally:**
1. **Rotate the secret immediately** (generate new API key, change password)
2. Remove the secret from Git history:
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   git filter-repo --path secrets.json --invert-paths
   ```
3. Force push (requires admin permissions)
4. Notify security team

### Code Scanning

**Enable Azure DevOps security scanning:**
- **Dependency scanning** — Detect vulnerable npm/NuGet packages
- **Code scanning** — Static analysis (SonarQube, Checkmarx)
- **Secret scanning** — CredScan

**Run scans on every PR:**
```yaml
# azure-pipelines-ci.yml
- task: CredScan@3
  displayName: 'Scan for credentials'

- task: DependencyCheck@6
  displayName: 'Check for vulnerable dependencies'
```

---

## Summary

Azure Repos at AssetMark follows these principles:

1. **Trunk-Based Development** — Short-lived feature branches, merge frequently
2. **Conventional Commits** — Structured commit messages for changelog generation
3. **Work Item Linking** — All commits reference Azure Boards work items (`AB#12345`)
4. **PR-Based Workflow** — All changes via PR, no direct commits to `main`/`develop`
5. **Squash Merge** — Keep commit history clean (one commit per PR)
6. **Branch Policies** — Minimum reviewers, build validation, work item linking
7. **Code Review** — Thread-based comments, comment resolution required
8. **No Secrets** — Use `.gitignore` and CredScan to prevent credential leaks
9. **Git LFS** — Use for large binary files (> 1 MB)
10. **Security Scanning** — CredScan, dependency checks, static analysis on every PR

**For questions or exceptions, contact:** DevOps Lead or submit RFC for approval.


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
