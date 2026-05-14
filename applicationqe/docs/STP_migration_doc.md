# STP Branch Creation, Migration & Monorepo Execution Plan

## TL;DR

Cut a `team/stp` branch from `develop`, migrate current `ES2PlaywrightPython` work into it
via a **merge strategy** to preserve history, then reorganize the flat `qeautomation` structure
into the `applicationqe/` monorepo layout already partially scaffolded in Azure DevOps.
CI/CD pipelines get cloned per STP sub-domain with path-based triggers.

---

## Current State

| Item | Value |
|---|---|
| Repository | `AssetmarkInc / ProdEng / qeautomation` (Azure DevOps) |
| Active branch | `ES2PlaywrightPython` |
| Pipeline | `azurePipeline_ES2.yaml` |
| Agent pool | `ubuntu2204-qa` |
| Test runner | `tests/bdd/test_runners/test_add_ach.py` (loads all scenarios) |
| Feature files | `tests/bdd/features/*.feature` (flat, single folder) |
| Step files | `tests/bdd/steps/*.py` (flat, ~27 files) |
| Page objects | `pages/*.py` (flat, ~50 files) |

**STP sub-domains already visible in Azure DevOps `applicationqe/`:**
- `stp-aip`
- `stp-contributions`
- `stp-ict`
- `stp-journals`
- `stp-manageBene`
- `stp-oaTradingTool`
- `stp-swp`
- `stp-updateAddress`

---

## Target State

```
qeautomation/
└── applicationqe/
    ├── azure-pipelines/
    │   ├── stp-contributions.yml
    │   ├── stp-aip.yml
    │   ├── stp-journals.yml
    │   ├── stp-ict.yml
    │   ├── stp-manageBene.yml
    │   ├── stp-oaTradingTool.yml
    │   ├── stp-swp.yml
    │   ├── stp-updateAddress.yml
    │   └── full_regression.yml
    ├── config/
    │   ├── shared/
    │   └── stp/
    │       ├── stp-contributions/
    │       ├── stp-aip/
    │       ├── stp-journals/
    │       ├── stp-ict/
    │       ├── stp-manageBene/
    │       ├── stp-oaTradingTool/
    │       ├── stp-swp/
    │       └── stp-updateAddress/
    ├── pages/
    │   ├── shared/                  # base_page.py, login_page.py, docusign_page.py, etc.
    │   └── stp/
    │       ├── stp-contributions/
    │       ├── stp-aip/
    │       ├── stp-manageBene/
    │       ├── stp-oaTradingTool/
    │       ├── stp-swp/
    │       └── stp-updateAddress/
    ├── tests/
    │   ├── features/
    │   │   └── stp/
    │   │       ├── stp-contributions/   # Contribution.feature, Withdrawal.feature
    │   │       ├── stp-aip/             # AIP.feature, EstablishAIP.feature
    │   │       ├── stp-journals/
    │   │       ├── stp-ict/
    │   │       ├── stp-manageBene/      # Manage_bene.feature
    │   │       ├── stp-oaTradingTool/   # OA_tool.feature
    │   │       ├── stp-swp/             # SWP.feature
    │   │       └── stp-updateAddress/   # Address_change.feature, add_ACH.feature
    │   └── steps/
    │       ├── shared/                  # common_steps.py, login_steps.py, etc.
    │       └── stp/
    │           ├── stp-contributions/
    │           ├── stp-aip/
    │           ├── stp-manageBene/
    │           ├── stp-oaTradingTool/
    │           ├── stp-swp/
    │           └── stp-updateAddress/
    ├── utils/                           # Fully shared: allure_logger, database, etc.
    ├── conftest.py
    ├── pyproject.toml
    └── requirements.txt
```

---

## File Migration Mapping

| Current path | Target path |
|---|---|
| `tests/bdd/features/Contribution.feature` | `applicationqe/tests/features/stp/stp-contributions/` |
| `tests/bdd/features/Withdrawal.feature` | `applicationqe/tests/features/stp/stp-contributions/` |
| `tests/bdd/features/AIP.feature` | `applicationqe/tests/features/stp/stp-aip/` |
| `tests/bdd/features/EstablishAIP.feature` | `applicationqe/tests/features/stp/stp-aip/` |
| `tests/bdd/features/SWP.feature` | `applicationqe/tests/features/stp/stp-swp/` |
| `tests/bdd/features/Manage_bene.feature` | `applicationqe/tests/features/stp/stp-manageBene/` |
| `tests/bdd/features/OA_tool.feature` | `applicationqe/tests/features/stp/stp-oaTradingTool/` |
| `tests/bdd/features/Address_change.feature` | `applicationqe/tests/features/stp/stp-updateAddress/` |
| `tests/bdd/features/add_ACH.feature` | `applicationqe/tests/features/stp/stp-updateAddress/` |
| `tests/bdd/features/roth_conversion.feature` | `applicationqe/tests/features/stp/stp-contributions/` |
| `pages/establish_aip_*.py` | `applicationqe/pages/stp/stp-aip/` |
| `pages/swp_*.py` | `applicationqe/pages/stp/stp-swp/` |
| `pages/manage_bene_*.py` | `applicationqe/pages/stp/stp-manageBene/` |
| `pages/mimo_*.py` | `applicationqe/pages/stp/stp-contributions/` |
| `pages/oa_tool_*.py` | `applicationqe/pages/stp/stp-oaTradingTool/` |
| `pages/base_page.py`, `pages/login_page.py`, `pages/docusign_page.py`, `pages/outlook_page.py` | `applicationqe/pages/shared/` |
| `utils/` | `applicationqe/utils/` |
| `config/` | `applicationqe/config/shared/` + per-domain splits |
| `tests/bdd/test_runners/test_add_ach.py` | Split into per-domain `test_runner.py` files |

---

## Phase 1 — Branch Strategy

### 1.1 Create the STP team branch from `develop`

```bash
git fetch origin
git checkout develop
git pull origin develop
git checkout -b team/stp
git push origin team/stp
```

### 1.2 Naming conventions

| Branch type | Pattern | Example |
|---|---|---|
| Team integration | `team/stp` | `team/stp` |
| Feature | `team/stp/feature/<jira-id>-description` | `team/stp/feature/STP-123-add-ict-tests` |
| Hotfix | `team/stp/hotfix/<jira-id>-description` | `team/stp/hotfix/STP-456-fix-login-step` |
| Release | `team/stp/release/vX.Y` | `team/stp/release/v1.0` |

### 1.3 Keeping `team/stp` synced with `develop` (weekly)

```bash
git checkout team/stp
git fetch origin
git merge origin/develop --no-ff -m "chore: sync develop into team/stp $(date +%Y-%m-%d)"
git push origin team/stp
```

Use `--no-ff` (not rebase) so sync commits are clearly identifiable in history.

### 1.4 Feature branch workflow

```
develop
  └── team/stp                                  ← long-lived integration branch
        └── team/stp/feature/STP-123-feature    ← feature work
              └── PR → team/stp
```

Never commit directly to `team/stp`. All work comes via PR from `team/stp/feature/*`.

---

## Phase 2 — Migration from `ES2PlaywrightPython` → `team/stp`

**Strategy: Merge (not rebase)** — rebase rewrites SHAs and breaks anyone still working on `ES2PlaywrightPython`.

### 2.1 Backup before anything

```bash
git checkout ES2PlaywrightPython
git tag backup/ES2PlaywrightPython-pre-migration
git push origin backup/ES2PlaywrightPython-pre-migration
```

### 2.2 Inspect the diff

```bash
git log origin/develop..origin/ES2PlaywrightPython --oneline
git diff origin/develop...origin/ES2PlaywrightPython --stat
```

### 2.3 Merge ES2 work into `team/stp`

```bash
git checkout team/stp
git merge origin/ES2PlaywrightPython --no-ff -m "feat: migrate ES2PlaywrightPython work into team/stp"
```

### 2.4 Conflict resolution strategy

| File type | Resolution |
|---|---|
| Pipeline YAMLs (`azurePipeline_*.yaml`) | Accept `team/stp` version (from develop) |
| Config files (`config/*.yaml`) | Accept `team/stp` version |
| Feature files (`*.feature`) | Accept `ES2PlaywrightPython` version |
| Step files (`*_steps.py`) | Accept `ES2PlaywrightPython` version |
| Page objects (`pages/*.py`) | Accept `ES2PlaywrightPython` version |

```bash
# Open all conflict files in VS Code
git mergetool
# Or resolve manually then:
git add .
git commit
```

### 2.5 Validate before pushing

```bash
python -m pytest tests/ --collect-only -q     # all tests must collect
python -m mypy pages/ tests/ --ignore-missing-imports
python -m flake8 pages/ tests/
```

### 2.6 Push and raise draft PR for review

```bash
git push origin team/stp
# Open PR: team/stp → develop (draft, for review only — do not merge yet)
```

---

## Phase 3 — Monorepo Restructure

### 3.1 Move files using `git mv` (preserves commit history)

```bash
# Create target directories
mkdir -p applicationqe/tests/features/stp/stp-contributions
mkdir -p applicationqe/tests/steps/stp/stp-contributions
mkdir -p applicationqe/pages/stp/stp-contributions
mkdir -p applicationqe/pages/shared
# ... repeat for each sub-domain

# Move feature files
git mv tests/bdd/features/Contribution.feature applicationqe/tests/features/stp/stp-contributions/
git mv tests/bdd/features/Withdrawal.feature   applicationqe/tests/features/stp/stp-contributions/
git mv tests/bdd/features/AIP.feature          applicationqe/tests/features/stp/stp-aip/
git mv tests/bdd/features/EstablishAIP.feature applicationqe/tests/features/stp/stp-aip/
git mv tests/bdd/features/SWP.feature          applicationqe/tests/features/stp/stp-swp/
git mv tests/bdd/features/Manage_bene.feature  applicationqe/tests/features/stp/stp-manageBene/
git mv tests/bdd/features/OA_tool.feature      applicationqe/tests/features/stp/stp-oaTradingTool/
git mv tests/bdd/features/Address_change.feature applicationqe/tests/features/stp/stp-updateAddress/
git mv tests/bdd/features/add_ACH.feature      applicationqe/tests/features/stp/stp-updateAddress/

# Move shared pages
git mv pages/base_page.py       applicationqe/pages/shared/
git mv pages/login_page.py      applicationqe/pages/shared/
git mv pages/docusign_page.py   applicationqe/pages/shared/
git mv pages/outlook_page.py    applicationqe/pages/shared/
git mv utils/                   applicationqe/utils/

git commit -m "refactor: move files into applicationqe monorepo structure"
```

### 3.2 Update `scenarios()` paths in test runners

Each sub-domain gets its own `test_runner.py`:

```python
# applicationqe/tests/features/stp/stp-contributions/test_runner.py
from pytest_bdd import scenarios
from tests.steps.shared.common_steps import *        # noqa
from tests.steps.stp.stp_contributions_steps import *  # noqa

scenarios("Contribution.feature")
scenarios("Withdrawal.feature")
```

### 3.3 Update `pyproject.toml` testpaths

```toml
[tool.pytest.ini_options]
testpaths = ["applicationqe/tests"]
```

---

## Phase 4 — CI/CD Pipeline Changes

### 4.1 Clone `azurePipeline_ES2.yaml` per sub-domain

Key changes per pipeline:
- `trigger.paths.include` → only that sub-domain's folders
- `parameters.marker.default` → sub-domain pytest marker
- `displayName` → sub-domain name

```yaml
# applicationqe/azure-pipelines/stp-contributions.yml
trigger:
  branches:
    include:
      - team/stp
  paths:
    include:
      - applicationqe/tests/features/stp/stp-contributions/**
      - applicationqe/tests/steps/stp/stp-contributions/**
      - applicationqe/pages/stp/stp-contributions/**

parameters:
  - name: marker
    default: "stp_contributions"
    values:
      - stp_contributions
      - smoke
```

### 4.2 Full regression pipeline (nightly on `team/stp`)

```yaml
# applicationqe/azure-pipelines/full_regression.yml
schedules:
  - cron: "0 2 * * *"
    branches:
      include:
        - team/stp
    always: true

jobs:
  - template: stp-contributions.yml
  - template: stp-aip.yml
  - template: stp-swp.yml
  # ... etc
```

### 4.3 Add pytest markers per sub-domain

In `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "stp_contributions: STP Contributions sub-domain tests",
    "stp_aip: STP AIP sub-domain tests",
    "stp_swp: STP SWP sub-domain tests",
    "stp_manageBene: STP Manage Beneficiary tests",
    "stp_oaTradingTool: STP OA Trading Tool tests",
    "stp_updateAddress: STP Update Address / Add ACH tests",
]
```

---

## Phase 5 — Validation & Rollback Plan

### 5.1 Pre-migration checklist

- [ ] Backup tag created: `backup/ES2PlaywrightPython-pre-migration`
- [ ] `git stash` on all developer machines before migration starts
- [ ] All open PRs merged or acknowledged
- [ ] Pipeline ran green on `ES2PlaywrightPython` as baseline (screenshot saved)
- [ ] Azure DevOps variable group `qa-pipelines-shared-config` documented
- [ ] All team members notified of `ES2PlaywrightPython` freeze date

### 5.2 Post-migration validation

```bash
# 1. All tests collect
pytest applicationqe/ --collect-only -q

# 2. Smoke suite passes
pytest -m smoke --env test11

# 3. Allure report generates
pytest -m smoke --env test11 --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report

# 4. Type and lint check
mypy applicationqe/ --ignore-missing-imports
flake8 applicationqe/
```

### 5.3 Rollback strategy

**Option A — Revert the merge commit on `team/stp`:**
```bash
git log --oneline team/stp -5       # find the merge commit SHA
git revert -m 1 <merge-commit-sha>
git push origin team/stp
```

**Option B — Restore from backup tag:**
```bash
git checkout backup/ES2PlaywrightPython-pre-migration -b recovery/stp
git push origin recovery/stp
```

**Option C — If monorepo restructure is the issue, revert the mv commit:**
```bash
git revert HEAD   # the git mv commit
git push origin team/stp
```

Keep `ES2PlaywrightPython` branch alive and read-only for **30 days** after cutover.

---

## Phase 6 — Team Collaboration Plan

### 6.1 Branch protection rules (Azure DevOps → Repos → Branches → Policies)

| Branch | Rules |
|---|---|
| `develop` | Require PR + 2 reviewers + all pipelines green + no active work items |
| `team/stp` | Require PR + 1 reviewer + pipeline green on changed paths |
| `team/stp/feature/*` | No restrictions — open for developer push |

### 6.2 CODEOWNERS file

```
# applicationqe/CODEOWNERS
applicationqe/tests/features/stp/stp-contributions/   @stp-contributions-team
applicationqe/tests/features/stp/stp-aip/             @stp-aip-team
applicationqe/tests/features/stp/stp-swp/             @stp-swp-team
applicationqe/tests/features/stp/stp-manageBene/      @stp-managebene-team
applicationqe/tests/features/stp/stp-oaTradingTool/   @stp-oatool-team
applicationqe/tests/features/stp/stp-updateAddress/   @stp-updateaddress-team
applicationqe/utils/                                   @qa-platform-team
applicationqe/pages/shared/                            @qa-platform-team
applicationqe/azure-pipelines/                         @qa-platform-team
```

### 6.3 Release management

```bash
# When STP features are release-ready:
# PR: team/stp → develop (full regression must pass)
# PR: develop → main (release gate)
git tag stp/v1.0.0
git push origin stp/v1.0.0
```

---

## Phase 7 — Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Merge conflicts in shared pages (`base_page.py`, `login_page.py`) | High | Medium | Merge `develop` first, resolve before migrating ES2 |
| `import` paths break after `git mv` | High | High | Run `--collect-only` as mandatory gate; update all `from pages.X` to `from applicationqe.pages.X` |
| Sub-domain pipelines not triggering on `team/stp` | Medium | High | Verify branch trigger section; test with dummy commit |
| Shared step definitions conflict across sub-domains | Medium | Medium | `common_steps.py` stays in `applicationqe/tests/steps/shared/`; sub-domains import from there |
| Developers bypass migration and keep committing to ES2 | Low | Medium | Set ES2 as read-only in Azure DevOps branch policies after freeze date |
| Azure DevOps service connections broken in new pipelines | Low | High | Copy variable group reference `qa-pipelines-shared-config` to all new YAMLs |
| Test data CSV paths break after restructure | Medium | Medium | Update `data/` references in `config/settings.py`; move CSVs to `applicationqe/data/` |

---

## Rollout Timeline

| Week | Activity | Owner |
|---|---|---|
| Week 1 | Create `team/stp`, create backup tag, communicate ES2 freeze date to team | DevOps lead |
| Week 2 | Merge ES2 → `team/stp`, resolve conflicts, validate with `--collect-only` + smoke | QA lead |
| Week 3 | `git mv` restructure into `applicationqe/`, update imports and test runners | QA engineer |
| Week 4 | Clone pipelines per sub-domain, validate path triggers, run full regression | DevOps + QA |
| Week 5 | Add CODEOWNERS, set branch policies, add pytest markers, retire ES2 (read-only) | DevOps lead |

---

## Best Practices Checklist

- [ ] Never commit directly to `team/stp` — always via PR
- [ ] Always use `git mv` (not OS-level move) to preserve history
- [ ] Run `--collect-only` after every structural change
- [ ] `utils/` and `pages/shared/` are owned by `@qa-platform-team` — changes require 2 reviewers
- [ ] Sync `develop` into `team/stp` every Monday before new feature work starts
- [ ] Every new sub-domain pipeline must include path-based triggers
- [ ] All new pytest markers must be registered in `pyproject.toml`
- [ ] Keep backup tags for all major migration steps
- [ ] Do not rename `develop` or `main` — Azure DevOps pipelines reference them by name
- [ ] Document the `azureSubscription` service connection value in the team wiki before cloning pipelines

---

## Phase 9 — Develop Branch Readiness & Migration Validation

### 9.1 Compare `ES2PlaywrightPython` vs `develop` before migration

**Fetch all remote state first**
```bash
git fetch --all --prune
```

**Commits in ES2 NOT in develop (your unreleased work)**
```bash
git log origin/develop..origin/ES2PlaywrightPython --oneline --no-merges
```

**Commits in develop NOT in ES2 (what you inherit on migration)**
```bash
git log origin/ES2PlaywrightPython..origin/develop --oneline --no-merges
```

**How many develop commits ES2 is behind**
```bash
git rev-list --count origin/ES2PlaywrightPython..origin/develop
```

**Full file-level diff with change statistics**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --stat
```

**Files that differ — names only**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-only
```

**Files by change type (A=added, M=modified, D=deleted)**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status
```

**Scoped diffs per layer**
```bash
git diff origin/develop...origin/ES2PlaywrightPython -- pages/
git diff origin/develop...origin/ES2PlaywrightPython -- tests/bdd/features/
git diff origin/develop...origin/ES2PlaywrightPython -- tests/bdd/steps/
git diff origin/develop...origin/ES2PlaywrightPython -- config/
```

---

### 9.2 Identify missing files, configs, and dependencies

**Feature files in ES2 not yet in develop**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status -- tests/bdd/features/ | grep "^A"
```

**Page objects in ES2 not yet in develop**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status -- pages/ | grep "^A"
```

**Step files in ES2 not yet in develop**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status -- tests/bdd/steps/ | grep "^A"
```

**Pipeline files missing from develop**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status -- "*.yaml" "*.yml" | grep "^A"
```

**Dependency drift — compare requirements.txt**
```bash
git show origin/develop:requirements.txt > /tmp/req_develop.txt
git show origin/ES2PlaywrightPython:requirements.txt > /tmp/req_es2.txt
diff /tmp/req_develop.txt /tmp/req_es2.txt
```

**Config drift — compare environment files**
```bash
git show origin/develop:config/env.test11.yaml > /tmp/env_develop.yaml
git show origin/ES2PlaywrightPython:config/env.test11.yaml > /tmp/env_es2.yaml
diff /tmp/env_develop.yaml /tmp/env_es2.yaml
```

**pyproject.toml / Makefile / conftest drift**
```bash
git diff origin/develop origin/ES2PlaywrightPython -- pyproject.toml Makefile conftest.py
```

---

### 9.3 Identify stale or conflicting changes

**Find the common ancestor (merge base)**
```bash
git merge-base origin/develop origin/ES2PlaywrightPython
```

**Files changed in BOTH branches since the common ancestor = conflict candidates**
```bash
BASE=$(git merge-base origin/develop origin/ES2PlaywrightPython)

git diff $BASE origin/develop --name-only | sort > /tmp/develop_changed.txt
git diff $BASE origin/ES2PlaywrightPython --name-only | sort > /tmp/es2_changed.txt

comm -12 /tmp/develop_changed.txt /tmp/es2_changed.txt
```

**Stale files — deleted in develop but still present in ES2**
```bash
git diff origin/develop...origin/ES2PlaywrightPython --name-status | grep "^D"
```

---

### 9.4 Develop branch stability checklist

| Check | Command | Expected result |
|---|---|---|
| develop CI last run | Azure DevOps → Pipelines → develop | All stages passed |
| develop is clean | `git checkout develop && git status` | Nothing to commit |
| Tests collect on develop | `pytest --collect-only -q` | Zero collection errors |
| Smoke suite on develop | `pytest -m smoke --env test11` | All green |
| Dependencies install | `pip install -r requirements.txt` | No errors |
| Config loads | `python -c "from config.settings import get_settings; get_settings()"` | No exceptions |
| No broken imports | Python import chain check (Section 9.8) | All `OK` |
| No dangling merge conflicts | `git log --merges origin/develop --oneline -5` | Only expected merges |

---

### 9.5 Dry-run migration strategy

Run the entire merge in a **throwaway branch** first. Delete it if anything breaks.

```bash
# Create dry-run branch (local only — do NOT push to origin)
git checkout team/stp
git checkout -b dryrun/stp-migration-$(date +%Y%m%d)

# Attempt merge without committing
git merge origin/ES2PlaywrightPython --no-ff --no-commit

# Inspect the merge state
git status
git diff --cached --stat

# List conflict files
git ls-files -u | awk '{print $4}' | sort -u

# If issues found — abort completely
git merge --abort
git checkout team/stp
git branch -D dryrun/stp-migration-$(date +%Y%m%d)
```

If the dry-run resolves cleanly:
```bash
# Commit the dry-run
git commit -m "dryrun: test migration of ES2PlaywrightPython into team/stp"

# Run validation suite on the dry-run branch
pytest --collect-only -q
pytest -m smoke --env test11

# If green — delete dry-run and perform real migration
git checkout team/stp
git branch -D dryrun/stp-migration-$(date +%Y%m%d)
# Now execute Phase 2, Step 2.3
```

---

### 9.6 Branch parity validation after migration

**All ES2 commits must be reachable from `team/stp` (expected: empty output)**
```bash
git log origin/team/stp..origin/ES2PlaywrightPython --oneline
```

**No unexpected file differences between ES2 and `team/stp`**
```bash
git diff origin/team/stp origin/ES2PlaywrightPython --name-status
# Only pipeline/config files should differ (intentional). No missing feature/step/page files.
```

**File count comparison**
```bash
git ls-tree -r --name-only origin/ES2PlaywrightPython | wc -l
git ls-tree -r --name-only origin/team/stp | wc -l
```

**After monorepo restructure — confirm `git mv` preserved history**
```bash
git log --follow applicationqe/tests/features/stp/stp-contributions/Contribution.feature --oneline
# Must show original commit history from tests/bdd/features/Contribution.feature
```

**Confirm old paths are empty after the move**
```bash
git ls-tree -r --name-only origin/team/stp -- tests/bdd/features/
git ls-tree -r --name-only origin/team/stp -- pages/
# Both should return empty (files moved to applicationqe/)
```

---

### 9.7 Migration comparison reports

**Report 1 — Pre-migration: ES2 vs develop**
```bash
{
  echo "=== COMMITS: ES2 not in develop ==="
  git log origin/develop..origin/ES2PlaywrightPython --oneline --no-merges

  echo ""
  echo "=== COMMITS: develop not in ES2 ==="
  git log origin/ES2PlaywrightPython..origin/develop --oneline --no-merges

  echo ""
  echo "=== FILE DIFF (name-status) ==="
  git diff origin/develop...origin/ES2PlaywrightPython --name-status

  echo ""
  echo "=== CONFLICT CANDIDATES ==="
  BASE=$(git merge-base origin/develop origin/ES2PlaywrightPython)
  comm -12 \
    <(git diff $BASE origin/develop --name-only | sort) \
    <(git diff $BASE origin/ES2PlaywrightPython --name-only | sort)
} > migration_report_1_pre_migration.txt
```

**Report 2 — Post-migration parity: ES2 vs `team/stp`**
```bash
{
  echo "=== PARITY: ES2 vs team/stp ==="
  git diff origin/team/stp origin/ES2PlaywrightPython --name-status

  echo ""
  echo "=== COMMITS IN ES2 NOT IN team/stp (must be empty) ==="
  git log origin/team/stp..origin/ES2PlaywrightPython --oneline
} > migration_report_2_parity.txt
```

**Report 3 — Post-migration: develop vs `team/stp`**
```bash
{
  echo "=== develop vs team/stp AFTER MIGRATION ==="
  git diff origin/develop origin/team/stp --name-status

  echo ""
  echo "=== COMMITS IN team/stp NOT IN develop (STP-specific work) ==="
  git log origin/develop..origin/team/stp --oneline --no-merges
} > migration_report_3_stp_vs_develop.txt
```

---

### 9.8 QA automation & regression validation post-migration

```bash
# 1. All tests must collect — zero errors
pytest applicationqe/ --collect-only -q 2>&1 | tail -10

# 2. Smoke suite on test11
pytest -m smoke --env test11 -v --tb=short

# 3. Per-sub-domain collection check
pytest applicationqe/tests/features/stp/stp-contributions/ --collect-only -q
pytest applicationqe/tests/features/stp/stp-aip/          --collect-only -q
pytest applicationqe/tests/features/stp/stp-swp/          --collect-only -q

# 4. Import chain check — no broken page/step imports
python -c "
import importlib, pkgutil, sys
sys.path.insert(0, '.')
for finder, name, ispkg in pkgutil.walk_packages(['applicationqe/tests/steps']):
    try:
        importlib.import_module(name)
        print(f'OK: {name}')
    except Exception as e:
        print(f'FAIL: {name} -- {e}')
"

# 5. Config load check
python -c "from config.settings import get_settings; s = get_settings(); print('Config OK:', s.env)"

# 6. Allure report generation check
pytest -m smoke --env test11 --alluredir=reports/allure-results -q
allure generate reports/allure-results -o reports/allure-report --clean
```

---

### 9.9 Risk indicators that block migration

| Risk indicator | How to detect | Blocking? |
|---|---|---|
| develop CI pipeline failing | Azure DevOps pipeline status on develop | **YES — fix develop first** |
| >20 conflict candidate files | `comm -12` output line count > 20 | **YES — resolve manually first** |
| ES2 is >50 commits behind develop | `git rev-list --count` > 50 | **YES — sync ES2 with develop first** |
| `pytest --collect-only` fails on develop | Collection errors on develop | **YES — fix before migrating** |
| `requirements.txt` version conflicts | `pip check` outputs errors | **YES** |
| Environment config files missing | diff shows env.yaml deleted in develop | **YES** |
| Any step file import error | Import chain script shows `FAIL` | **YES** |
| Uncommitted changes on ES2 | `git status` shows modified files | **YES — commit or stash first** |
| `qa-pipelines-shared-config` variable group missing | New pipeline fails at variable resolution | **YES** |
| Dry-run produces >5 unresolvable conflicts | `git ls-files -u` count > 5 | **YES — escalate** |
| Test data CSV paths broken | `pytest --collect-only` import errors on data files | **YES** |

---

### 9.10 Go / No-Go checklist before final migration

**Git state**
- [ ] `git status` on `ES2PlaywrightPython` is clean (no uncommitted changes)
- [ ] `git fetch --all` completed without errors
- [ ] Backup tag `backup/ES2PlaywrightPython-pre-migration` pushed to origin
- [ ] Commit-behind count documented (ES2 is N commits behind develop)
- [ ] Conflict candidate count < 20 files
- [ ] Dry-run merge completed and deleted cleanly

**develop branch health**
- [ ] develop CI pipeline last run: **PASSED**
- [ ] `pytest --collect-only -q` on develop: zero errors
- [ ] `pytest -m smoke --env test11` on develop: all green
- [ ] `pip install -r requirements.txt` on develop: no errors
- [ ] Config loads without exception on develop

**ES2 branch health**
- [ ] `pytest --collect-only -q` on ES2: zero errors
- [ ] `pytest -m smoke --env test11` on ES2: all green (baseline saved)
- [ ] All page object imports resolve
- [ ] Report 1 (pre-migration) generated and reviewed

**Team readiness**
- [ ] All developers notified of migration date and ES2 freeze time
- [ ] All open PRs on ES2 merged or explicitly deferred
- [ ] Rollback owner identified and rollback commands ready to execute
- [ ] Post-migration validation assignee confirmed

**Infrastructure**
- [ ] Azure DevOps `qa-pipelines-shared-config` variable group verified
- [ ] `azureSubscription` service connection name confirmed and documented
- [ ] Agent pool `ubuntu2204-qa` is available and not under maintenance
- [ ] Allure reporting confirmed working on a test run

**Decision: GO only when every box above is checked. Any unchecked item = NO-GO.**
