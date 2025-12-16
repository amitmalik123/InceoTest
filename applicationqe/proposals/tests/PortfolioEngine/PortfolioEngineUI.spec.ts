import { test, Page } from '@playwright/test';
import { expect } from '@fixtures/fixtures';
import { PortfolioEnginePage } from '@pages/PortfolioEngineObjectModel';
import { navigateToPortfolioEngine } from '@helperfunctions/navigateToPortfolioEngine';
import { navigateToHomePage } from '@helperfunctions/navigateToHomePage';
import { selectIfVisible } from '@helperfunctions/selectIfVisible';
import { selectCustodian, selectRegistrationType } from '@datafactory/proposalVariations';



let page1: Page;
let portfolioEnginePage: PortfolioEnginePage;


test.describe.configure({ mode: 'serial' }); //Have to add strategies, then create prposal, then validate proposal doc in order

test.describe('Portfolio Engine Prep', () => {

    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from Portfolio Engine home page
    test.beforeEach('Navigate to Portfolio Engine Home Page', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
        portfolioEnginePage = new PortfolioEnginePage(portfolioEnginePageObject);

    });

    test('Add strategies to portfolio', async ({ page }) => {
        await expect(portfolioEnginePage.getStartedButton.or(portfolioEnginePage.managePortfoliosButton)).toBeVisible({ timeout: 15_000 });
        if (await portfolioEnginePage.getStartedButton.isVisible()) {
            await portfolioEnginePage.getStartedButton.click();
        } else if (await portfolioEnginePage.managePortfoliosButton.isVisible()) {
            await portfolioEnginePage.managePortfoliosButton.click();
        }
        //Open create portfolio window
        await portfolioEnginePage.createNewModelPortfolioButton.click();
        await portfolioEnginePage.assetMarkPlatformStrategiesText.click();

        // Add strategies using the helper method
        /*TODO: Create data driven way to add strategies*/
        await portfolioEnginePage.addStrategyToPortfolio('assetmark income builder, profile 2, conservative');
        await portfolioEnginePage.addStrategyToPortfolio('blackrock equity dividend');
        await portfolioEnginePage.addStrategyToPortfolio('savos us risk controlled strategy, profile 6');
        await portfolioEnginePage.addStrategyToPortfolio('alphasimplex, alternative model portfolio, profile 5, growth');
        await portfolioEnginePage.addStrategyToPortfolio('jpmorgan absolute return - profile 1');

        await portfolioEnginePage.modelPortfolioNameTextbox.fill('Test Portfolio');
        await portfolioEnginePage.strategySaveButton.click();
        await portfolioEnginePage.page.waitForLoadState();

        //Verify each strategy was added
        await expect(portfolioEnginePage.investmentAllocationText).toContainText('Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1');

        //verify allocation percentages
        await expect(portfolioEnginePage.getAllocationTextbox(0)).toHaveValue('20');
        await expect(portfolioEnginePage.getAllocationTextbox(1)).toHaveValue('20');
        await expect(portfolioEnginePage.getAllocationTextbox(2)).toHaveValue('20');
        await expect(portfolioEnginePage.getAllocationTextbox(3)).toHaveValue('20');
        await expect(portfolioEnginePage.getAllocationTextbox(4)).toHaveValue('20');

    });
});



test.describe('Portfolio Engine Happy Path Tests', () => {

    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from Portfolio Engine home page
    test.beforeEach('Navigate to Portfolio Engine Home Page', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePageObject = await navigateToPortfolioEngine(page);
        portfolioEnginePage = new PortfolioEnginePage(portfolioEnginePageObject);

    });


    test('Portfolio Engine Widgets Load', async ({ page }) => {
        // Select all widgets only if they are not already selected
        await portfolioEnginePage.selectAllWidgetsIfNeeded();
        await portfolioEnginePage.page.waitForLoadState('domcontentloaded');
        //Verify all widget headers are loaded
        await expect(portfolioEnginePage.upsideDownsideCaptureHeader).toBeVisible({ timeout: 15_000 });
        await expect(portfolioEnginePage.investmentApproachHeader).toBeVisible();
        await expect(portfolioEnginePage.returnByStrategyHeader).toBeVisible();
        await expect(portfolioEnginePage.stressTestHeader).toBeVisible();
        await expect(portfolioEnginePage.assetAllocationHoldingsHeader).toBeVisible();
        await expect(portfolioEnginePage.riskVsReturnHeader).toBeVisible();
        await expect(portfolioEnginePage.summaryStatisticsHeader).toBeVisible();
        await expect(portfolioEnginePage.drawdownHeader).toBeVisible();
        await expect(portfolioEnginePage.performanceHeader).toBeVisible();

        // Verify all widget graph containers contain data
        await portfolioEnginePage.verifyAllGraphsHaveData();
    });

    test('Create proposal with new portfolio and new client', async ({ page }) => {
        //Create proposal using newly created portfolio
        await portfolioEnginePage.createProposalButton.click();
        await portfolioEnginePage.quitProposalButton.click();
        await portfolioEnginePage.createProposalButton.click(); //opening twice because the page does not always load the first time
        await page.waitForLoadState();

        //Verify portfolios & percentages are correct on left dropdown
        await expect(portfolioEnginePage.assetMarkIncomeBuilderText).toBeVisible({ timeout: 15_000 });
        await expect(portfolioEnginePage.blackRockEquityDividendText).toBeVisible();
        await expect(portfolioEnginePage.savosUSRiskText).toBeVisible();
        await expect(portfolioEnginePage.alphaSimplexText).toBeVisible();
        await expect(portfolioEnginePage.jpMorganAbsoluteReturnText).toBeVisible();

        //Verify client type options are visible and editable
        await expect(portfolioEnginePage.newClientRadio).toBeEditable();
        await expect(portfolioEnginePage.newClientText).toBeVisible();
        await expect(portfolioEnginePage.existingClientRadio).toBeEditable();
        await expect(portfolioEnginePage.existingClientText).toBeVisible();
        await expect(portfolioEnginePage.discretionaryText).toBeVisible();
        await expect(portfolioEnginePage.nonDiscretionaryText).toBeVisible();

        //Fill new client information
        await portfolioEnginePage.fillNewClientInfo('Guy', 'Dude');
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Select risk profile
        await portfolioEnginePage.selectRiskProfile();
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Select custodian and set up account
        await selectCustodian(portfolioEnginePage);
        await portfolioEnginePage.addRegistrationButton.click();
        await portfolioEnginePage.registrationNameTextbox.click();
        await portfolioEnginePage.registrationNameTextbox.fill('Test Registration');
        await portfolioEnginePage.registrationTypeDropdown.click();
        await portfolioEnginePage.individualCategory.click();
        await portfolioEnginePage.individualOption.click();
        await page.waitForLoadState();

        //Select all strategies
        await portfolioEnginePage.addAccountButton.click();
        await portfolioEnginePage.selectAllStrategies();

        await portfolioEnginePage.modelListConfirmEnable.click();
        await portfolioEnginePage.investmentAmountInput.fill('$500000');
        await expect(portfolioEnginePage.enrollInTaxRadio).toBeEditable();
        await portfolioEnginePage.doNotEnrollInTaxRadio.check();
        await portfolioEnginePage.confirmText.click();
        await portfolioEnginePage.nextButton.click();
        await page.waitForLoadState();

        //Assert left box is correct after proposing accounts
        await expect(portfolioEnginePage.proposedAccountsText).toContainText('Proposed Accounts (1)$ 500,000');
        await expect(portfolioEnginePage.accountHolderNameParagraph).toBeVisible();
        await expect(portfolioEnginePage.multipleStrategyAccountParagraph).toBeVisible();

        //Check fee values
        await portfolioEnginePage.enterPercentageTextbox.fill('.5');
        await page.waitForLoadState();
        await portfolioEnginePage.nextButton.click();
        await expect(portfolioEnginePage.portfolioValueText).toContainText('500,000', { timeout: 15_000 });
        await expect(portfolioEnginePage.financialAdvisorText).toContainText('0.50%');
        await expect(portfolioEnginePage.platformText).not.toContainText('0.00%'); //ensure fee service is calculated
        await expect(portfolioEnginePage.totalText).not.toContainText('0.00%'); //ensure total annual fee is calculated
        await page.waitForLoadState();

        //Assert left boxes are correct
        await expect(portfolioEnginePage.proposedAccountsText).toBeVisible();
        await expect(portfolioEnginePage.accountHolderNameParagraph).toBeVisible();


        await portfolioEnginePage.nextButton.click();
        await portfolioEnginePage.continueButton.click();

        await portfolioEnginePage.previewProposalButton.click();

        //Make sure all sections are selected in proposal
        await portfolioEnginePage.setAllProposalSections();

        await portfolioEnginePage.saveProposalButton.click();
        await portfolioEnginePage.viewDocumentsButton.click();
        await portfolioEnginePage.page.waitForLoadState();

        //Verify we made it back to document list
        await expect(portfolioEnginePage.oneCombinedDocumentText).toBeVisible({ timeout: 15_000 });
    });
});

test.describe('Check proposal doc', () => {
    //apply storage state of role from auth file created in setup
    test.use({ storageState: './authfiles/role1.json' });
    //Start each test from home page
    test.beforeEach('Navigate to eWm Home Page', async ({ page }) => {
        await navigateToHomePage(page);
    });

    test('Verify proposal document', async ({ page }) => {
        //Navigate to created proposal in portfolio details
        const proposalDocPage = new PortfolioEnginePage(page);

        await proposalDocPage.clientsLink.click();
        await page.waitForLoadState();
        await proposalDocPage.searchForClient('guy dude');
        await page.waitForLoadState();
        await proposalDocPage.navigateToClientPortfolioDetails();
        await page.waitForLoadState();
        await proposalDocPage.previewProposalButton.click();
        await page.waitForLoadState();

        await proposalDocPage.setAllProposalSections();

        //Click through each section and make sure doc is generated
        //check cover page
        await proposalDocPage.coverPageHeader.click();
        await proposalDocPage.pursueYourGoalsText.click();
        await expect(proposalDocPage.previewLayoutContentFirst).toBeVisible();

        //check table of contents
        await proposalDocPage.tableOfContentsText.click();
        await expect(proposalDocPage.tableOfContentsContent).toBeVisible();

        //check introduction
        await expect(proposalDocPage.introductionCheckbox).toBeChecked();
        await proposalDocPage.introductionHeader.click();
        await expect(proposalDocPage.introductionContent).toBeVisible();

        //check pursue your goals
        await expect(proposalDocPage.pursuingYourGoalsCheckbox.first()).toBeChecked();

        //check investing is personal
        await expect(proposalDocPage.investingIsPersonalCheckbox).toBeChecked();
        await proposalDocPage.investingIsPersonalText.click();
        await expect(proposalDocPage.investingContent).toBeVisible();

        //check equities vs bonds
        await expect(proposalDocPage.equitiesVsBondsCheckbox).toBeChecked();
        await proposalDocPage.equitiesVsBondsTitle.click();
        await expect(proposalDocPage.growthContentFirst).toBeVisible();

        //check cycle of emotions
        await expect(proposalDocPage.cycleOfEmotionsCheckbox).toBeChecked();
        await proposalDocPage.cycleOfEmotionsHeader.click();
        await expect(proposalDocPage.theContent).toBeVisible();

        //check staying invested
        await expect(proposalDocPage.stayingInvestedCheckbox).toBeChecked();
        await proposalDocPage.stayingInvestedTitle.click();
        await expect(proposalDocPage.growthContentSecond).toBeVisible();

        //check your investment team
        await expect(proposalDocPage.yourInvestmentTeamCheckboxTop).toBeChecked();
        await proposalDocPage.yourInvestmentTeamDiv.click();
        await expect(proposalDocPage.yourContentCanvas).toBeVisible();

        //check portfolio strategists
        await expect(proposalDocPage.portfolioStrategistsCheckbox).toBeChecked();
        await proposalDocPage.portfolioStrategistsSection.click();
        await expect(proposalDocPage.portfolioContent).toBeVisible();

        //check custodian selection
        await expect(proposalDocPage.custodianSelectionCheckbox).toBeChecked();
        await proposalDocPage.custodianSelectionHeader.click();
        await expect(proposalDocPage.custodianContent).toBeVisible();

        //check ongoing review
        await expect(proposalDocPage.ongoingReviewCheckbox).toBeChecked();
        await proposalDocPage.ongoingReviewText.click();
        await expect(proposalDocPage.ongoingContent).toBeVisible();

        //check your financial analysis
        await proposalDocPage.yourFinancialAnalysisHeader.click();
        await expect(proposalDocPage.yourFinancialContent).toBeVisible();

        //check recommended investment portfolio
        await expect(proposalDocPage.recommendedInvestmentPortfolioCheckbox).toBeChecked();

        //check recommended portfolio
        await proposalDocPage.recommendedPortfolioDiv.click();
        await expect(proposalDocPage.recommendedContent).toBeVisible();

        //check allocation by asset class
        await proposalDocPage.allocationByAssetClassHeader.click();
        await expect(proposalDocPage.allocationContent).toBeVisible();

        //check top holdings
        await proposalDocPage.topHoldingsText.click();
        await expect(proposalDocPage.topHoldingsContent).toBeVisible();

        //check proposed accounts estimated yield
        await expect(proposalDocPage.proposedAccountsEstimatedYieldCheckbox).toBeChecked();
        await proposalDocPage.proposedAccountsTitle.click();
        await expect(proposalDocPage.proposedContentFirst).toBeVisible();

        //check hypothetical historical performance
        await proposalDocPage.hypotheticalHistoricalPerformanceDiv.click();
        await expect(proposalDocPage.hypotheticalHistoricalPerformanceCheckbox).toBeChecked();

        //check hypothetical section
        await proposalDocPage.hypotheticalSectionTitle.click();
        await expect(proposalDocPage.hypotheticalSectionCheckbox).toBeChecked();
        await expect(proposalDocPage.hypotheticalContent).toBeVisible();

        //check rates section
        await expect(proposalDocPage.ratesCheckbox).toBeChecked();
        await proposalDocPage.ratesHeader.click();
        await expect(proposalDocPage.ratesContent).toBeVisible();

        //check calendar year returns
        await proposalDocPage.calendarYearReturnsText.click();
        await expect(proposalDocPage.calendarContent).toBeVisible();

        //check historical cumulative performance
        await proposalDocPage.historicalCumulativeText.click();
        await expect(proposalDocPage.historicalContent).toBeVisible();

        //check risk versus return
        await proposalDocPage.riskVersusReturnSection.click();
        await expect(proposalDocPage.riskContent).toBeVisible();

        //check annual portfolio fees
        await expect(proposalDocPage.annualPortfolioFeesCheckbox).toBeChecked();

        //check fee schedule
        await proposalDocPage.feeScheduleDiv.click();
        await expect(proposalDocPage.feeContentFirst).toBeVisible();

        //check tiered fee schedule
        await expect(proposalDocPage.tieredFeeScheduleCheckbox).toBeChecked();
        await proposalDocPage.tieredFeeScheduleHeader.click();
        await expect(proposalDocPage.tieredContent).toBeVisible();

        //check estimate expense
        await expect(proposalDocPage.estimateExpenseCheckbox).toBeChecked();
        await proposalDocPage.estimateExpenseTitle.click();
        await expect(proposalDocPage.estimatedExpenseCanvas).toBeVisible();

        //check important information
        await proposalDocPage.importantInformationText.click();
        await expect(proposalDocPage.importantInformationCanvas).toBeVisible();

        //check disclosures
        await proposalDocPage.disclosuresTitle.click();
        await expect(proposalDocPage.disclosuresCanvas).toBeVisible();

        //check client signature
        await expect(proposalDocPage.clientSignatureCheckbox).toBeChecked();
        await proposalDocPage.clientSignatureText.click();
        await expect(proposalDocPage.clientSignatureCanvas).toBeVisible();

        //check investment policy statement
        await expect(proposalDocPage.investmentPolicyStatementCheckbox).toBeChecked();
        await proposalDocPage.investmentPolicyStatementText.click();
        await expect(proposalDocPage.investmentPolicyCanvas).toBeVisible();
    });
});