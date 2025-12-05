import { Page } from '@playwright/test';

/**
 * Navigate to Portfolio Engine from ewm
 * Opens Portfolio Engine in a new popup window
 * @param mainPage - The main page object
 * @returns The Portfolio Engine page object (new tab)
 */
export async function navigateToPortfolioEngine(mainPage: Page): Promise<Page> {
    await mainPage.getByRole('link', { name: 'Investments' }).click();
    await mainPage.getByRole('link', { name: 'PortfolioEngine', exact: true }).click();
    const page1Promise = mainPage.waitForEvent('popup');
    await mainPage.getByRole('img', { name: 'Launch Portfolio Engine' }).first().click();
    const portfolioEnginePage = await page1Promise;
    await mainPage.waitForLoadState();
    return portfolioEnginePage;
}
