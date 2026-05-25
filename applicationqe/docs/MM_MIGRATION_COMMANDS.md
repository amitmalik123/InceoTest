# Model Management SMI — Migration Command Reference

All terminal commands executed during migration from branch
`origin/application/ModelManagement_SMI` → monorepo branch `ModelManagement_SMI`.

Source branch layout: flat pre-monorepo (`pages/`, `tests/bdd/`, `config/`, `data/`).  
Target layout: `applicationqe/` monorepo structure.

---

## 1. Branch Inspection

```powershell
# View source branch commits
git log --oneline origin/application/ModelManagement_SMI

# List all files changed between develop and source branch
git diff --name-only origin/develop origin/application/ModelManagement_SMI

# Show full tree of source branch
git show origin/application/ModelManagement_SMI --stat

# Check current local branch
git status
git branch
```

---

## 2. Reading Source Pipeline File

```powershell
git show origin/application/ModelManagement_SMI:azure-pipelines/model-management.yml
```

---

## 3. Reading Source Page Object Files

```powershell
git show origin/application/ModelManagement_SMI:pages/SMI_Login_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Home_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Reallocation_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Models_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Admin_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Companies_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Manager_Console_Page.py

git show origin/application/ModelManagement_SMI:pages/SMI_Performance_Page.py
```

---

## 4. Reading Source Feature Files

```powershell
# All 4 login feature files in one command
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Login_Functionality_AdminAgent.feature
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Login_Functionality_ExecutiveAgent.feature
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Login_Functionality_ExternalAgent.feature
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Login_Functionality_InternalAgent.feature

# Workflow feature files
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Reallocation.feature
git show origin/application/ModelManagement_SMI:tests/bdd/features/SMI_Rebalance.feature
```

---

## 5. Reading Source Step Definition Files

```powershell
git show origin/application/ModelManagement_SMI:tests/bdd/steps/login_steps.py

git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py
# File is large (~1700 lines); read in slices:
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -First 200
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 200 -First 200
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 400 -First 300
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 700 -First 300
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 1000 -First 300
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 1300 -First 300
git show origin/application/ModelManagement_SMI:tests/bdd/steps/SMI_Login_Steps.py | Select-Object -Skip 1600

git show origin/application/ModelManagement_SMI:tests/bdd/steps/common_steps.py
git show origin/application/ModelManagement_SMI:tests/bdd/steps/data_steps.py
git show origin/application/ModelManagement_SMI:tests/bdd/steps/database_steps.py

git show origin/application/ModelManagement_SMI:tests/bdd/conftest.py
```

---

## 6. Reading Source Config Files

```powershell
# All envs in one command (test12 does not exist in source — returns fatal error, safe to ignore)
git show origin/application/ModelManagement_SMI:config/env.test11.yaml
git show origin/application/ModelManagement_SMI:config/env.test12.yaml   # fatal: path does not exist
git show origin/application/ModelManagement_SMI:config/env.qa.yaml
git show origin/application/ModelManagement_SMI:config/env.silo.yaml
git show origin/application/ModelManagement_SMI:config/env.prod.yaml
```

---

## 7. Reading Source Data Files (for reference / future migration)

```powershell
git show origin/application/ModelManagement_SMI:data/test_data.test10.csv
git show origin/application/ModelManagement_SMI:data/test_Executive_data.test10.csv
git show origin/application/ModelManagement_SMI:data/test_External_data.test10.csv
git show origin/application/ModelManagement_SMI:data/test_Admin_data.test10.csv
```

> Excel files cannot be read via `git show` (binary). Extract them with:
> ```powershell
> git checkout origin/application/ModelManagement_SMI -- data/Test11_data.xlsx
> # then move to applicationqe/data/model-management/
> ```

---

## 8. Verifying Migrated File Structure

```powershell
# Confirm all migrated files are present
Get-ChildItem -Recurse `
  applicationqe/tests/features/model-management, `
  applicationqe/tests/steps/model-management, `
  applicationqe/config/model-management `
| Where-Object { -not $_.PSIsContainer } `
| Select-Object FullName `
| ForEach-Object { $_.FullName.Replace("$PWD\", "") }

# Check data directory
Get-ChildItem applicationqe/data/model-management/ | Select-Object Name

# Check pages
Get-ChildItem applicationqe/pages/model-management/ | Select-Object Name
```

---

## 9. Git Commit & Push

```powershell
# Stage all changes
git add applicationqe/azure-pipelines/model-management.yml
git add applicationqe/pages/model-management/
git add applicationqe/tests/features/model-management/
git add applicationqe/tests/steps/model-management/
git add applicationqe/config/model-management/
git add applicationqe/docs/MM_MIGRATION_PLAN.md
git add applicationqe/docs/MM_MIGRATION_COMMANDS.md

# Commit
git commit -m "feat(model-management): migrate SMI pages, features, steps, config and pipeline"

# Push to remote
git push origin ModelManagement_SMI
```

---

## 10. Pending Commands (not yet run)

### Add MM markers to pytest.ini
```powershell
# After editing pytest.ini, verify markers are registered
cd applicationqe
python -m pytest --markers | Select-String "model_management\|SMI_"
```

### Verify imports resolve correctly
```powershell
cd applicationqe
python -c "from pages.model_management import SMIHomePage, SMILoginPage, SMIReallocationPage; print('OK')"
```

### Run smoke tests locally
```powershell
cd applicationqe
$env:ENV = "test11"
$env:TEAM_NAME = "model-management"
python -m pytest tests/features/model-management/ -m "smoke" -v --tb=short
```

### Run a specific feature file
```powershell
cd applicationqe
python -m pytest tests/features/model-management/smi_login_admin_agent.feature -v
```

### Check for lint errors
```powershell
cd applicationqe
python -m flake8 pages/model-management/ tests/steps/model-management/ --max-line-length=120
```

### Validate pyproject.toml build
```powershell
cd applicationqe
pip install -e . --dry-run
```

---

## Migrated File Map

| Source (flat layout) | Target (monorepo layout) |
|---|---|
| `azure-pipelines/model-management.yml` | `applicationqe/azure-pipelines/model-management.yml` |
| `pages/SMI_Login_Page.py` | `applicationqe/pages/model-management/smi_login_page.py` |
| `pages/SMI_Home_Page.py` | `applicationqe/pages/model-management/smi_home_page.py` |
| `pages/SMI_Reallocation_Page.py` | `applicationqe/pages/model-management/smi_reallocation_page.py` |
| `pages/SMI_Models_Page.py` | `applicationqe/pages/model-management/smi_models_page.py` |
| `pages/SMI_Admin_Page.py` | `applicationqe/pages/model-management/smi_admin_page.py` |
| `pages/SMI_Companies_Page.py` | `applicationqe/pages/model-management/smi_companies_page.py` |
| `pages/SMI_Manager_Console_Page.py` | `applicationqe/pages/model-management/smi_manager_console_page.py` |
| `pages/SMI_Performance_Page.py` | `applicationqe/pages/model-management/smi_performance_page.py` |
| `tests/bdd/features/SMI_Login_Functionality_AdminAgent.feature` | `applicationqe/tests/features/model-management/smi_login_admin_agent.feature` |
| `tests/bdd/features/SMI_Login_Functionality_ExecutiveAgent.feature` | `applicationqe/tests/features/model-management/smi_login_executive_agent.feature` |
| `tests/bdd/features/SMI_Login_Functionality_ExternalAgent.feature` | `applicationqe/tests/features/model-management/smi_login_external_agent.feature` |
| `tests/bdd/features/SMI_Login_Functionality_InternalAgent.feature` | `applicationqe/tests/features/model-management/smi_login_internal_agent.feature` |
| `tests/bdd/features/SMI_Reallocation.feature` | `applicationqe/tests/features/model-management/smi_reallocation.feature` |
| `tests/bdd/features/SMI_Rebalance.feature` | `applicationqe/tests/features/model-management/smi_rebalance.feature` |
| `tests/bdd/steps/SMI_Login_Steps.py` | `applicationqe/tests/steps/model-management/flows/smi_login_flow.py` |
| `tests/bdd/steps/login_steps.py` | _(merged into smi_login_flow.py)_ |
| `tests/bdd/steps/common_steps.py` | _(merged into smi_login_flow.py)_ |
| `tests/bdd/steps/data_steps.py` | `applicationqe/tests/steps/model-management/validations/smi_validations.py` |
| `tests/bdd/steps/database_steps.py` | `applicationqe/tests/steps/model-management/validations/smi_validations.py` |
| `tests/bdd/conftest.py` | `applicationqe/tests/features/model-management/conftest.py` |
| `config/env.test11.yaml` | `applicationqe/config/model-management/env.test11.yaml` |
| `config/env.qa.yaml` | `applicationqe/config/model-management/env.qa.yaml` |
| `config/env.silo.yaml` | `applicationqe/config/model-management/env.silo.yaml` |
| `config/env.prod.yaml` | `applicationqe/config/model-management/env.prod.yaml` |
| `data/test_data.test10.csv` | `applicationqe/data/model-management/test_data.test11.csv` _(pending)_ |
| `data/Test11_data.xlsx` | `applicationqe/data/model-management/Test11_data.xlsx` _(pending)_ |
