import { When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { selectCustodian } from '../../../../data/proposalVariations';
import { portfolioEnginePageInstance } from './addStrategiesToPortfolio';

When('I click the create proposal button', async () => {
    console.log('\nStarting create proposal with new portfolio and new client test');
    await portfolioEnginePageInstance.createProposalButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then('the portfolio strategies should be displayed correctly', async () => {
    console.log('\nVerifying portfolios & percentages are correct');
    await expect(portfolioEnginePageInstance.assetMarkIncomeBuilderText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.blackRockEquityDividendText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.savosUSRiskText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.alphaSimplexText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.jpMorganAbsoluteReturnText).toBeVisible({ timeout: 300000 });
});

Then('the client type options should be visible and editable', async () => {
    console.log('\nVerifying client type options');
    await expect(portfolioEnginePageInstance.newClientRadio).toBeEditable({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.newClientText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.existingClientRadio).toBeEditable({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.existingClientText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.discretionaryText).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.nonDiscretionaryText).toBeVisible({ timeout: 300000 });
});

When('I fill new client information with first name {string} and last name {string}', async ({ }, firstName: string, lastName: string) => {
    console.log('\nCreating new client');
    await portfolioEnginePageInstance.fillNewClientInfo(firstName, lastName);
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I select a risk profile', async () => {
    console.log('\nSelecting risk profile');
    await portfolioEnginePageInstance.selectRiskProfile();
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I select a custodian and set up account registration', async () => {
    console.log('\nSelecting custodian and registration type');
    await selectCustodian(portfolioEnginePageInstance);
    await portfolioEnginePageInstance.addRegistrationButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState('domcontentloaded');
    await portfolioEnginePageInstance.registrationTypeDropdown.waitFor({ state: 'visible' });
    await portfolioEnginePageInstance.registrationTypeDropdown.click({ force: true });
    await portfolioEnginePageInstance.selectRegistrationType('Individual');
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I add an account with all strategies and investment amount {string}', async ({ }, investmentAmount: string) => {
    console.log('\nAdding account with all 5 strategies');
    await portfolioEnginePageInstance.addAccountButton.click();
    await portfolioEnginePageInstance.selectAllStrategies();
    await portfolioEnginePageInstance.modelListConfirm.click();

    console.log('\nSetting investment amount');
    await portfolioEnginePageInstance.investmentAmountInput.fill(investmentAmount);
    await expect(portfolioEnginePageInstance.enrollInTaxRadio).toBeEditable({ timeout: 300000 });
    await portfolioEnginePageInstance.doNotEnrollInTaxRadio.check();
    await portfolioEnginePageInstance.confirmText.click();
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then('the proposed accounts should display correctly with amount {string}, first name {string}, and last name {string}', async ({ }, expectedAmount: string, firstName: string, lastName: string) => {
    console.log('\nVerifying proposed accounts information');
    await expect(portfolioEnginePageInstance.proposedAccountsHeader).toContainText('Proposed Accounts (1)', { timeout: 300000 });
    await expect(portfolioEnginePageInstance.proposedAccountsAmount).toContainText(expectedAmount, { timeout: 300000 });
    await expect(portfolioEnginePageInstance.accountHolderName).toContainText(`${firstName} ${lastName}, Individual`, { timeout: 300000 });
    await expect(portfolioEnginePageInstance.multipleStrategyAccountName).toContainText('Multiple Strategy Account, Profile', { timeout: 300000 });
    await expect(portfolioEnginePageInstance.multipleStrategyAccountAmount).toContainText(expectedAmount, { timeout: 300000 });
});

When('I enter fee percentage {string}', async ({ }, feePercentage: string) => {
    console.log('\nEntering fee values');
    await portfolioEnginePageInstance.enterFeePercentageTextbox.fill(feePercentage);
    await portfolioEnginePageInstance.page.waitForLoadState();
    await portfolioEnginePageInstance.nextButton.click();
});

Then('the fee summary should display correctly with portfolio value {string} and financial advisor fee {string}', async ({ }, portfolioValue: string, advisorFee: string) => {
    console.log('\nVerifying fee summary values');
    await expect(portfolioEnginePageInstance.portfolioValueAmount).toContainText(portfolioValue, { timeout: 300000 });
    await expect(portfolioEnginePageInstance.financialAdvisorFee).toContainText(advisorFee, { timeout: 300000 });
    await expect(portfolioEnginePageInstance.platformFee).not.toContainText('0.00%', { timeout: 300000 }); // Ensure fee service is returning something
});

Then('the total fee calculation should be correct', async () => {
    console.log('\nValidating total fee calculation');
    const financialAdvisorFeeText = await portfolioEnginePageInstance.financialAdvisorFee.textContent();
    const platformFeeText = await portfolioEnginePageInstance.platformFee.textContent();
    const totalFeeText = await portfolioEnginePageInstance.totalFee.textContent();

    const financialAdvisorValue = parseFloat(financialAdvisorFeeText.replace('%', ''));
    const platformValue = parseFloat(platformFeeText.replace('%', ''));
    const totalValue = parseFloat(totalFeeText.replace('%', ''));
    const expectedTotal = financialAdvisorValue + platformValue;

    if (Math.abs(totalValue - expectedTotal) > 0.01) {
        throw new Error(`Total fee ${totalValue}% does not match sum of Financial Advisor ${financialAdvisorValue}% and Platform ${platformValue}% fees (expected ${expectedTotal}%)`);
    }
    await portfolioEnginePageInstance.page.waitForLoadState();
});

When('I generate the proposal document with all sections', async () => {
    console.log('\nGenerating proposal document with all sections');
    await portfolioEnginePageInstance.nextButton.click();
    await portfolioEnginePageInstance.continueButton.click();
    await portfolioEnginePageInstance.previewProposalButton.click();

    // Make sure all sections are selected in proposal
    await portfolioEnginePageInstance.setAllProposalSections();
});

When('I save the proposal', async () => {
    console.log('\nSaving proposal');
    await portfolioEnginePageInstance.saveProposalButton.click();
    await portfolioEnginePageInstance.viewDocumentsButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
});

Then('the proposal should be saved successfully', async () => {
    console.log('\nVerifying proposal was saved');
    await expect(portfolioEnginePageInstance.oneCombinedDocumentText).toBeVisible({ timeout: 300000 });
});
