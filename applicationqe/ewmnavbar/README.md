# 🛡️ EWM-NavBar

### 🧭 Automation Framework Setup & Contribution Guide
This guide is designed to help you **quickly set up, understand, and contribute** to the automation framework.

---

## 🚀 Getting Started
1. 📦 Node.js — Ensure v18+ is installed.
2. 📚 Dependencies

        npm install

3. 🌍 Environment Variables — Create env/.env.[ENV] (e.g., env/.env.qa) with URL, user_standard, and password.
4. 🔐 Authentication Setup (first run)

        npx playwright test --project=setup

### 🚀 Running Tests

NPM scripts

        npm run test:e2e
        npm run test:auth
        npm run test:unauth
        npm run test:local
        npm run test:unit

## 🧾 Review Reports
    Examine the generated Playwright Report (playwright-report/) to understand flow and results.


## ⚙️ Core Configuration

Before writing new tests, replace placeholder settings with your application’s details.

| **Area**                     | **File / Path**                    | **Action Required**                                                     |
| :--------------------------- | :--------------------------------- | :---------------------------------------------------------------------- |
| 🌍 **Environment Variables** | `env/.env.{ENV}`                   | Update all application URLs, API endpoints, and credentials.            |
| 🔐 **Authentication Setup**  | `helper/global.auth.setup.spec.ts` | Modify URLs and locator IDs to match your login flow.                   |
| 🗄️ **Database Integration** | `helper/dbconnect.ts`              | Edit connection parameters and credentials if DB interaction is needed. |

## 🧱 Framework Principles (Fixtures & Structure) WIP



> 💡 **Tip:** Keeping a clean folder structure makes it easier to maintain tests, locate files, and onboard new contributors quickly - SRILU BALLA