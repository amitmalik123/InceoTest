import { When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { portfolioEnginePageInstance } from './addStrategiesToPortfolio';

When('I generate the proposal document', async () => {
    console.log('\nNavigating back to client portfolio details');
    // Navigate back to the client portfolio details after being redirected
    await portfolioEnginePageInstance.navigateToClientPortfolioDetails('Guy Dude, Individual');
    await portfolioEnginePageInstance.page.waitForLoadState();
    await portfolioEnginePageInstance.previewProposalButton.click();
    await portfolioEnginePageInstance.page.waitForLoadState();
    await portfolioEnginePageInstance.setAllProposalSections();
});

Then('the proposal document should be generated successfully', async () => {
    console.log('\nVerifying proposal sections were generated');
    // Verify the proposal document is loaded
    await expect(portfolioEnginePageInstance.coverPageHeader).toBeVisible({ timeout: 300000 });
});

Then('the document should contain all the relevant information from the proposal', async () => {
    console.log('\nVerifying all proposal document sections');
});

Then('the cover page section should be verified', async () => {
    console.log('\nVerifying cover page section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.coverPageHeader, portfolioEnginePageInstance.previewLayoutContentFirst);
    expect(result).toBeTruthy();
});

Then('the table of contents section should be verified', async () => {
    console.log('\nVerifying table of contents section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.tableOfContentsText, portfolioEnginePageInstance.tableOfContentsContent);
    expect(result).toBeTruthy();
});

Then('the introduction section should be verified', async () => {
    console.log('\nVerifying introduction section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.introductionHeader, portfolioEnginePageInstance.introductionContent);
    expect(result).toBeTruthy();
});

Then('the pursuing your goals checkbox should be checked', async () => {
    console.log('\nVerifying pursuing your goals checkbox...');
    await expect(portfolioEnginePageInstance.pursuingYourGoalsCheckbox.first()).toBeChecked({ timeout: 300000 });
});

Then('the investing is personal section should be verified', async () => {
    console.log('\nVerifying investing is personal section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.investingIsPersonalText, portfolioEnginePageInstance.investingContent);
    expect(result).toBeTruthy();
});

Then('the equities vs bonds section should be verified', async () => {
    console.log('\nVerifying equities vs bonds section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.equitiesVsBondsTitle, portfolioEnginePageInstance.growthContentFirst);
    expect(result).toBeTruthy();
});

Then('the cycle of emotions section should be verified', async () => {
    console.log('\nVerifying cycle of emotions section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.cycleOfEmotionsHeader, portfolioEnginePageInstance.theContent);
    expect(result).toBeTruthy();
});

Then('the staying invested section should be verified', async () => {
    console.log('\nVerifying staying invested section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.stayingInvestedTitle, portfolioEnginePageInstance.growthContentSecond);
    expect(result).toBeTruthy();
});

Then('the investment team section should be verified', async () => {
    console.log('\nVerifying investment team section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.yourInvestmentTeamDiv, portfolioEnginePageInstance.yourContentCanvas);
    expect(result).toBeTruthy();
});

Then('the portfolio strategists section should be verified', async () => {
    console.log('\nVerifying portfolio strategists section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.portfolioStrategistsSection, portfolioEnginePageInstance.portfolioContent);
    expect(result).toBeTruthy();
});

Then('the custodian selection section should be verified', async () => {
    console.log('\nVerifying custodian selection section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.custodianSelectionHeader, portfolioEnginePageInstance.custodianContent);
    expect(result).toBeTruthy();
});

Then('the ongoing review section should be verified', async () => {
    console.log('\nVerifying ongoing review section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.ongoingReviewText, portfolioEnginePageInstance.ongoingContent);
    expect(result).toBeTruthy();
});

Then('the financial analysis section should be verified', async () => {
    console.log('\nVerifying financial analysis section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.yourFinancialAnalysisHeader, portfolioEnginePageInstance.yourFinancialContent);
    expect(result).toBeTruthy();
});

Then('the recommended investment portfolio checkbox should be checked', async () => {
    console.log('\nVerifying recommended investment portfolio checkbox...');
    await expect(portfolioEnginePageInstance.recommendedInvestmentPortfolioCheckbox).toBeChecked({ timeout: 300000 });
});

Then('the recommended portfolio section should be verified', async () => {
    console.log('\nVerifying recommended portfolio section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.recommendedPortfolioDiv, portfolioEnginePageInstance.recommendedContent);
    expect(result).toBeTruthy();
});

Then('the allocation by asset class section should be verified', async () => {
    console.log('\nVerifying allocation by asset class section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.allocationByAssetClassHeader, portfolioEnginePageInstance.allocationContent);
    expect(result).toBeTruthy();
});

Then('the top holdings section should be verified', async () => {
    console.log('\nVerifying top holdings section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.topHoldingsText, portfolioEnginePageInstance.topHoldingsContent);
    expect(result).toBeTruthy();
});

Then('the proposed accounts section should be verified', async () => {
    console.log('\nVerifying proposed accounts section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.proposedAccountsTitle, portfolioEnginePageInstance.proposedContentFirst);
    expect(result).toBeTruthy();
});

Then('the hypothetical performance sections should be verified', async () => {
    console.log('\nVerifying hypothetical performance sections...');
    await portfolioEnginePageInstance.hypotheticalHistoricalPerformanceDiv.click();
    console.log('\nVerifying hypothetical historical performance checkbox...');
    await expect(portfolioEnginePageInstance.hypotheticalHistoricalPerformanceCheckbox).toBeChecked({ timeout: 300000 });
    await portfolioEnginePageInstance.hypotheticalSectionTitle.click();
    console.log('\nVerifying hypothetical growth of proposed accounts checkbox...');
    await expect(portfolioEnginePageInstance.hypotheticalGrowthOfProposedAccountsCheckbox).toBeChecked({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.hypotheticalContent).toBeVisible({ timeout: 300000 });
});

Then('the rates section should be verified', async () => {
    console.log('\nVerifying rates section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.ratesHeader, portfolioEnginePageInstance.ratesContent);
    expect(result).toBeTruthy();
});

Then('the calendar year returns section should be verified', async () => {
    console.log('\nVerifying calendar year returns section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.calendarYearReturnsText, portfolioEnginePageInstance.calendarContent);
    expect(result).toBeTruthy();
});

Then('the historical cumulative section should be verified', async () => {
    console.log('\nVerifying historical cumulative section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.historicalCumulativeText, portfolioEnginePageInstance.historicalContent);
    expect(result).toBeTruthy();
});

Then('the risk versus return section should be verified', async () => {
    console.log('\nVerifying risk versus return section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.riskVersusReturnSection, portfolioEnginePageInstance.riskContent);
    expect(result).toBeTruthy();
});

Then('the annual portfolio fees checkbox should be checked', async () => {
    console.log('\nVerifying annual portfolio fees checkbox...');
    await expect(portfolioEnginePageInstance.annualPortfolioFeesCheckbox).toBeChecked({ timeout: 300000 });
});

Then('the fee schedule section should be verified', async () => {
    console.log('\nVerifying fee schedule section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.feeScheduleDiv, portfolioEnginePageInstance.feeContentFirst);
    expect(result).toBeTruthy();
});

Then('the tiered fee schedule section should be verified', async () => {
    console.log('\nVerifying tiered fee schedule section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.tieredFeeScheduleHeader, portfolioEnginePageInstance.tieredContent);
    expect(result).toBeTruthy();
});

Then('the estimated expense section should be verified', async () => {
    console.log('\nVerifying estimated expense section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.estimateExpenseTitle, portfolioEnginePageInstance.estimatedExpenseCanvas);
    expect(result).toBeTruthy();
});

Then('the important information section should be verified', async () => {
    console.log('\nVerifying important information section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.importantInformationText, portfolioEnginePageInstance.importantInformationCanvas);
    expect(result).toBeTruthy();
});

Then('the disclosures section should be verified', async () => {
    console.log('\nVerifying disclosures section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.disclosuresTitle, portfolioEnginePageInstance.disclosuresCanvas);
    expect(result).toBeTruthy();
});

Then('the client signature section should be verified', async () => {
    console.log('\nVerifying client signature section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.clientSignatureText, portfolioEnginePageInstance.clientSignatureCanvas);
    expect(result).toBeTruthy();
});

Then('the investment policy statement section should be verified', async () => {
    console.log('\nVerifying investment policy statement section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(portfolioEnginePageInstance.investmentPolicyStatementText, portfolioEnginePageInstance.investmentPolicyCanvas);
    expect(result).toBeTruthy();
    console.log('\nAll proposal document sections verified successfully');
});


