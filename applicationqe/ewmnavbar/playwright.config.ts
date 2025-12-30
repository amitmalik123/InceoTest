import { defineConfig, devices } from "@playwright/test";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as fs from "fs"; 

// --- __dirname and __filename Setup ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// --- Environment Setup ---
const ENV = process.env.ENV || "test";
dotenv.config({ path: join(__dirname, `env/.env.${ENV}`) });

const isCI = !!process.env.CI;
const authDir = join(__dirname, ".auth");
const authFile = join(authDir, "user.json");

if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

// --- Common Settings ---
const commonUse = {
  baseURL: process.env.URL,
  headless: isCI,
  slowMo: isCI ? 0 : 50,
  trace: "on-first-retry" as const,
  colorScheme: "dark" as const,
  geolocation: { longitude: 12.492507, latitude: 41.889938 },
  permissions: ["geolocation"] as const,
  ignoreHTTPSErrors: true,
  
  viewport: { width: 1280, height: 720 },

  launchOptions: {
    logger: {
      isEnabled: (name, severity) => name === 'api', 
      log: (name, severity, message, args) => null,
    },
  },
};

export default defineConfig({
  timeout: 3 * 60 * 1000,
  testDir: "./", 
  testIgnore: ["**/unit-tests/**"],
  
  // Update settings here
  fullyParallel: false, 
  workers: 1,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
 
  reporter: [
    ['allure-playwright', { outputFolder: join(__dirname, 'target/allure-results') }],
    ['html', { outputFolder: join(__dirname, 'playwright-report') }],
    ['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }],
  ],

  use: {
    ...commonUse,
    screenshot: 'only-on-failure',
    // video: 'retain-on-failure',
    // trace: 'retain-on-failure', 
    // retries: process.env.CI ? 2 : 1,
  },

  projects: [
    // 1. Setup (Stays the same)
    {
      name: "setup",
      testDir: "./helper",
      testMatch: ["global.auth.setup.spec.ts"],
    },

    // 2. Main Project 
    {
      name: "compareiFrame",
      testDir: "./e2e/compareiFrame", 
      testMatch: "**/*.spec.ts", 
      dependencies: ["setup"],
      use: {
        ...commonUse,
        screenshot: 'only-on-failure',
        storageState: authFile,
        channel: 'chrome', 
      },
    },

    // 3. User Roles 
    {
      name: "userRoles",
      testDir: "./e2e/userRoles", 
      testMatch: "**/*.spec.ts",
      use: {
        screenshot: 'only-on-failure',
        ...commonUse,
        channel: 'chrome',
      },
    },

    // 4. Local Dev Work
    {
      name: "local",
      testDir: "./e2e/local", 
      testMatch: "**/*.spec.ts",
      use: { ...commonUse, 
        screenshot: 'only-on-failure',
        channel: 'chrome' },
    },

    // 5. Experimental
    {
      name: "exp",
      testDir: "./e2e/exp", 
      testMatch: "**/*.spec.ts",
      dependencies: ["setup"], 
      use: {
        ...commonUse,
        screenshot: 'only-on-failure',
        storageState: authFile, 
        channel: 'chrome',
      },
    },
],
});