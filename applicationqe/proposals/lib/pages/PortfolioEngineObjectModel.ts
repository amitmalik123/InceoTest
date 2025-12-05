import { type Locator, type Page } from '@playwright/test';

export class PortfolioEnginePage {
    readonly page: Page;

    // Navigation Links (Main Page)
    readonly investmentsLink: Locator;
    readonly portfolioEngineLink: Locator;
    readonly launchPortfolioEngineImg: Locator;
    readonly clientsLink: Locator;
    readonly getStartedButton: Locator;

    // Widget Headers
    readonly upsideDownsideCaptureHeader: Locator;
    readonly investmentApproachHeader: Locator;
    readonly returnByStrategyHeader: Locator;
    readonly stressTestHeader: Locator;
    readonly assetAllocationHoldingsHeader: Locator;
    readonly riskVsReturnHeader: Locator;
    readonly summaryStatisticsHeader: Locator;
    readonly drawdownHeader: Locator;
    readonly performanceHeader: Locator;

    // Widget Selection Checkboxes
    readonly widgetSelectionDropdownButton: Locator;
    readonly widgetCheckbox1: Locator;
    readonly widgetCheckbox2: Locator;
    readonly widgetCheckbox3: Locator;
    readonly widgetCheckbox4: Locator;
    readonly widgetCheckbox5: Locator;
    readonly widgetCheckbox6: Locator;
    readonly widgetCheckbox7: Locator;
    readonly widgetCheckbox8: Locator;
    readonly widgetCheckbox9: Locator;

    // Graph Containers
    readonly graphContainer1: Locator;
    readonly graphContainer2: Locator;
    readonly graphContainer3: Locator;
    readonly graphContainer4: Locator;
    readonly graphContainer5: Locator;
    readonly graphContainer6: Locator;
    readonly graphContainer7: Locator;
    readonly graphContainer8: Locator;
    readonly graphContainer9: Locator;

    // Portfolio Management Buttons
    readonly managePortfoliosButton: Locator;
    readonly createNewModelPortfolioButton: Locator;
    readonly strategySaveButton: Locator;
    readonly createProposalButton: Locator;

    // Portfolio Management - Delete Elements
    readonly portfolioDeleteControlButton: Locator;
    readonly portfolioDeleteText: Locator;
    readonly portfolioDeleteConfirmButton: Locator;
    readonly previewProposalButton: Locator;
    readonly saveProposalButton: Locator;
    readonly viewDocumentsButton: Locator;

    // Portfolio Creation Elements
    readonly assetMarkPlatformStrategiesText: Locator;
    readonly strategySearchBox: Locator;
    readonly addToPortfolioText: Locator;
    readonly modelPortfolioNameTextbox: Locator;
    readonly investmentAllocationText: Locator;

    // Proposal Creation - Client Type
    readonly newClientRadio: Locator;
    readonly newClientText: Locator;
    readonly existingClientRadio: Locator;
    readonly existingClientText: Locator;
    readonly discretionaryRadio: Locator;
    readonly discretionaryText: Locator;
    readonly nonDiscretionaryRadio: Locator;
    readonly nonDiscretionaryText: Locator;
    readonly firstNameTextbox: Locator;
    readonly lastNameTextbox: Locator;
    readonly nextButton: Locator;

    // Proposal Creation - Risk Profile
    readonly moderateRiskRadio: Locator;
    readonly timeHorizonNineYearsRadio: Locator;
    readonly declineFiftyPercentRadio: Locator;
    readonly riskToleranceModerateRadio: Locator;

    // Proposal Creation - Account Setup
    readonly selectCustodianDropdown: Locator;
    readonly fidelityText: Locator;
    readonly pershingAdvisorSolutionsText: Locator;
    readonly assetMarkText: Locator;
    readonly schwabText: Locator;
    readonly addRegistrationButton: Locator;
    readonly registrationNameTextbox: Locator;
    readonly registrationTypeDropdown: Locator;
    readonly individualCategory: Locator;
    readonly individualOption: Locator;
    readonly addAccountButton: Locator;
    readonly modelListConfirmEnable: Locator;
    readonly investmentAmountInput: Locator;
    readonly enrollInTaxRadio: Locator;
    readonly doNotEnrollInTaxRadio: Locator;
    readonly confirmText: Locator;

    // Proposal Creation - Verification Elements
    readonly proposedAccountsText: Locator;
    readonly accountHolderNameParagraph: Locator;
    readonly multipleStrategyAccountParagraph: Locator;
    readonly enterPercentageTextbox: Locator;
    readonly portfolioValueText: Locator;
    readonly financialAdvisorText: Locator;
    readonly platformText: Locator;
    readonly totalText: Locator;
    readonly continueButton: Locator;
    readonly fundedAccountsDiv: Locator;
    readonly oneCombinedDocumentText: Locator;

    // Strategy Checkboxes
    readonly assetMarkIncomeBuilderCheckbox: Locator;
    readonly blackRockEquityDividendCheckbox: Locator;
    readonly savosUSRiskCheckbox: Locator;
    readonly alphaSimplexCheckbox: Locator;
    readonly jpMorganAbsoluteReturnCheckbox: Locator;

    // Strategy Display Text
    readonly assetMarkIncomeBuilderText: Locator;
    readonly blackRockEquityDividendText: Locator;
    readonly savosUSRiskText: Locator;
    readonly alphaSimplexText: Locator;
    readonly jpMorganAbsoluteReturnText: Locator;

    // Proposal Document Sections - Checkboxes
    readonly introductionCheckbox: Locator;
    readonly pursuingYourGoalsCheckbox: Locator;
    readonly investingIsPersonalCheckbox: Locator;
    readonly equitiesVsBondsCheckbox: Locator;
    readonly cycleOfEmotionsCheckbox: Locator;
    readonly stayingInvestedCheckbox: Locator;
    readonly yourInvestmentTeamCheckboxTop: Locator;
    readonly yourInvestmentTeamCheckboxInside: Locator;
    readonly portfolioStrategistsCheckbox: Locator;
    readonly custodianSelectionCheckbox: Locator;
    readonly ongoingReviewCheckbox: Locator;
    readonly recommendedInvestmentPortfolioCheckbox: Locator;
    readonly allocationByAssetClassCheckbox: Locator;
    readonly topHoldingsCheckbox: Locator;
    readonly proposedAccountsEstimatedYieldCheckbox: Locator;
    readonly hypotheticalHistoricalPerformanceCheckbox: Locator;
    readonly hypotheticalSectionCheckbox: Locator;
    readonly ratesCheckbox: Locator;
    readonly calendarYearReturnsCheckbox: Locator;
    readonly historicalCumulativePerformanceCheckbox: Locator;
    readonly riskVersusReturnCheckbox: Locator;
    readonly annualPortfolioFeesCheckbox: Locator;
    readonly tieredFeeScheduleCheckbox: Locator;
    readonly estimateExpenseCheckbox: Locator;
    readonly clientSignatureCheckbox: Locator;
    readonly investmentPolicyStatementCheckbox: Locator;

    // Proposal Document Sections - Dropdown Icons
    readonly pursuingYourGoalsDropdownIcon: Locator;
    readonly recommendedInvestmentPortfolioDropdownIcon: Locator;
    readonly hypotheticalHistoricalPerformanceDropdownIcon: Locator;
    readonly annualPortfolioFeesDropdownIcon: Locator;

    // Proposal Document Verification - Click Elements
    readonly coverPageHeader: Locator;
    readonly pursueYourGoalsText: Locator;
    readonly tableOfContentsText: Locator;
    readonly introductionHeader: Locator;
    readonly investingIsPersonalText: Locator;
    readonly equitiesVsBondsTitle: Locator;
    readonly cycleOfEmotionsHeader: Locator;
    readonly stayingInvestedTitle: Locator;
    readonly yourInvestmentTeamDiv: Locator;
    readonly portfolioStrategistsSection: Locator;
    readonly custodianSelectionHeader: Locator;
    readonly ongoingReviewText: Locator;
    readonly yourFinancialAnalysisHeader: Locator;
    readonly recommendedPortfolioDiv: Locator;
    readonly allocationByAssetClassHeader: Locator;
    readonly topHoldingsText: Locator;
    readonly proposedAccountsTitle: Locator;
    readonly hypotheticalHistoricalPerformanceDiv: Locator;
    readonly hypotheticalSectionTitle: Locator;
    readonly ratesHeader: Locator;
    readonly calendarYearReturnsText: Locator;
    readonly historicalCumulativeText: Locator;
    readonly riskVersusReturnSection: Locator;
    readonly feeScheduleDiv: Locator;
    readonly tieredFeeScheduleHeader: Locator;
    readonly estimateExpenseTitle: Locator;
    readonly importantInformationText: Locator;
    readonly disclosuresTitle: Locator;
    readonly clientSignatureText: Locator;
    readonly investmentPolicyStatementText: Locator;

    // Proposal Document Verification - Content Visibility
    readonly previewLayoutContentFirst: Locator;
    readonly tableOfContentsContent: Locator;
    readonly introductionContent: Locator;
    readonly investingContent: Locator;
    readonly growthContentFirst: Locator;
    readonly theContent: Locator;
    readonly growthContentSecond: Locator;
    readonly yourContentCanvas: Locator;
    readonly portfolioContent: Locator;
    readonly custodianContent: Locator;
    readonly ongoingContent: Locator;
    readonly yourFinancialContent: Locator;
    readonly recommendedContent: Locator;
    readonly allocationContent: Locator;
    readonly topHoldingsContent: Locator;
    readonly proposedContentFirst: Locator;
    readonly hypotheticalContent: Locator;
    readonly ratesContent: Locator;
    readonly calendarContent: Locator;
    readonly historicalContent: Locator;
    readonly riskContent: Locator;
    readonly feeContentFirst: Locator;
    readonly tieredContent: Locator;
    readonly estimatedExpenseCanvas: Locator;
    readonly importantInformationCanvas: Locator;
    readonly disclosuresCanvas: Locator;
    readonly clientSignatureCanvas: Locator;
    readonly investmentPolicyCanvas: Locator;

    // Client Search Elements
    readonly loadingImageModal: Locator;
    readonly clientSearchInput: Locator;
    readonly searchButton: Locator;
    readonly clientCollapsedLink: Locator;
    readonly guyDudeIndividualLink: Locator;
    readonly viewDocumentHistoryLink: Locator;
    readonly portfolioDetailsLink: Locator;

    constructor(page: Page) {
        this.page = page;

        // Navigation Links (Main Page)
        this.investmentsLink = page.getByRole('link', { name: 'Investments' });
        this.portfolioEngineLink = page.getByRole('link', { name: 'PortfolioEngine', exact: true });
        this.launchPortfolioEngineImg = page.getByRole('img', { name: 'Launch Portfolio Engine' }).first();
        this.clientsLink = page.getByRole('link', { name: 'Clients' });
        this.getStartedButton = page.getByRole('button', { name: 'Get Started...' });

        // Widget Headers
        this.upsideDownsideCaptureHeader = page.locator('header').filter({ hasText: 'Upside/Downside Capture' });
        this.investmentApproachHeader = page.locator('header').filter({ hasText: 'Investment Approach' });
        this.returnByStrategyHeader = page.locator('header').filter({ hasText: 'Return by Strategy' });
        this.stressTestHeader = page.locator('header').filter({ hasText: 'Stress Test' });
        this.assetAllocationHoldingsHeader = page.locator('header').filter({ hasText: 'Asset Allocation & Holdings' });
        this.riskVsReturnHeader = page.locator('header').filter({ hasText: 'Risk vs Return' });
        this.summaryStatisticsHeader = page.locator('header').filter({ hasText: 'Summary Statistics' });
        this.drawdownHeader = page.locator('header').filter({ hasText: 'Drawdown' });
        this.performanceHeader = page.locator('header').filter({ hasText: 'Performance' });

        // Widget Selection Checkboxes
        this.widgetSelectionDropdownButton = page.getByRole('button').nth(2);
        this.widgetCheckbox1 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(1) > div > span');
        this.widgetCheckbox2 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(2) > div > span');
        this.widgetCheckbox3 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(3) > div > span');
        this.widgetCheckbox4 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(4) > div > span');
        this.widgetCheckbox5 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(5) > div > span');
        this.widgetCheckbox6 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(6) > div > span');
        this.widgetCheckbox7 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(7) > div > span');
        this.widgetCheckbox8 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(8) > div > span');
        this.widgetCheckbox9 = page.locator('#root > div:nth-child(5) > div > div > ul > li:nth-child(9) > div > span');

        // Widget Graph Containers
        this.graphContainer1 = page.locator('div.react-grid-layout > div').nth(0);
        this.graphContainer2 = page.locator('div.react-grid-layout > div').nth(1);
        this.graphContainer3 = page.locator('div.react-grid-layout > div').nth(2);
        this.graphContainer4 = page.locator('div.react-grid-layout > div').nth(3);
        this.graphContainer5 = page.locator('div.react-grid-layout > div').nth(4);
        this.graphContainer6 = page.locator('div.react-grid-layout > div').nth(5);
        this.graphContainer7 = page.locator('div.react-grid-layout > div').nth(6);
        this.graphContainer8 = page.locator('div.react-grid-layout > div').nth(7);
        this.graphContainer9 = page.locator('div.react-grid-layout > div').nth(8);

        // Portfolio Management Buttons
        this.managePortfoliosButton = page.getByRole('button', { name: 'Manage Portfolios' });
        this.createNewModelPortfolioButton = page.getByRole('button', { name: 'Create New Model Portfolio' });
        this.strategySaveButton = page.getByRole('button', { name: 'Save' });
        this.createProposalButton = page.getByRole('button', { name: 'Create Proposal' });

        // Portfolio Management - Delete Elements
        this.portfolioDeleteControlButton = page.locator('tr:nth-child(2) > .table-component__cell__2rhe1.table-child__cell__3SV_1.table-child__cell_controls__2U_PE > div');
        this.portfolioDeleteText = page.getByText('Delete');
        this.portfolioDeleteConfirmButton = page.getByRole('button', { name: 'Delete' });
        this.previewProposalButton = page.getByRole('button', { name: 'Preview Proposal' });
        this.saveProposalButton = page.getByRole('button', { name: 'save proposal' });
        this.viewDocumentsButton = page.getByRole('button', { name: 'View Documents' });

        // Portfolio Creation Elements
        this.assetMarkPlatformStrategiesText = page.getByText('AssetMark Platform Strategies', { exact: true });
        this.strategySearchBox = page.getByRole('textbox', { name: 'Search' });
        this.addToPortfolioText = page.getByText('Add to Portfolio');
        this.modelPortfolioNameTextbox = page.getByRole('textbox', { name: 'Model Portfolio Name' });
        this.investmentAllocationText = page.getByText('Investment Allocation100 %Add');

        // Proposal Creation - Client Type
        this.newClientRadio = page.getByRole('radio', { name: 'New Client' });
        this.newClientText = page.getByText('New Client');
        this.existingClientRadio = page.getByRole('radio', { name: 'Existing Client' });
        this.existingClientText = page.getByText('Existing Client');
        this.discretionaryRadio = page.getByRole('radio', { name: 'Discretionary', exact: true });
        this.discretionaryText = page.getByText('Discretionary', { exact: true });
        this.nonDiscretionaryRadio = page.getByRole('radio', { name: 'Non-Discretionary' });
        this.nonDiscretionaryText = page.getByText('Non-Discretionary');
        this.firstNameTextbox = page.getByRole('textbox', { name: 'First' });
        this.lastNameTextbox = page.getByRole('textbox', { name: 'Last' });
        this.nextButton = page.getByRole('button', { name: 'NEXT' });

        // Proposal Creation - Risk Profile
        this.moderateRiskRadio = page.getByRole('radio', { name: 'Moderate', exact: true });
        this.timeHorizonNineYearsRadio = page.getByRole('radio', { name: '- 9 years' });
        this.declineFiftyPercentRadio = page.getByRole('radio', { name: '- 50%' });
        this.riskToleranceModerateRadio = page.getByRole('radio', { name: '3 - Moderate' });

        // Proposal Creation - Account Setup
        this.selectCustodianDropdown = page.getByRole('img', { name: 'ArrowDown' }).first();
        this.fidelityText = page.getByRole('listitem').filter({ hasText: 'Fidelity' });
        this.assetMarkText = page.getByRole('listitem').filter({ hasText: 'AssetMark Trust' });
        this.schwabText = page.getByRole('listitem').filter({ hasText: 'Schwab' });
        this.pershingAdvisorSolutionsText = page.getByRole('listitem').filter({ hasText: 'Pershing Advisor Solutions' });
        this.addRegistrationButton = page.getByRole('img', { name: 'imgEnable' });
        this.registrationNameTextbox = page.getByRole('textbox');
        this.registrationTypeDropdown = page.getByRole('img', { name: 'ArrowDown' }).nth(1)
        this.individualCategory = page.getByRole('paragraph').filter({ hasText: 'Individual' });
        this.individualOption = page.getByRole('listitem').filter({ hasText: /^Individual$/ });
        this.addAccountButton = page.getByRole('img', { name: 'img' });
        this.modelListConfirmEnable = page.locator('#modelListConfirmEnable');
        this.investmentAmountInput = page.locator('input[name="investmentAmount"]');
        this.enrollInTaxRadio = page.getByRole('radio', { name: 'Enroll in Tax Management Services', exact: true });
        this.doNotEnrollInTaxRadio = page.getByRole('radio', { name: 'Do not enroll in Tax' });
        this.confirmText = page.getByText('CONFIRM', { exact: true });

        // Proposal Creation - Verification Elements
        this.proposedAccountsText = page.getByText('Proposed Accounts (1)$');
        this.accountHolderNameParagraph = page.getByRole('paragraph').filter({ hasText: 'Guy Dude, Individual' });
        this.multipleStrategyAccountParagraph = page.getByRole('paragraph').filter({ hasText: 'Multiple Strategy Account, Profile ' });
        this.enterPercentageTextbox = page.getByRole('textbox', { name: 'Enter %' });
        this.portfolioValueText = page.getByText('Portfolio Value$');
        this.financialAdvisorText = page.getByText('Financial Advisor1');
        this.platformText = page.getByText('Platform0');
        this.totalText = page.getByText('Total1');
        this.continueButton = page.getByRole('button', { name: 'Continue' });
        this.fundedAccountsDiv = page.locator('div').filter({ hasText: /^Funded Accounts\(0\) \$0$/ }).first();
        this.oneCombinedDocumentText = page.getByText('One Combined Document');

        // Strategy Checkboxes
        this.assetMarkIncomeBuilderCheckbox = page.getByRole("checkbox", { name: 'AssetMark Income Builder, Profile 2, Conservative' });
        this.blackRockEquityDividendCheckbox = page.getByRole("checkbox", { name: 'BlackRock Equity Dividend' });
        this.savosUSRiskCheckbox = page.getByRole("checkbox", { name: 'Savos US Risk Controlled Strategy, Profile 6' });
        this.alphaSimplexCheckbox = page.getByRole("checkbox", { name: 'AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth' });
        this.jpMorganAbsoluteReturnCheckbox = page.getByRole("checkbox", { name: 'JPMorgan Absolute Return - Profile 1' });

        // Strategy Display Text
        this.assetMarkIncomeBuilderText = page.getByText('AssetMark Income Builder, Profile 2, Conservative20%');
        this.blackRockEquityDividendText = page.getByText('BlackRock Equity Dividend20%');
        this.savosUSRiskText = page.getByText('Savos US Risk Controlled Strategy, Profile 620%');
        this.alphaSimplexText = page.getByText('AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth20%');
        this.jpMorganAbsoluteReturnText = page.getByText('JPMorgan Absolute Return - Profile 120%');

        // Proposal Document Sections - Checkboxes
        this.introductionCheckbox = page.locator('.th-wrap.th-Introduction-wrap > .th-header > .th-title > .checkbox-container > .clsA');
        this.pursuingYourGoalsCheckbox = page.locator('.th-wrap.th-Investing > .th-header > .th-title > .checkbox-container > .clsA');
        this.investingIsPersonalCheckbox = page.locator('.th-title.th-listview-title.listview-child > .checkbox-container > .clsA').first();
        this.equitiesVsBondsCheckbox = page.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').first();
        this.cycleOfEmotionsCheckbox = page.locator('.th-wrap.th-The > .th-header > .th-title > .checkbox-container > .clsA');
        this.stayingInvestedCheckbox = page.locator('.th-wrap.th-Growth > .th-header > .th-title > .checkbox-container > .clsA').nth(1);
        this.yourInvestmentTeamCheckboxTop = page.locator('.th-wrap.th-Your > div > .th-title > .checkbox-container > .clsA').first();
        this.yourInvestmentTeamCheckboxInside = page.locator('.th-wrap.th-Your > div > .th-title > .checkbox-container > .clsA').nth(1);
        this.portfolioStrategistsCheckbox = page.locator('.th-wrap.th-Portfolio > .th-header > .th-title > .checkbox-container > .clsA');
        this.custodianSelectionCheckbox = page.locator('.th-wrap.th-Custodian > .th-header > .th-title > .checkbox-container > .clsA');
        this.ongoingReviewCheckbox = page.locator('.th-wrap.th-Ongoing > .th-header > .th-title > .checkbox-container > .clsA');
        this.recommendedInvestmentPortfolioCheckbox = page.locator('.th-wrap.th-Recommended > div > .th-title > .checkbox-container > .clsA').first();
        this.allocationByAssetClassCheckbox = page.locator('.th-wrap.th-Allocation > .th-header > .th-title > .checkbox-container > .clsA');
        this.topHoldingsCheckbox = page.locator('.th-wrap.th-Top > .th-header > .th-title > .checkbox-container > .clsA');
        this.proposedAccountsEstimatedYieldCheckbox = page.locator('.th-wrap.th-Proposed > .th-header > .th-title > .checkbox-container > .clsA');
        this.hypotheticalHistoricalPerformanceCheckbox = page.locator('.th-wrap.th-Hypothetical > div > .th-title > .checkbox-container > .clsA').first();
        this.hypotheticalSectionCheckbox = page.locator('.th-wrap.th-Hypothetical > div:nth-child(2) > .th-title > .checkbox-container > .clsA');
        this.ratesCheckbox = page.locator('.th-wrap.th-Rates > .th-header > .th-title > .checkbox-container > .clsA');
        this.calendarYearReturnsCheckbox = page.locator('.th-wrap.th-Calendar > .th-header > .th-title > .checkbox-container > .clsA');
        this.historicalCumulativePerformanceCheckbox = page.locator('.th-wrap.th-Historical > .th-header > .th-title > .checkbox-container > .clsA');
        this.riskVersusReturnCheckbox = page.locator('.th-wrap.th-Risk > .th-header > .th-title > .checkbox-container > .clsA');
        this.annualPortfolioFeesCheckbox = page.locator('.th-wrap.th-Fee > div > .th-title > .checkbox-container > .clsA').first();
        this.tieredFeeScheduleCheckbox = page.locator('.th-wrap.th-Tiered > .th-header > .th-title > .checkbox-container > .clsA');
        this.estimateExpenseCheckbox = page.locator('.th-wrap.th-Estimated > .th-header > .th-title > .checkbox-container > .clsA');
        this.clientSignatureCheckbox = page.locator('.th-wrap.th-Client > .th-header > .th-title > .checkbox-container > .clsA');
        this.investmentPolicyStatementCheckbox = page.locator('.th-wrap.th-Investment > .th-header > .th-title > .checkbox-container');

        // Proposal Document Sections - Dropdown Icons
        this.pursuingYourGoalsDropdownIcon = page.locator('.th-wrap.th-Investing > .th-header > .th-title > span > .icon-holder > .glyphicon');
        this.recommendedInvestmentPortfolioDropdownIcon = page.locator('span').filter({ hasText: 'Recommended Investment Portfolio (4)' }).locator('i');
        this.hypotheticalHistoricalPerformanceDropdownIcon = page.locator('.th-wrap.th-Hypothetical > div > .th-title > span > .icon-holder > .glyphicon');
        this.annualPortfolioFeesDropdownIcon = page.locator('.th-wrap.th-Fee > div > .th-title > span > .icon-holder > .glyphicon');

        // Proposal Document Verification - Click Elements
        this.coverPageHeader = page.locator('.th-header').first();
        this.pursueYourGoalsText = page.getByText('Pursue Your Goals', { exact: true });
        this.tableOfContentsText = page.getByText('Table Of Contents', { exact: true });
        this.introductionHeader = page.locator('.th-wrap.th-Introduction-wrap > .th-header');
        this.investingIsPersonalText = page.getByText('Investing is Personal', { exact: true });
        this.equitiesVsBondsTitle = page.locator('.th-wrap.th-Growth > .th-header > .th-title').first();
        this.cycleOfEmotionsHeader = page.locator('.th-wrap.th-The > .th-header');
        this.stayingInvestedTitle = page.locator('.th-wrap.th-Growth > .th-header > .th-title').nth(1);
        this.yourInvestmentTeamDiv = page.locator('.th-wrap.th-Your > div:nth-child(2)');
        this.portfolioStrategistsSection = page.locator('.th-wrap.th-Portfolio');
        this.custodianSelectionHeader = page.locator('.th-wrap.th-Custodian > .th-header');
        this.ongoingReviewText = page.getByText('Ongoing Review of Your Portfolio', { exact: true });
        this.yourFinancialAnalysisHeader = page.locator('.th-wrap.th-Your.Financial > .th-header');
        this.recommendedPortfolioDiv = page.locator('.th-wrap.th-Recommended > div:nth-child(2)');
        this.allocationByAssetClassHeader = page.locator('.th-wrap.th-Allocation > .th-header');
        this.topHoldingsText = page.getByText('Top Holdings').first();
        this.proposedAccountsTitle = page.locator('.th-wrap.th-Proposed > .th-header > .th-title');
        this.hypotheticalHistoricalPerformanceDiv = page.locator('div').filter({ hasText: /^Hypothetical Historical Performance \(5\)$/ }).nth(1);
        this.hypotheticalSectionTitle = page.locator('.th-wrap.th-Hypothetical > div:nth-child(2) > .th-title');
        this.ratesHeader = page.locator('.th-wrap.th-Rates > .th-header');
        this.calendarYearReturnsText = page.locator('.th-wrap.th-Calendar > .th-header');
        this.historicalCumulativeText = page.getByText('Historical Cumulative').first();
        this.riskVersusReturnSection = page.locator('.th-wrap.th-Risk');
        this.feeScheduleDiv = page.locator('.th-wrap.th-Fee > div:nth-child(2)');
        this.tieredFeeScheduleHeader = page.locator('.th-wrap.th-Tiered > .th-header');
        this.estimateExpenseTitle = page.locator('.th-wrap.th-Estimated > .th-header > .th-title');
        this.importantInformationText = page.getByText('Important Information and Standardized Performance Returns', { exact: true });
        this.disclosuresTitle = page.locator('.th-wrap.th-Disclosures > .th-header > .th-title');
        this.clientSignatureText = page.getByText('Client Signature', { exact: true });
        this.investmentPolicyStatementText = page.getByText('Investment Policy Statement', { exact: true });

        // Proposal Document Verification - Content Visibility
        this.previewLayoutContentFirst = page.locator('.preview-layout-content').first();
        this.tableOfContentsContent = page.locator('.page-wrap.Table > .page-component > .preview-layout-component > .preview-layout-content');
        this.introductionContent = page.locator('.page-wrap.Introduction-page-component-wrap > .page-component > .preview-layout-component > .preview-layout-content');
        this.investingContent = page.locator('.page-wrap.Investing > .page-component > .preview-layout-component > .preview-layout-content');
        this.growthContentFirst = page.locator('.page-wrap.Growth > .page-component > .preview-layout-component > .preview-layout-content').first();
        this.theContent = page.locator('.page-wrap.The > .page-component > .preview-layout-component > .preview-layout-content');
        this.growthContentSecond = page.locator('.page-wrap.Growth > .page-component > .preview-layout-component > .preview-layout-content').nth(1);
        this.yourContentCanvas = page.locator('.page-wrap.Your > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas').first();
        this.portfolioContent = page.locator('.page-wrap.Portfolio > .page-component > .preview-layout-component > .preview-layout-content');
        this.custodianContent = page.locator('.page-wrap.Custodian > .page-component > .preview-layout-component > .preview-layout-content');
        this.ongoingContent = page.locator('.page-wrap.Ongoing > .page-component > .preview-layout-component > .preview-layout-content');
        this.yourFinancialContent = page.locator('.page-wrap.Your.Financial > .page-component > .preview-layout-component > .preview-layout-content');
        this.recommendedContent = page.locator('.page-wrap.Recommended > .page-component > .preview-layout-component > .preview-layout-content');
        this.allocationContent = page.locator('.page-wrap.Allocation > .page-component > .preview-layout-component > .preview-layout-content');
        this.topHoldingsContent = page.locator('.page-wrap.Top > .page-component > .preview-layout-component > .preview-layout-content');
        this.proposedContentFirst = page.locator('.page-wrap.Proposed > .page-component > .preview-layout-component > .preview-layout-content').first();
        this.hypotheticalContent = page.locator('.page-wrap.Hypothetical > .page-component > .preview-layout-component > .preview-layout-content');
        this.ratesContent = page.locator('.page-wrap.Rates > .page-component > .preview-layout-component > .preview-layout-content');
        this.calendarContent = page.locator('.page-wrap.Calendar > .page-component > .preview-layout-component > .preview-layout-content');
        this.historicalContent = page.locator('.page-wrap.Historical > .page-component > .preview-layout-component > .preview-layout-content');
        this.riskContent = page.locator('.page-wrap.Risk > .page-component > .preview-layout-component > .preview-layout-content');
        this.feeContentFirst = page.locator('.page-wrap.Fee > .page-component > .preview-layout-component > .preview-layout-content').first();
        this.tieredContent = page.locator('.page-wrap.Tiered > .page-component > .preview-layout-component > .preview-layout-content');
        this.estimatedExpenseCanvas = page.locator('.page-wrap.Estimated.Expense > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas');
        this.importantInformationCanvas = page.locator('.page-wrap.Important.Information > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas');
        this.disclosuresCanvas = page.locator('.page-wrap.Disclosures > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas');
        this.clientSignatureCanvas = page.locator('.page-wrap.Client > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas');
        this.investmentPolicyCanvas = page.locator('.page-wrap.Investment.Policy > .page-component > .preview-layout-component > .preview-layout-content > div > .react-pdf__Document > .react-pdf__Page > .react-pdf__Page__canvas');

        // Client Search Elements
        this.loadingImageModal = page.locator('#loadingImageModal');
        this.clientSearchInput = page.locator('#client_search_input');
        this.searchButton = page.locator('#searchbutton');
        this.clientCollapsedLink = page.locator('.ui-sgcollapsed > a').first();
        this.guyDudeIndividualLink = page.getByRole('link', { name: 'Guy Dude, Individual' });
        this.viewDocumentHistoryLink = page.getByRole('link', { name: 'View Document History' });
        this.portfolioDetailsLink = page.getByRole('link', { name: 'Portfolio Details' });
    }

    // Helper Methods

    /**
     * Add a strategy to portfolio by searching and clicking "Add to Portfolio"
     * @param strategyName - Name of the strategy to search for
     */
    async addStrategyToPortfolio(strategyName: string): Promise<void> {
        await this.strategySearchBox.fill(strategyName);
        await this.addToPortfolioText.click();
    }

    /**
     * Get allocation textbox by index
     * @param index - Index of the textbox (0-based)
     */
    getAllocationTextbox(index: number): Locator {
        return this.page.getByRole('textbox').nth(index);
    }

    /**
     * Fill client information for new client
     * @param firstName - Client's first name
     * @param lastName - Client's last name
     */
    async fillNewClientInfo(firstName: string, lastName: string): Promise<void> {
        await this.firstNameTextbox.fill(firstName);
        await this.lastNameTextbox.fill(lastName);
    }

    /**
     * Select risk profile options
     */
    async selectRiskProfile(): Promise<void> {
        await this.moderateRiskRadio.check();
        await this.timeHorizonNineYearsRadio.check();
        await this.declineFiftyPercentRadio.check();
        await this.riskToleranceModerateRadio.check();
    }

    /**
     * Select all strategy checkboxes
     */
    async selectAllStrategies(): Promise<void> {
        await this.assetMarkIncomeBuilderCheckbox.click();
        await this.blackRockEquityDividendCheckbox.click();
        await this.savosUSRiskCheckbox.click();
        await this.alphaSimplexCheckbox.click();
        await this.jpMorganAbsoluteReturnCheckbox.click();
    }

    /**
     * Set all proposal document section checkboxes
     */
    async setAllProposalSections(): Promise<void> {
        await this.introductionCheckbox.setChecked(true);
        await this.pursuingYourGoalsCheckbox.setChecked(true);
        await this.pursuingYourGoalsDropdownIcon.click();
        await this.investingIsPersonalCheckbox.setChecked(true);
        await this.equitiesVsBondsCheckbox.setChecked(true);
        await this.cycleOfEmotionsCheckbox.setChecked(true);
        await this.stayingInvestedCheckbox.setChecked(true);
        await this.yourInvestmentTeamCheckboxTop.setChecked(true);
        await this.yourInvestmentTeamCheckboxInside.setChecked(true);
        await this.portfolioStrategistsCheckbox.setChecked(true);
        await this.custodianSelectionCheckbox.setChecked(true);
        await this.ongoingReviewCheckbox.setChecked(true);
        await this.recommendedInvestmentPortfolioCheckbox.setChecked(true);
        await this.recommendedInvestmentPortfolioDropdownIcon.click();
        await this.allocationByAssetClassCheckbox.setChecked(true);
        await this.topHoldingsCheckbox.setChecked(true);
        await this.proposedAccountsEstimatedYieldCheckbox.setChecked(true);
        await this.hypotheticalHistoricalPerformanceCheckbox.setChecked(true);
        await this.hypotheticalHistoricalPerformanceDropdownIcon.click();
        await this.hypotheticalSectionCheckbox.setChecked(true);
        await this.ratesCheckbox.setChecked(true);
        await this.calendarYearReturnsCheckbox.setChecked(true);
        await this.historicalCumulativePerformanceCheckbox.setChecked(true);
        await this.riskVersusReturnCheckbox.setChecked(true);
        await this.annualPortfolioFeesCheckbox.setChecked(true);
        await this.annualPortfolioFeesDropdownIcon.click();
        await this.tieredFeeScheduleCheckbox.setChecked(true);
        await this.estimateExpenseCheckbox.setChecked(true);
        await this.clientSignatureCheckbox.setChecked(true);
        await this.investmentPolicyStatementCheckbox.setChecked(true);
    }

    /**
     * Search for a client by name
     * @param clientName - Full name of the client
     */
    async searchForClient(clientName: string): Promise<void> {
        await this.clientSearchInput.fill(clientName);
        await this.searchButton.click();
    }

    /**
     * Navigate to client's portfolio details
     */
    async navigateToClientPortfolioDetails(): Promise<void> {
        await this.clientCollapsedLink.click();
        await this.guyDudeIndividualLink.click();
        await this.viewDocumentHistoryLink.click();
        await this.portfolioDetailsLink.click();
    }

    /**
     * Select all widgets if they are not already selected
     */
    async selectAllWidgetsIfNeeded(): Promise<void> {
        await this.widgetSelectionDropdownButton.click();
        const widgets = [
            this.widgetCheckbox1,
            this.widgetCheckbox2,
            this.widgetCheckbox3,
            this.widgetCheckbox4,
            this.widgetCheckbox5,
            this.widgetCheckbox6,
            this.widgetCheckbox7,
            this.widgetCheckbox8,
            this.widgetCheckbox9
        ];

        for (const widget of widgets) {
            const isChecked = await widget.evaluate((el) => {
                // Check if the parent li has a class indicating checked state
                const listItem = el.closest('li');
                return listItem?.classList.contains('selected') ||
                    listItem?.classList.contains('checked') ||
                    el.getAttribute('aria-checked') === 'true' ||
                    window.getComputedStyle(el).opacity === '1';
            });

            if (!isChecked) {
                await widget.click();
            }
        }
    }


    /**
     * Verify all 9 widgets contain rendered data
     */
    async verifyAllGraphsHaveData(): Promise<void> {
        const graphLocators = [
            this.graphContainer1,
            this.graphContainer2,
            this.graphContainer3,
            this.graphContainer4,
            this.graphContainer5,
            this.graphContainer6,
            this.graphContainer7,
            this.graphContainer8,
            this.graphContainer9
        ];

        for (let i = 0; i < graphLocators.length; i++) {
            const chartElement = graphLocators[i];

            // Verify the chart has been rendered with data (non-zero dimensions) and assert that container is not empty
            const hasContent = await chartElement.evaluate((el) => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            });

            if (!hasContent) {
                throw new Error(`Graph ${i + 1} does not have rendered content`);
            } else if (hasContent) {
                console.log(`Graph ${i + 1} has rendered content`);
            }
        }
    }
}