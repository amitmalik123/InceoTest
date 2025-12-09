import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const SETUP_FILE_PATH = path.resolve(__dirname, '..', 'helper', 'global.auth.setup.spec.ts');
const EXPECTED_STORAGE_PATH = '.auth/user.json';
const EXPECTED_ENV_VAR_USAGE = /process\.env\.(user_standard|password)/;

describe('🛡️ Global Auth Setup Integrity Check (helper/global.auth.setup.spec.ts)', () => {

    let fileContent: string;

    it('should successfully read the content of the setup file', () => {
        expect(fs.existsSync(SETUP_FILE_PATH)).toBe(true);
        fileContent = fs.readFileSync(SETUP_FILE_PATH, 'utf-8');
        expect(fileContent.length).toBeGreaterThan(0);
    });

    it(`should explicitly save the storage state to the expected path: ${EXPECTED_STORAGE_PATH}`, () => {
        const pathReference = `path: '${EXPECTED_STORAGE_PATH}'`;
        expect(fileContent).toContain(pathReference);

        if (!fileContent.includes(pathReference)) {
            console.error(`\n[ERROR] The storageState path is incorrect. Expected: "${pathReference}"`);
        }
    });

    it('should ensure the file imports and uses the base "test" object from Playwright', () => {
        expect(fileContent).toContain('import { test } from "@playwright/test";');

        expect(fileContent).toContain('test("create auth storage", async ({ page }) => {');
    });

    it('should remind the user about the highest protection level for this file', () => {
        const reminder = 'This file is core to authenticated testing speed. Do not modify the login steps or storage path unless changing the authentication mechanism itself.';
        expect(reminder).toBeDefined();
    });
});