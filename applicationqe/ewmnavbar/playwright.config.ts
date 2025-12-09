import { defineConfig, devices } from "@playwright/test";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as fs from "fs"; 

// --- __dirname and __filename ---
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// ---------------------------------------------------

const ENV = process.env.ENV || "test";
dotenv.config({ path: join(__dirname, `env/.env.${ENV}`) });

const isCI = !!process.env.CI;
const authDir = join(__dirname, ".auth");
const authFile = join(authDir, "user.json");

// The .auth directory 
if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

const commonUse = {
  viewport: null,
  baseURL: process.env.URL,
  headless: isCI,
  slowMo: isCI ? 0 : 50, // Reduced slowMo 
  trace: "on-first-retry" as const,
  colorScheme: "dark" as const,
  geolocation: { longitude: 12.492507, latitude: 41.889938 },
  permissions: ["geolocation"] as const,
  ignoreHTTPSErrors: true, // Ignore SSL certificate validation for test environments
};

export default defineConfig({

  timeout: 3 * 60 * 1000,
  testDir: "./",
  
  testIgnore: ["**/unit-tests/**"],

  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: 1,
  reporter: "html",

  use: {
    ...commonUse,
  },

  projects: [
    // 0) Unit Tests Project - Defines path/config for unit tests (run via 'npm run test:unit')
    {
      name: "unit-tests",
      testDir: "./unit-tests",
      testMatch: "/**/*.test.ts",
      workers: 1,
      use: {
        browserName: "chromium",
        baseURL: undefined,
        headless: true,
      },
    },
    
    // 1) Setup project — logs in and saves authFile
    {
      name: "setup",
      testDir: "./helper",
      testMatch: ["global.auth.setup.spec.ts"],
      use: {
        ...commonUse,
        ...devices["Desktop Chrome"],
      },
    },

    // 2) Authenticated tests — reuse saved storage state
    {
      name: "authenticated",
      testDir: "./e2e",
      testMatch: "/auth/**/*.spec.ts",
      testIgnore: ['./unit-tests/**', './helper/globalSetup.ts'],
      dependencies: ["setup"],
      use: {
        ...commonUse,
        storageState: authFile,
        ...devices["Desktop Chrome"],
      },
    },

    // 3) Unauthenticated tests
    {
      name: "unauthenticated",
      testDir: "./e2e",
      testMatch: "/unauth/**/*.spec.ts",
      testIgnore: ['./unit-tests/**', './helper/globalSetup.ts'],
      use: {
        ...commonUse,
        ...devices["Desktop Chrome"], 
      },
    },

    // 4) Local While working
    {
      name: "local",
      testDir: "./e2e",
      testMatch: "/local/**/*.spec.ts",
      testIgnore: ['./unit-tests/**', './helper/globalSetup.ts'],
      use: {
        ...commonUse,
        ...devices["Desktop Chrome"], 
      },
    },
  ],
});