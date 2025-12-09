import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const CONFIG_FILE_PATH = path.resolve(__dirname, '..', 'playwright.config.ts');

describe('🛡️ Playwright Config Integrity Check (playwright.config.ts)', () => {

    let configContent: string;

    it('should successfully read the content of the config file', () => {
        expect(fs.existsSync(CONFIG_FILE_PATH)).toBe(true);
        configContent = fs.readFileSync(CONFIG_FILE_PATH, 'utf-8');
        expect(configContent.length).toBeGreaterThan(0);
    });


    it('should enforce the use of process.env.URL for baseURL within commonUse', () => {
        const baseURLCheck = configContent.match(/commonUse\s*=\s*{[^}]*baseURL:\s*process\.env\.URL/s);
        expect(baseURLCheck).not.toBeNull();

        if (!baseURLCheck) {
            console.error('\n[ERROR] `baseURL` must be set using `process.env.URL` within the `commonUse` object.');
        }
    });

    it('should enforce `fullyParallel: true` for performance', () => {
        expect(configContent).toContain('fullyParallel: false');
    });

    it('should enforce `forbidOnly: isCI` to prevent accidental commits of focused tests', () => {
        expect(configContent).toContain('forbidOnly: isCI');
    });

    it('should use `process.env.ENV` for dynamic environment loading and correct pathing', () => {

        const envDefinitionCheck = configContent.match(/const ENV = process\.env\.ENV \|\| "[^"]*";/);
        expect(envDefinitionCheck).not.toBeNull();

        if (!envDefinitionCheck) {
            console.error('\n[ERROR] `const ENV` must be defined using `process.env.ENV` with a fallback value.');
        }

        const dotenvConfigCheck = configContent.match(/dotenv\.config\({ path: join\(__dirname, `env\/\.env\.\$\{ENV\}`\) }\);/);
        expect(dotenvConfigCheck).not.toBeNull();

        if (!dotenvConfigCheck) {
            console.error('\n[ERROR] `dotenv.config` must use the ENV variable to dynamically load the .env file.');
        }
    });

    it('should explicitly ensure the .auth directory exists', () => {
        expect(configContent).toMatch(/fs\.mkdirSync\(authDir,\s*{ recursive:\s*true }\);/);
    });

    it('should define the "setup" project pointing to global.auth.setup.spec.ts', () => {
        const setupProject = configContent.match(/name:\s*"setup"[^}]*testMatch:\s*\["global\.auth\.setup\.spec\.ts"\]/s);
        expect(setupProject).not.toBeNull();
    });

    it('should define the "authenticated" project with storageState dependency', () => {
        const authenticatedProject = configContent.match(/name:\s*"authenticated"[^}]*dependencies:\s*\["setup"\][^}]*storageState:\s*authFile/s);
        expect(authenticatedProject).not.toBeNull();

        if (!authenticatedProject) {
            console.error('\n[ERROR] "authenticated" project is missing mandatory properties: dependencies: ["setup"] and storageState: authFile.');
        }
    });

    it('should define the "unauthenticated" project', () => {
        expect(configContent).toContain('name: "unauthenticated"');
        expect(configContent).toContain('testMatch: "/unauth/**/*.spec.ts"');
    });

    it('should define the "local" project with correct baseURL override', () => {
        expect(configContent).toContain('name: "local"');
        expect(configContent).toContain('testMatch: "/local/**/*.spec.ts"');
    });

    it('should define the "unit-tests" project and point to the correct directory', () => {
        const unitTestProject = configContent.match(/name:\s*"unit-tests"[^}]*testDir:\s*".\/unit-tests"/s);
        expect(unitTestProject).not.toBeNull();
    });

    it('should use testIgnore to exclude unit-tests from the main run', () => {
        expect(configContent).toContain('testIgnore: ["**/unit-tests/**"],');
    });

    it('should remind the user about required intentional modifications', () => {
        const reminder = 'Sections like `workers` and adding new `projects` are flexible, but core performance/security settings (fullyParallel, forbidOnly, baseURL) must be maintained.';
        expect(reminder).toBeDefined();
    });
});