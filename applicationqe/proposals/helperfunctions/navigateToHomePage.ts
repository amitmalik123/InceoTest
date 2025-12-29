import { Page } from '@playwright/test';

/**
 * Navigate to the ewm home page
 * @param page - The page object to navigate
 */
export async function navigateToHomePage(page: Page): Promise<void> {
    await page.goto(process.env.baseURL + '/en.aspx');
    await page.waitForLoadState('domcontentloaded');
}
