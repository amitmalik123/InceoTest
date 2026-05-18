import { Given, When, Then } from "../../../../fixtures/fixtures";
import { expect } from "@playwright/test";
import { logger } from "../../../../utils/logger";
import { navigateToHomePage } from "../../../../helperfunctions/navigateToHomePage";
import { navigateToPortfolioEngine } from "../../../../helperfunctions/navigateToPortfolioEngine";
import { PortfolioEnginePage } from "../../../../pages/PortfolioEngineObjectModel";
import {
    setPortfolioEnginePageInstance,
    getPortfolioEnginePageInstance,
} from "../shared/instanceManager";

Given("I am on the Portfolio Engine page", async ({ page }) => {
    await navigateToHomePage(page);
    const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
    const portfolioEnginePageInstance = new PortfolioEnginePage(
        portfolioEnginePageObject,
    );
    setPortfolioEnginePageInstance(portfolioEnginePageInstance);

    // Dismiss privacy dialog immediately
    await portfolioEnginePageInstance.dismissPrivacyDialog();

    try {
        await expect(
            portfolioEnginePageInstance.getStartedButton.or(
                portfolioEnginePageInstance.managePortfoliosButton,
            ),
        ).toBeVisible();
    } catch (err) {
        logger.error("Portfolio Engine homepage failed to load in time", err);
        throw err;
    }
});

When("I click the manage portfolios button", async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();

    try {
        await Promise.race([
            portfolioEnginePageInstance.getStartedButton.waitFor({
                state: "visible",
            }),
            portfolioEnginePageInstance.managePortfoliosButton.waitFor({
                state: "visible",
            }),
            //portfolioEnginePageInstance.okButton.waitFor({ state: 'visible' }), // OK button is part of overlay and may appear instead of Manage Portfolios; May break in future if portfolio has inalid data but selector is matching mutliple buttons atm and don't have example to fix with
        ]);
    } catch (err) {
        logger.error("Portfolio Engine homepage failed to load in time", err);
        throw err;
    }

    // If Get Started is visible, it is an exclusive page state.
    if (await portfolioEnginePageInstance.getStartedButton.isVisible()) {
        await portfolioEnginePageInstance.getStartedButton.click();
        return;
    }

    // Otherwise, handle OK/Manage Portfolios flow where either button takes you to the next step.
    // OK button is part of the overlay; clicking it dismisses the overlay and proceeds.
    for (let attempt = 0; attempt < 5; attempt++) {
        //may need to re-enable once okbutton select is fixed
        // if (await portfolioEnginePageInstance.okButton.isVisible()) {
        //     // OK button is part of overlay; clicking it dismisses overlay and proceeds to next step
        //     await portfolioEnginePageInstance.okButton.click({ timeout: 5000 });
        //     return;
        // }
        if (
            await portfolioEnginePageInstance.managePortfoliosButton.isVisible()
        ) {
            // Manage Portfolios is visible and not blocked; click to proceed
            await portfolioEnginePageInstance.managePortfoliosButton.click({
                timeout: 5000,
            });
            return;
        }

        // Delay before retry if neither button is visible
        await portfolioEnginePageInstance.page.evaluate(
            () => new Promise((resolve) => setTimeout(resolve, 300)),
        );
    }

    throw new Error(
        "Neither OK button nor Manage Portfolios button was visible after retries",
    );
});

When("I create a new model portfolio", async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.createNewModelPortfolioButton.click();
});

When("I select AssetMark Platform Strategies as portfolio type", async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.assetMarkPlatformStrategiesText.waitFor({
        state: "visible",
    });
    await portfolioEnginePageInstance.assetMarkPlatformStrategiesText.evaluate(
        (el: HTMLElement) => el.click(),
    );
});

When("I select Savos Personal Portfolio Custom as portfolio type", async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.SavosPersonalStrategyText.waitFor({
        state: "visible",
    });
    await portfolioEnginePageInstance.SavosPersonalStrategyText.evaluate(
        (el: HTMLElement) => el.click(),
    );
});

When(
    "I add the following strategies to the portfolio:",
    async ({}, dataTable) => {
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        const strategies = dataTable.raw().flat();
        for (const strategy of strategies) {
            await portfolioEnginePageInstance.addStrategyToPortfolio(strategy);
        }
    },
);

When("I enter portfolio name {string}", async ({}, portfolioName: string) => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.modelPortfolioNameTextbox.fill(
        portfolioName,
    );
});

When("I save the portfolio", async ({ page }) => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.strategySaveButton.click();
    await page.waitForLoadState();
});

Then("the portfolio should contain the expected strategies", async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    try {
        await expect(
            portfolioEnginePageInstance.investmentAllocationText,
        ).toContainText(
            "Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1",
        );
    } catch (err) {
        logger.error(
            "Expected strategies not found in portfolio allocation text",
            err,
        );
        throw err;
    }
});

Then(
    "all strategies should have {string} percent allocation",
    async ({}, expectedAllocation: string) => {
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        for (let i = 0; i < 5; i++) {
            try {
                await expect(
                    portfolioEnginePageInstance.getAllocationTextbox(i),
                ).toHaveValue(expectedAllocation, {});
            } catch (err) {
                logger.error(
                    `Allocation percent mismatch for strategy index ${i}`,
                    err,
                );
                throw err;
            }
        }
    },
);
