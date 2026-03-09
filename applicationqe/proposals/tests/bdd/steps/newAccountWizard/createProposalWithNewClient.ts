import { expect, Then, When } from '../../../../fixtures/fixtures';
import { logger } from '../../../../utils/logger';
import { PortfolioEnginePage } from '@pages/PortfolioEngineObjectModel';
import NewAccountWizardPage from '@pages/newAccountWizardPageObjectModel';
import { EwmPage } from '@pages/ewmPageObjectModel';
import {
    setPortfolioEnginePageInstance,
    setNewAccountWizardPageInstance,
    getNewAccountWizardPageInstance,
    setEwmPageInstance,
    getEwmPageInstance,
    setTaxManagementServicesPageInstance,
} from '../shared/instanceManager';
import { TaxManagementServicesPage } from '@pages/taxManagementServicesPageObjectModel';
import { navigateToHomePage } from '../../../../helperfunctions/navigateToHomePage';
import '../portfolioEngine/verifyProposalDocument';

When('I click on the Account Wizard link', async ({ page }) => {
    await navigateToHomePage(page);
    const ewmPageInstance = new EwmPage(page);
    setEwmPageInstance(ewmPageInstance);
    await ewmPageInstance.openAccountWizard();
    await expect(ewmPageInstance.page.getByText('There are two ways to get started')).toBeVisible();
});

When('I decide to create a new client', async ({}) => {
    const ewmPageInstance = getEwmPageInstance();
    await ewmPageInstance.createNewClient.click();
    await ewmPageInstance.page.waitForLoadState();
});

When(
    'I complete the client profile with first name {string} and last name {string}',
    async ({}, firstName: string, lastName: string) => {
        const ewmPageInstance = getEwmPageInstance();
        const newAccountWizardPageInstance = new NewAccountWizardPage(ewmPageInstance.page);
        setNewAccountWizardPageInstance(newAccountWizardPageInstance);
        await expect(newAccountWizardPageInstance.firstNameInput).toBeVisible();
        await expect(newAccountWizardPageInstance.lastNameInput).toBeVisible();
        await expect(newAccountWizardPageInstance.fiduciaryNonDiscretionary).toBeVisible();
        await expect(newAccountWizardPageInstance.fiduciaryDiscretionary).toBeVisible();
        await expect(newAccountWizardPageInstance.lowRiskRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.moderateRiskRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.highRiskRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.veryHighRiskRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.twoYearsOrLessRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.sixToNineYearsRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.twentyFiveTo50PercentRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.growthRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.conservativeRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.moderateConservativeRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.moderateRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.moderateGrowthRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.growthRiskReturnRadio).toBeVisible();
        await expect(newAccountWizardPageInstance.maximumGrowthRiskReturnRadio).toBeVisible();

        logger.debug('\nFilling out new client profile');

        if (await newAccountWizardPageInstance.agentDropdown.isVisible()) {
            await newAccountWizardPageInstance.agentDropdown.click();
            await newAccountWizardPageInstance.agentDropdown.selectOption(process.env.userID);
        }
        await newAccountWizardPageInstance.fillName(firstName, lastName);
        await newAccountWizardPageInstance.fiduciaryDiscretionary.click();
        await newAccountWizardPageInstance.highRiskRadio.click();
        await newAccountWizardPageInstance.sixToNineYearsRadio.click();
        await newAccountWizardPageInstance.twentyFiveTo50PercentRadio.click();
        await newAccountWizardPageInstance.growthRiskReturnRadio.click();
        await newAccountWizardPageInstance.nextButton.click();
    }
);

When('I Complete the Construct Portfolio section', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nFilling out Construct Portfolio section');
    await newAccountWizardPageInstance.page.waitForLoadState();
    await newAccountWizardPageInstance.selectRegistrationType('Individual');
    await newAccountWizardPageInstance.page.waitForLoadState();
    await newAccountWizardPageInstance.selectCustodian();
    await newAccountWizardPageInstance.fillInvestmentAmount('500000');
    await newAccountWizardPageInstance.page.waitForLoadState();
    await newAccountWizardPageInstance.selectAccountType('Multiple Strategy Account');
    await newAccountWizardPageInstance.page.waitForLoadState();
});

When('I add all strategies to the account', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nAdding all strategies to the account');
    await newAccountWizardPageInstance.addStrategy('assetmark income builder, profile 2, conservative');
    await newAccountWizardPageInstance.addStrategy('blackrock equity dividend');
    await newAccountWizardPageInstance.addStrategy('alphasimplex, alternative model portfolio, profile 5, growth');
    await newAccountWizardPageInstance.addStrategy('jpmorgan absolute return - profile 1');
    await newAccountWizardPageInstance.addStrategy('savos us risk controlled strategy, profile 6');

    // Verify all strategies were added by checking for their respective rows and content
    await expect(newAccountWizardPageInstance.coreStrategyRow).toBeVisible();
    await expect(
        newAccountWizardPageInstance.coreStrategyRow.locator(
            'text=AssetMark Income Builder, Profile 2, Conservative, ETF'
        )
    ).toBeVisible();

    await expect(newAccountWizardPageInstance.tacticalEnhancedStrategyRow).toBeVisible();
    await expect(
        newAccountWizardPageInstance.tacticalEnhancedStrategyRow.locator('text=BlackRock Equity Dividend, IMA')
    ).toBeVisible();

    await expect(newAccountWizardPageInstance.diversifyingEquityStrategyRow).toBeVisible();
    await expect(
        newAccountWizardPageInstance.diversifyingEquityStrategyRow.locator(
            'text=AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth, MF'
        )
    ).toBeVisible();

    await expect(newAccountWizardPageInstance.diversifyingBondStrategyRow).toBeVisible();
    await expect(
        newAccountWizardPageInstance.diversifyingBondStrategyRow.locator(
            'text=JPMorgan Absolute Return - Profile 1, MF'
        )
    ).toBeVisible();

    await expect(newAccountWizardPageInstance.tacticalLimitStrategyRow).toBeVisible();
    await expect(
        newAccountWizardPageInstance.tacticalLimitStrategyRow.locator(
            'text=Savos US Risk Controlled Strategy, Profile 6, GMS'
        )
    ).toBeVisible();
});

When('I allocate equal percentages to all strategies', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nAllocating equal percentages to all strategies');
    // Use the stable name attribute selector instead of hardcoded investment IDs
    const percentInputs = newAccountWizardPageInstance.percentLabelsInputs;
    const count = await percentInputs.count();
    for (let i = 0; i < count; i++) {
        await percentInputs.nth(i).fill('20');
        await percentInputs.nth(i).press('Enter');
        // Small delay to allow UI to process the input
        // eslint-disable-next-line playwright/no-wait-for-timeout
        await newAccountWizardPageInstance.page.waitForTimeout(500);
    }

    await newAccountWizardPageInstance.reviewButton.click();
});

When('I opt out of tax management services', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nOpting out of tax management services');
    await newAccountWizardPageInstance.tmsOptionsNo.click();
    await newAccountWizardPageInstance.confirmButton.click();
});

When('I opt into tax management services', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nOpting into tax management services');
    await newAccountWizardPageInstance.tmsOptionsYes.click();
    await newAccountWizardPageInstance.confirmButton.click();
    await newAccountWizardPageInstance.page.waitForLoadState();
    setTaxManagementServicesPageInstance(new TaxManagementServicesPage(newAccountWizardPageInstance.page));
});

Then('the investment summary should display correctly with all strategies and allocations', async () => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    // Verify asset allocation summary widget exists
    await expect(newAccountWizardPageInstance.assetAllocationSummaryWidget).toBeVisible();

    // Verify Core Markets section with 20% and investment account
    await expect(newAccountWizardPageInstance.coreMarketsSection).toBeVisible();
    await expect(newAccountWizardPageInstance.coreMarketsSection.locator('text=20.00%').nth(0)).toBeVisible();
    await expect(newAccountWizardPageInstance.coreMarketsSection.locator('text=20.00%').nth(1)).toBeVisible();
    await expect(
        newAccountWizardPageInstance.coreMarketsSection.locator('text=Multiple Strategy Account')
    ).toBeVisible();

    // Verify Tactical Strategies - Enhanced Return Focus section with 20% and investment account
    await expect(newAccountWizardPageInstance.tacEnhancedSection).toBeVisible();
    await expect(newAccountWizardPageInstance.tacEnhancedSection.locator('text=20.00%').nth(0)).toBeVisible();
    await expect(newAccountWizardPageInstance.tacEnhancedSection.locator('text=20.00%').nth(1)).toBeVisible();
    await expect(
        newAccountWizardPageInstance.tacEnhancedSection.locator('text=Multiple Strategy Account')
    ).toBeVisible();

    // Verify Tactical Strategies - Limit Loss Focus section with 20% and investment account
    await expect(newAccountWizardPageInstance.tacLimitSection).toBeVisible();
    await expect(newAccountWizardPageInstance.tacLimitSection.locator('text=20.00%').nth(0)).toBeVisible();
    await expect(newAccountWizardPageInstance.tacLimitSection.locator('text=20.00%').nth(1)).toBeVisible();
    await expect(newAccountWizardPageInstance.tacLimitSection.locator('text=Multiple Strategy Account')).toBeVisible();

    // Verify Diversifying Strategies - Equity Alternatives section with 20% and investment account
    await expect(newAccountWizardPageInstance.divEquitySection).toBeVisible();
    await expect(newAccountWizardPageInstance.divEquitySection.locator('text=20.00%').nth(0)).toBeVisible();
    await expect(newAccountWizardPageInstance.divEquitySection.locator('text=20.00%').nth(1)).toBeVisible();
    await expect(newAccountWizardPageInstance.divEquitySection.locator('text=Multiple Strategy Account')).toBeVisible();

    // Verify Diversifying Strategies - Bonds & Bond Alternatives section with 20% and investment account
    await expect(newAccountWizardPageInstance.divBondsSection).toBeVisible();
    await expect(newAccountWizardPageInstance.divBondsSection.locator('text=20.00%').nth(0)).toBeVisible();
    await expect(newAccountWizardPageInstance.divBondsSection.locator('text=20.00%').nth(1)).toBeVisible();
    await expect(newAccountWizardPageInstance.divBondsSection.locator('text=Multiple Strategy Account')).toBeVisible();

    // Verify Additional Investments section with 0% (no allocation)
    await expect(newAccountWizardPageInstance.additionalInvestmentsSection).toBeVisible();
    await expect(newAccountWizardPageInstance.additionalInvestmentsSection.locator('text=0.00%')).toBeVisible();

    // Verify Total Portfolio shows 100%
    await expect(
        newAccountWizardPageInstance.assetAllocationSummaryWidget.locator(
            '.header-row:has-text("Total Portfolio") >> text=100.00%'
        )
    ).toBeVisible();

    await newAccountWizardPageInstance.nextButton.click();
});

When('I set a flat fee of {string} percent', async ({}, percent: string) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug(`\nSetting flat fee to ${percent} percent`);
    await newAccountWizardPageInstance.advFlatFeeInput.fill(percent);
    await newAccountWizardPageInstance.advFlatFeeInput.press('Enter');
});

Then('the portfolio fees should be valid', async () => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    // Verify portfolio fee summary table exists
    await expect(newAccountWizardPageInstance.portfolioFeeSummaryTable).toBeVisible();

    // Verify Financial Advisor row exists
    await expect(newAccountWizardPageInstance.financialAdvisorFeeRow).toBeVisible();

    // Get Financial Advisor fee percentage and verify it's not 0
    const faFeeText = await newAccountWizardPageInstance.financialAdvisorFeeRow
        .locator('td.portfolioColumnData label')
        .first()
        .textContent();
    const faFeeValue = parseFloat(faFeeText?.replace('%', '') || '0');
    expect(faFeeValue).toBeGreaterThan(0);

    // Verify Platform row exists
    await expect(newAccountWizardPageInstance.platformFeeRow).toBeVisible();

    // Get Platform fee percentage and verify it's not 0
    const platformFeeText = await newAccountWizardPageInstance.platformFeeRow
        .locator('td.portfolioColumnData label')
        .first()
        .textContent();
    const platformFeeValue = parseFloat(platformFeeText?.replace('%', '') || '0');
    expect(platformFeeValue).toBeGreaterThan(0);

    // Verify portfolio total value row exists and displays $500,000
    await expect(newAccountWizardPageInstance.portfolioTotalValueRow).toBeVisible();
    await expect(newAccountWizardPageInstance.portfolioTotalValueRow.locator('text=$500,000')).toBeVisible();

    // Verify fee Total row exists
    await expect(newAccountWizardPageInstance.totalFeeRow).toBeVisible();

    // Check if TMS fee row is visible and add it to expected total if present
    let expectedTotal = faFeeValue + platformFeeValue;
    const tmsCount = await newAccountWizardPageInstance.taxManagementServicesFeeRow.count();
    if (tmsCount > 0) {
        const tmsFeeText = await newAccountWizardPageInstance.taxManagementServicesFeeRow
            .locator('td.portfolioColumnData label')
            .first()
            .textContent();
        const tmsFeeValue = parseFloat(tmsFeeText?.replace('%', '') || '0');
        if (tmsFeeValue > 0) {
            expectedTotal += tmsFeeValue;
            logger.debug(`Including TMS fee: ${tmsFeeValue}%`);
        }
    }

    // Get Total fee percentage and verify it equals the sum of all fees
    const totalFeeText = await newAccountWizardPageInstance.totalFeeRow
        .locator('td.portfolioAnnualColumnData label')
        .first()
        .textContent();
    const totalFeeValue = parseFloat(totalFeeText?.replace('%', '') || '0');

    // Verify total equals sum of individual fees (with small tolerance for floating point)
    expect(Math.abs(totalFeeValue - expectedTotal)).toBeLessThan(0.01);
    await newAccountWizardPageInstance.nextButton.click();
});

When('I create the proposal document', async ({}) => {
    const newAccountWizardPageInstance = getNewAccountWizardPageInstance();
    logger.debug('\nCreating the proposal document');
    const portfolioEnginePageInstance = new PortfolioEnginePage(newAccountWizardPageInstance.page);
    setPortfolioEnginePageInstance(portfolioEnginePageInstance);
    await portfolioEnginePageInstance.previewProposalButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});
