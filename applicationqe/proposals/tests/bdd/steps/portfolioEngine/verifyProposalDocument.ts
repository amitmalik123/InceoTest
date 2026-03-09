import { Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { getPortfolioEnginePageInstance } from '../shared/instanceManager';
import { logger } from '../../../../utils/logger';

Then('the proposal document should be generated successfully', async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    logger.debug('\nVerifying proposal sections were generated');
    // Verify the proposal document is loaded
    try {
        await portfolioEnginePageInstance.coverPageHeader.click();
        await expect(portfolioEnginePageInstance.coverPageHeader).toBeVisible();
    } catch (err) {
        logger.error('Cover page header not visible in generated proposal document', err);
        throw err;
    }
});

Then('the document should contain all the relevant information from the proposal', async () => {
    logger.debug('\nVerifying all proposal document sections');
});

Then('the cover page section should be verified', async () => {
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    logger.debug('\nVerifying cover page section...');
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.coverPageHeader,
        portfolioEnginePageInstance.previewLayoutContentFirst
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Cover page validation failed', err);
        throw err;
    }
});

Then('the table of contents section should be verified', async () => {
    logger.debug('\nVerifying table of contents section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.tableOfContentsText,
        portfolioEnginePageInstance.tableOfContentsContent
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Table of contents validation failed', err);
        throw err;
    }
});

Then('the introduction section should be verified', async () => {
    logger.debug('\nVerifying introduction section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.introductionHeader,
        portfolioEnginePageInstance.introductionContent,
        portfolioEnginePageInstance.introductionCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Introduction section validation failed', err);
        throw err;
    }
});

Then('the investing is personal section should be verified', async () => {
    logger.debug('\nVerifying investing is personal section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.clickAndWaitForExpansion(
        portfolioEnginePageInstance.pursuingYourGoalsDropdownIcon
    );
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.investingIsPersonalText,
        portfolioEnginePageInstance.investingContent,
        portfolioEnginePageInstance.investingIsPersonalCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Investing is Personal section validation failed', err);
        throw err;
    }
});

Then('the equities vs bonds section should be verified', async () => {
    logger.debug('\nVerifying equities vs bonds section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.equitiesVsBondsTitle,
        portfolioEnginePageInstance.growthContentFirst,
        portfolioEnginePageInstance.equitiesVsBondsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Equities vs Bonds section validation failed', err);
        throw err;
    }
});

Then('the cycle of emotions section should be verified', async () => {
    logger.debug('\nVerifying cycle of emotions section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.cycleOfEmotionsHeader,
        portfolioEnginePageInstance.theContent,
        portfolioEnginePageInstance.cycleOfEmotionsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Cycle of Emotions section validation failed', err);
        throw err;
    }
});

Then('the staying invested section should be verified', async () => {
    logger.debug('\nVerifying staying invested section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.stayingInvestedTitle,
        portfolioEnginePageInstance.growthContentSecond,
        portfolioEnginePageInstance.stayingInvestedCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Staying Invested section validation failed', err);
        throw err;
    }
});

Then('the investment team section should be verified', async () => {
    logger.debug('\nVerifying investment team section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.yourInvestmentTeamDiv,
        portfolioEnginePageInstance.yourContentCanvas,
        portfolioEnginePageInstance.yourInvestmentTeamCheckboxInside
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Investment Team section validation failed', err);
        throw err;
    }
});

Then('the portfolio strategists section should be verified', async () => {
    logger.debug('\nVerifying portfolio strategists section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.portfolioStrategistsSection,
        portfolioEnginePageInstance.portfolioContent,
        portfolioEnginePageInstance.portfolioStrategistsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Portfolio Strategists section validation failed', err);
        throw err;
    }
});

Then('the custodian selection section should be verified', async () => {
    logger.debug('\nVerifying custodian selection section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.custodianSelectionHeader,
        portfolioEnginePageInstance.custodianContent,
        portfolioEnginePageInstance.custodianSelectionCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Custodian Selection section validation failed', err);
        throw err;
    }
});

Then('the ongoing review section should be verified', async () => {
    logger.debug('\nVerifying ongoing review section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.ongoingReviewText,
        portfolioEnginePageInstance.ongoingContent,
        portfolioEnginePageInstance.ongoingReviewCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Ongoing Review section validation failed', err);
        throw err;
    }
});

Then('the financial analysis section should be verified', async () => {
    logger.debug('\nVerifying financial analysis section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.yourFinancialAnalysisHeader,
        portfolioEnginePageInstance.yourFinancialContent
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Financial Analysis section validation failed', err);
        throw err;
    }
});

Then('the recommended portfolio section should be verified', async () => {
    logger.debug('\nVerifying recommended portfolio section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.clickAndWaitForExpansion(
        portfolioEnginePageInstance.recommendedInvestmentPortfolioDropdownIcon
    );
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.recommendedPortfolioDiv,
        portfolioEnginePageInstance.recommendedContent,
        portfolioEnginePageInstance.recommendedInvestmentPortfolioCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Recommended portfolio section validation failed', err);
        throw err;
    }
});

Then('the allocation by asset class section should be verified', async () => {
    logger.debug('\nVerifying allocation by asset class section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.allocationByAssetClassHeader,
        portfolioEnginePageInstance.allocationContent,
        portfolioEnginePageInstance.allocationByAssetClassCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Allocation by asset class validation failed', err);
        throw err;
    }
});

Then('the top holdings section should be verified', async () => {
    logger.debug('\nVerifying top holdings section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.topHoldingsText,
        portfolioEnginePageInstance.topHoldingsContent,
        portfolioEnginePageInstance.topHoldingsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Top holdings section validation failed', err);
        throw err;
    }
});

Then('the proposed accounts section should be verified', async () => {
    logger.debug('\nVerifying proposed accounts section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.proposedAccountsTitle,
        portfolioEnginePageInstance.proposedContentFirst,
        portfolioEnginePageInstance.proposedAccountsEstimatedYieldCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Proposed accounts section validation failed', err);
        throw err;
    }
});

Then('the hypothetical performance sections should be verified', async () => {
    logger.debug('\nVerifying hypothetical performance sections...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.clickAndWaitForExpansion(
        portfolioEnginePageInstance.hypotheticalHistoricalPerformanceDropdownIcon
    );
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.hypotheticalSectionTitle,
        portfolioEnginePageInstance.hypotheticalContent,
        portfolioEnginePageInstance.hypotheticalGrowthOfProposedAccountsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Hypothetical performance section checks failed', err);
        throw err;
    }
});

Then('the rates section should be verified', async () => {
    logger.debug('\nVerifying rates section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.ratesHeader,
        portfolioEnginePageInstance.ratesContent,
        portfolioEnginePageInstance.ratesCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Rates section validation failed', err);
        throw err;
    }
});

Then('the calendar year returns section should be verified', async () => {
    logger.debug('\nVerifying calendar year returns section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.calendarYearReturnsText,
        portfolioEnginePageInstance.calendarContent,
        portfolioEnginePageInstance.calendarYearReturnsCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Calendar year returns validation failed', err);
        throw err;
    }
});

Then('the historical cumulative section should be verified', async () => {
    logger.debug('\nVerifying historical cumulative section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.historicalCumulativeText,
        portfolioEnginePageInstance.historicalContent,
        portfolioEnginePageInstance.historicalCumulativePerformanceCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Historical cumulative validation failed', err);
        throw err;
    }
});

Then('the risk versus return section should be verified', async () => {
    logger.debug('\nVerifying risk versus return section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.riskVersusReturnSection,
        portfolioEnginePageInstance.riskContent,
        portfolioEnginePageInstance.riskVersusReturnCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Risk vs Return validation failed', err);
        throw err;
    }
});

Then('the fee schedule section should be verified', async () => {
    logger.debug('\nVerifying fee schedule section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.clickAndWaitForExpansion(
        portfolioEnginePageInstance.annualPortfolioFeesDropdownIcon
    );
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.feeScheduleDiv,
        portfolioEnginePageInstance.feeContentFirst
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Fee schedule section validation failed', err);
        throw err;
    }
});

Then('the tiered fee schedule section should be verified', async () => {
    logger.debug('\nVerifying tiered fee schedule section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.tieredFeeScheduleHeader,
        portfolioEnginePageInstance.tieredContent,
        portfolioEnginePageInstance.tieredFeeScheduleCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Tiered fee schedule validation failed', err);
        throw err;
    }
});

Then('the estimated expense section should be verified', async () => {
    logger.debug('\nVerifying estimated expense section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.estimateExpenseTitle,
        portfolioEnginePageInstance.estimatedExpenseCanvas,
        portfolioEnginePageInstance.estimateExpenseCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Estimated expense section validation failed', err);
        throw err;
    }
});

Then('the important information section should be verified', async () => {
    logger.debug('\nVerifying important information section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.importantInformationText,
        portfolioEnginePageInstance.importantInformationCanvas
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Important information section validation failed', err);
        throw err;
    }
});

Then('the disclosures section should be verified', async () => {
    logger.debug('\nVerifying disclosures section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.disclosuresTitle,
        portfolioEnginePageInstance.disclosuresCanvas
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Disclosures section validation failed', err);
        throw err;
    }
});

Then('the tax management services section should be verified', async () => {
    logger.debug('\nVerifying tax management services section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.taxManagementServicesText,
        portfolioEnginePageInstance.taxManagementServicesCanvas
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Tax Management Services section validation failed', err);
        throw err;
    }
});

Then('the client signature section should be verified', async () => {
    logger.debug('\nVerifying client signature section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.clientSignatureText,
        portfolioEnginePageInstance.clientSignatureCanvas,
        portfolioEnginePageInstance.clientSignatureCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Client signature section validation failed', err);
        throw err;
    }
});

Then('the investment policy statement section should be verified', async () => {
    logger.debug('\nVerifying investment policy statement section...');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    const result = await portfolioEnginePageInstance.verifyProposalSection(
        portfolioEnginePageInstance.investmentPolicyStatementText,
        portfolioEnginePageInstance.investmentPolicyCanvas,
        portfolioEnginePageInstance.investmentPolicyStatementCheckbox
    );
    try {
        expect(result).toBeTruthy();
    } catch (err) {
        logger.error('Investment policy statement validation failed', err);
        throw err;
    }
    logger.debug('\nAll proposal document sections verified successfully');
});
