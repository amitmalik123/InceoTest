import { defineConfig, devices } from "@playwright/test";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as fs from "fs"; 

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ENV = process.env.ENV || "test";
dotenv.config({ path: join(__dirname, `env/.env.${ENV}`) });

const isCI = !!process.env.CI;
const authDir = join(__dirname, ".auth");
const authFile = join(authDir, "user.json");

if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

// --- Settings ---
const commonUse = {
  baseURL: process.env.URL,
  headless: isCI,
  slowMo: isCI ? 0 : 50,
  colorScheme: "dark" as const,
  // geolocation: { longitude: 12.492507, latitude: 41.889938 },
  // permissions: ["geolocation"] as const,
  ignoreHTTPSErrors: true,
  viewport: { width: 1280, height: 720 },

  // Only one Trace for failed tests
  // trace: "retain-on-failure" as const, 
  screenshot: "only-on-failure" as const,
  // video: "retain-on-failure" as const,

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
  
  fullyParallel: false, 
  workers: 1, // Keep at 1 forauth session conflicts
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
 
  // AZURE PATHS: touch this config and I will kill you - Srilu Balla
  reporter: [
    ['allure-playwright', { outputFolder: join(__dirname, 'target/allure-results') }],
    ['html', { outputFolder: join(__dirname, 'target/playwright-report') }],
    ['junit', { outputFile: join(__dirname, 'test-results/junit-report.xml') }],
  ],

  use: {
    ...commonUse,
  },

  projects: [
    {
      name: "setup",
      testDir: "./helper",
      testMatch: ["global.auth.setup.spec.ts"],
    },
    {
      name: "compareiFrame",
      testDir: "./e2e/compareiFrame", 
      testMatch: "**/*.spec.ts", 
      dependencies: ["setup"],
      use: {
        ...commonUse,
        storageState: authFile,
        channel: 'chrome', 
      },
    },
    {
      name: "userRoles",
      testDir: "./e2e/userRoles", 
      testMatch: "**/*.spec.ts",
      use: {
        ...commonUse,
        channel: 'chrome',
      },
    },
    {
      name: "auth",
      testDir: "./e2e/auth", 
      testMatch: "**/*.spec.ts",
      use: { 
        ...commonUse, 
        channel: 'chrome' 
      },
    },
     {
      name: "local",
      testDir: "./e2e/local", 
      testMatch: "**/*.spec.ts",
      use: { 
        ...commonUse, 
        channel: 'chrome' 
      },
    },
    {
      name: "exp",
      testDir: "./e2e/exp", 
      testMatch: "**/*.spec.ts",
      dependencies: ["setup"], 
      use: {
        ...commonUse,
        storageState: authFile, 
        channel: 'chrome',
      },
    },
  ],
});