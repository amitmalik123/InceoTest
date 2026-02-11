# 🛡️ EWM-NavBar Documentation

For complete setup, execution, and details regarding the EWM-NavBar Automation Suite, please visit the Confluence page:

### 🔗  [EWMNavBar Automation ReadMe](https://assetmark.atlassian.net/wiki/spaces/PE/pages/1761017888/eWMNavBar+Automation+ReadMe)

### 🔗  [ProdEng Repo](https://dev.azure.com/AssetmarkInc/ProdEng/_git/qeautomation?version=GBplaywrightsrilu&path=%2Fapplicationqe%2Fewmnavbar)

### 🔗  [ProdEng PipeLine](https://dev.azure.com/AssetmarkInc/ProdEng/_build?definitionId=1484&_a=summary)

---

## 📋 .gitignore Configuration

This project uses a `.gitignore` file to manage which files are tracked by git:

### Repository-Level Ignores (Root)
```
/qeautomation/.auth/*
/qeautomation/allure-results/*
/qeautomation/eWM NavBar/*
/qeautomation/platformqe/*
/qeautomation/Salesforce/*
/qeautomation/test-results/*
/qeautomation/applicationqe/proposalas/*
```

### Build & Test Outputs
```
node_modules/
test-results/
playwright-report/
blob-report/
allure-results/
allure-report/
reports/
```

### IDE & Tools
```
.vscode/
.github/
.husky/
```

### Playwright & Cache
```
playwright/.cache/
playwright/.auth/
```

### Local Development
```
.auth/
framework/screenshots/
e2e/local/
```

### ✅ Tracked Files
- ✅ `framework/reporter/` - Python reporter module (intentionally tracked)
- ✅ All source code in `lib/`, `tests/`, `scripts/`
- ✅ Configuration files (playwright.config.ts, tsconfig.json, package.json)

---

> 💡 **Tip:** Keeping a clean folder structure makes it easier to maintain tests, locate files, and onboard new contributors quickly.
>
> — *Srilu Balla*