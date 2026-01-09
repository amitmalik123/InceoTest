// Url&Titles.spec.ts
import { test, expect } from '../../helper/fixtures';
import { fileURLToPath } from 'url';
import * as path from 'path';
import * as fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const urlTitles = path.join(__dirname, 'buttonTitlesUrls.json');

if (!fs.existsSync(urlTitles)) {
    throw new Error(`User data file not found at: ${urlTitles}`);
}

const menuMap = JSON.parse(fs.readFileSync(urlTitles, 'utf-8'));
const menuKeys = Object.keys(menuMap);

test.describe('URL and Document Title', () => {

    menuKeys.forEach((key) => {
        const route = menuMap[key];

        test(`Button - "${route.button}" has title "${route.title}"`, async ({ page, p, f, log }) => {
            
          const fullUrl = `${process.env.URL}${route.legacypath}`;

            await f.Browser.goToURL(fullUrl);
            await page.waitForLoadState('load');
            await page.waitForLoadState('networkidle');

            await f.Browser.compareTitle(route.title);
        });
    });
});