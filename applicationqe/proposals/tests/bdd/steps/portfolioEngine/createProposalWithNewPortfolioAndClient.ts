import { When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { selectCustodian } from '../../../../data/proposalVariations';
import {
    buildProposalTextValidationManifest,
    buildProposalTextValidationManifestExcludingTMS,
} from '../../../../data/proposalPdfTextManifest';
import { downloadAndValidatePdfFromClick } from '../../../../utils/pdfUtils';
import { getPortfolioEnginePageInstance } from '../shared/instanceManager';
import { logger } from '../../../../utils/logger';

When('I click the create proposal button', async () => {
    logger.debug('\nStarting create proposal with new portfolio and new client test');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.createProposalButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then('the portfolio strategies should be displayed correctly', async () => {
    logger.debug('\nVerifying portfolios & percentages are correct');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await expect(portfolioEnginePageInstance.assetMarkIncomeBuilderText).toBeVisible();
    await expect(portfolioEnginePageInstance.blackRockEquityDividendText).toBeVisible();
    await expect(portfolioEnginePageInstance.savosUSRiskText).toBeVisible();
    await expect(portfolioEnginePageInstance.alphaSimplexText).toBeVisible();
    await expect(portfolioEnginePageInstance.jpMorganAbsoluteReturnText).toBeVisible();
});

Then('the client type options should be visible and editable', async () => {
    logger.debug('\nVerifying client type options');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await expect(portfolioEnginePageInstance.newClientRadio).toBeEditable();
    await expect(portfolioEnginePageInstance.newClientText).toBeVisible();
    await expect(portfolioEnginePageInstance.existingClientRadio).toBeEditable();
    await expect(portfolioEnginePageInstance.existingClientText).toBeVisible();
    await expect(portfolioEnginePageInstance.discretionaryText).toBeVisible();
    await expect(portfolioEnginePageInstance.nonDiscretionaryText).toBeVisible();
});

When(
    'I fill new client information with first name {string} and last name {string}',
    async ({}, firstName: string, lastName: string) => {
        logger.debug('\nCreating new client');
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        await portfolioEnginePageInstance.fillNewClientInfo(firstName, lastName);
        await portfolioEnginePageInstance.nextButton.click();
        await portfolioEnginePageInstance.page.waitForLoadState();
    }
);

When('I select a risk profile', async () => {
    logger.debug('\nSelecting risk profile');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.selectRiskProfile();
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I select a custodian and set up account registration', async () => {
    logger.debug('\nSelecting custodian and registration type');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await selectCustodian(portfolioEnginePageInstance);
    await portfolioEnginePageInstance.addRegistrationButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState('domcontentloaded');
    await portfolioEnginePageInstance.registrationTypeDropdown.waitFor({ state: 'visible' });
    await portfolioEnginePageInstance.registrationTypeDropdown.click();
    await portfolioEnginePageInstance.selectRegistrationType('Individual');
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I add an account with all strategies and investment amount {string}', async ({}, investmentAmount: string) => {
    logger.debug('\nAdding account with all 5 strategies');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.addAccountButton.click();
    await portfolioEnginePageInstance.selectAllStrategies();
    await portfolioEnginePageInstance.modelListConfirm.click();

    logger.debug('\nSetting investment amount');
    await portfolioEnginePageInstance.investmentAmountInput.fill(investmentAmount);
    await expect(portfolioEnginePageInstance.enrollInTaxRadio).toBeEditable();
    await portfolioEnginePageInstance.doNotEnrollInTaxRadio.check();
    await portfolioEnginePageInstance.confirmText.click();
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then(
    'the proposed accounts should display correctly with amount {string}, first name {string}, and last name {string}',
    async ({}, expectedAmount: string, firstName: string, lastName: string) => {
        logger.debug('\nVerifying proposed accounts information');
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        await expect(portfolioEnginePageInstance.proposedAccountsHeader).toContainText('Proposed Accounts (1)', {});
        await expect(portfolioEnginePageInstance.proposedAccountsAmount).toContainText(expectedAmount, {});
        await expect(portfolioEnginePageInstance.accountHolderName).toContainText(
            `${firstName} ${lastName}, Individual`
        );
        await expect(portfolioEnginePageInstance.multipleStrategyAccountName).toContainText(
            'Multiple Strategy Account, Profile'
        );
        await expect(portfolioEnginePageInstance.multipleStrategyAccountAmount).toContainText(expectedAmount, {});
    }
);

When('I enter fee percentage {string}', async ({}, feePercentage: string) => {
    logger.debug('\nEntering fee values');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.enterFeePercentageTextbox.fill(feePercentage);
    await portfolioEnginePageInstance.page.waitForLoadState();
    await portfolioEnginePageInstance.nextButton.click();
});

Then(
    'the fee summary should display correctly with portfolio value {string} and financial advisor fee {string}',
    async ({}, portfolioValue: string, advisorFee: string) => {
        logger.debug('\nVerifying fee summary values');
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        await expect(portfolioEnginePageInstance.portfolioValueAmount).toContainText(portfolioValue, {});
        await expect(portfolioEnginePageInstance.financialAdvisorFee).toContainText(advisorFee);
        await expect(portfolioEnginePageInstance.platformFee).not.toContainText('0.00%'); // Ensure fee service is returning something
    }
);

Then('the total fee calculation should be correct', async () => {
    logger.debug('\nValidating total fee calculation');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const financialAdvisorFeeText = await portfolioEnginePageInstance.financialAdvisorFee.textContent();
    const platformFeeText = await portfolioEnginePageInstance.platformFee.textContent();
    const totalFeeText = await portfolioEnginePageInstance.totalFee.textContent();

    const financialAdvisorValue = parseFloat(financialAdvisorFeeText.replace('%', ''));
    const platformValue = parseFloat(platformFeeText.replace('%', ''));
    const totalValue = parseFloat(totalFeeText.replace('%', ''));
    const expectedTotal = financialAdvisorValue + platformValue;

    if (Math.abs(totalValue - expectedTotal) > 0.01) {
        throw new Error(
            `Total fee ${totalValue}% does not match sum of Financial Advisor ${financialAdvisorValue}% and Platform ${platformValue}% fees (expected ${expectedTotal}%)`
        );
    }
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I generate the proposal document with all sections', async () => {
    logger.debug('\nGenerating proposal document with all sections');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.continueButton.click();
    await portfolioEnginePageInstance.previewProposalButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I save the proposal', async () => {
    logger.debug('\nSaving proposal');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.saveProposalButton.click();
    await portfolioEnginePageInstance.viewDocumentsButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then(
    'the proposal should be saved successfully with {int} pages including Tax Management Services',
    async ({}, expectedProposalPageCount: number) => {
        logger.debug('\nVerifying proposal was saved with Tax Management Services');
        const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
        await expect(portfolioEnginePageInstance.oneCombinedDocumentText).toBeVisible();

        // Adjust for prod environment
        if (process.env.Environment.toLowerCase() === 'prod') {
            expectedProposalPageCount += 3;
        }

        const proposalTextValidation = buildProposalTextValidationManifest({
            includeTableOfContents: true,
        });

        await downloadAndValidatePdfFromClick(
            portfolioEnginePageInstance.page,
            () => portfolioEnginePageInstance.oneCombinedDocumentText.click(),
            {
                expectedPageCount: expectedProposalPageCount,
                filenamePrefix: 'proposal',
                expectedBrowserFilename: 'DownloadCombinedDocuments.pdf',
                proposalTextValidation,
            }
        );
    }
);

Then('the proposal should be saved successfully with {int} pages', async ({}, expectedProposalPageCount: number) => {
    logger.debug('\nVerifying proposal was saved');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await expect(portfolioEnginePageInstance.oneCombinedDocumentText).toBeVisible();

    // Adjust for prod environment
    if (process.env.Environment.toLowerCase() === 'prod') {
        expectedProposalPageCount += 3;
    }

    const proposalTextValidation = buildProposalTextValidationManifestExcludingTMS({
        includeTableOfContents: true,
    });

    await downloadAndValidatePdfFromClick(
        portfolioEnginePageInstance.page,
        () => portfolioEnginePageInstance.oneCombinedDocumentText.click(),
        {
            expectedPageCount: expectedProposalPageCount,
            filenamePrefix: 'proposal',
            expectedBrowserFilename: 'DownloadCombinedDocuments.pdf',
            proposalTextValidation,
        }
    );
});
