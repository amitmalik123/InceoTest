import { Given, When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { navigateToHomePage } from '../../../../helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '../../../../helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../../../../pages/PortfolioEngineObjectModel';

// Export the Portfolio Engine page instance so all steps can access it
export let portfolioEnginePageInstance: PortfolioEnginePage;

Given('I am on the Portfolio Engine page', async ({ page }) => {
    await navigateToHomePage(page);
    const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
    portfolioEnginePageInstance = new PortfolioEnginePage(portfolioEnginePageObject);
    await expect(portfolioEnginePageInstance.getStartedButton.or(portfolioEnginePageInstance.managePortfoliosButton)).toBeVisible({ timeout: 300000 });
});

Given('I have created a portfolio with strategies', async () => {
    await Promise.race([
        portfolioEnginePageInstance.getStartedButton.waitFor({ state: 'visible', timeout: 300000 }),
        portfolioEnginePageInstance.managePortfoliosButton.waitFor({ state: 'visible', timeout: 300000 })
    ]);
    await portfolioEnginePageInstance.createPortfolioIfNeeded('E2E Test Portfolio');
});

When('I click the manage portfolios button', async () => {
    await expect(portfolioEnginePageInstance.getStartedButton.or(portfolioEnginePageInstance.managePortfoliosButton)).toBeVisible({ timeout: 300000 });
    if (await portfolioEnginePageInstance.getStartedButton.isVisible()) {
        await portfolioEnginePageInstance.getStartedButton.click();
    } else if (await portfolioEnginePageInstance.managePortfoliosButton.isVisible()) {
        await portfolioEnginePageInstance.managePortfoliosButton.click();
    }
});

When('I create a new model portfolio', async () => {
    await portfolioEnginePageInstance.createNewModelPortfolioButton.click();
});

When('I select {string} as portfolio type', async ({ }, portfolioType: string) => {
    await portfolioEnginePageInstance.assetMarkPlatformStrategiesText.click();
});

When('I add the following strategies to the portfolio:', async ({ }, dataTable) => {
    const strategies = dataTable.raw().flat();
    for (const strategy of strategies) {
        await portfolioEnginePageInstance.addStrategyToPortfolio(strategy);
    }
});

When('I enter portfolio name {string}', async ({ }, portfolioName: string) => {
    await portfolioEnginePageInstance.modelPortfolioNameTextbox.fill(portfolioName);
});

When('I save the portfolio', async ({ page }) => {
    await portfolioEnginePageInstance.strategySaveButton.click();
    await page.waitForLoadState();
});

Then('the portfolio should contain the expected strategies', async () => {
    await expect(portfolioEnginePageInstance.investmentAllocationText).toContainText('Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1', { timeout: 300000 });
});

Then('all strategies should have {string} percent allocation', async ({ }, expectedAllocation: string) => {
    for (let i = 0; i < 5; i++) {
        await expect(portfolioEnginePageInstance.getAllocationTextbox(i)).toHaveValue(expectedAllocation, { timeout: 300000 });
    }
});
