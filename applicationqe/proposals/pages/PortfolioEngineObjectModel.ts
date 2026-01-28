import { selectIfVisible } from '../helperfunctions/selectIfVisible';
import { type Locator, type Page } from '@playwright/test';
import { logger } from '../utils/logger';

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
    readonly performanceWidgetCheckbox: Locator;
    readonly drawdownWidgetCheckbox: Locator;
    readonly summaryStatisticsWidgetCheckbox: Locator;
    readonly riskVsReturnWidgetCheckbox: Locator;
    readonly assetAllocationWidgetCheckbox: Locator;
    readonly stressTestWidgetCheckbox: Locator;
    readonly returnByStrategyWidgetCheckbox: Locator;
    readonly investmentApproachWidgetCheckbox: Locator;
    readonly upsideDownsideWidgetCheckbox: Locator;

    // Graph Containers
    readonly performanceGraphContainer: Locator;
    readonly drawdownGraphContainer: Locator;
    readonly summaryStatisticsGraphContainer: Locator;
    readonly riskVsReturnGraphContainer: Locator;
    readonly assetAllocationGraphContainer: Locator;
    readonly stressTestGraphContainer: Locator;
    readonly returnByStrategyGraphContainer: Locator;
    readonly investmentApproachGraphContainer: Locator;
    readonly upsideDownsideGraphContainer: Locator;

    // Widget Content Elements (for validation)
    readonly performanceGraphContent: Locator;
    readonly drawdownGraphContent: Locator;
    readonly summaryStatisticsGraphContent: Locator;
    readonly riskVsReturnGraphContent: Locator;
    readonly assetAllocationGraphContent: Locator;
    readonly stressTestGraphContent: Locator;
    readonly returnByStrategyGraphContent: Locator;
    readonly investmentApproachGraphContent: Locator;
    readonly upsideDownsideGraphContent: Locator;

    // Portfolio Management Buttons
    readonly managePortfoliosButton: Locator;
    readonly createNewModelPortfolioButton: Locator;
    readonly strategySaveButton: Locator;
    readonly portfolioCloseButton: Locator;
    readonly createProposalButton: Locator;

    // Portfolio Management - Delete Elements
    readonly portfolioDeleteControlButton: Locator;
    readonly portfolioDeleteText: Locator;
    readonly portfolioDeleteConfirmButton: Locator;
    readonly previewProposalButton: Locator;
    readonly saveProposalButton: Locator;
    readonly viewDocumentsButton: Locator;
    readonly quitProposalButton: Locator;

    // Portfolio Creation Elements
    readonly assetMarkPlatformStrategiesText: Locator;
    readonly SavosPersonalStrategyText: Locator;
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
    readonly registrationTypeDropdownMenu: Locator;
    readonly individualCategory: Locator;
    readonly trustCategory: Locator;
    readonly jointCategory: Locator;
    readonly irasCategory: Locator;
    readonly retirementPlansCategory: Locator;
    readonly businessAccountsCategory: Locator;
    readonly organizationsCategory: Locator;
    readonly otherCategory: Locator;
    readonly addAccountButton: Locator;
    readonly modelListConfirm: Locator;
    readonly investmentAmountInput: Locator;
    readonly enrollInTaxRadio: Locator;
    readonly doNotEnrollInTaxRadio: Locator;
    readonly confirmText: Locator;

    // Proposal Creation - Verification Elements
    readonly proposedAccountsContainer: Locator;
    readonly proposedAccountsHeader: Locator;
    readonly proposedAccountsAmount: Locator;
    readonly accountHolderName: Locator;
    readonly multipleStrategyAccountName: Locator;
    readonly multipleStrategyAccountAmount: Locator;
    readonly enterFeePercentageTextbox: Locator;
    readonly feeDetailsContainer: Locator;
    readonly portfolioValueLabel: Locator;
    readonly portfolioValueAmount: Locator;
    readonly financialAdvisorFeeLabel: Locator;
    readonly financialAdvisorFee: Locator;
    readonly platformFeeLabel: Locator;
    readonly platformFee: Locator;
    readonly totalFeeLabel: Locator;
    readonly totalFee: Locator;
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
    readonly hypotheticalGrowthOfProposedAccountsCheckbox: Locator;
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
    readonly noClientsFoundMessage: Locator;
    readonly clientCollapsedLink: Locator;
    readonly guyDudeIndividualLink: Locator;
    readonly viewDocumentHistoryLink: Locator;
    readonly deleteClientLink: Locator;
    readonly portfolioDetailsLink: Locator;
    readonly newClientExperienceDecline: Locator;

    constructor(page: Page) {
        this.page = page;

        // Navigation Links (Main Page)
        this.investmentsLink = page.getByRole('link', { name: 'Investments' });
        this.portfolioEngineLink = page.getByRole('link', { name: 'PortfolioEngine', exact: true });
        this.launchPortfolioEngineImg = page.getByRole('img', { name: 'Launch Portfolio Engine' }).first();
        this.clientsLink = page.getByRole('link', { name: 'Clients' });
        this.getStartedButton = page.getByRole('button', { name: 'Get Started...' });

        // Widget Headers
        this.upsideDownsideCaptureHeader = page.getByRole('heading', { name: /Upside.*Downside Capture/i });
        this.investmentApproachHeader = page.getByRole('heading', { name: /Investment Approach/i });
        this.returnByStrategyHeader = page.getByRole('heading', { name: /Return by Strategy/i });
        this.stressTestHeader = page.getByRole('heading', { name: /Stress Test/i });
        this.assetAllocationHoldingsHeader = page.getByRole('heading', { name: /Asset Allocation.*Holdings/i });
        this.riskVsReturnHeader = page.getByRole('heading', { name: /Risk vs Return/i });
        this.summaryStatisticsHeader = page.getByRole('heading', { name: /Summary Statistics/i });
        this.drawdownHeader = page.getByRole('heading', { name: /Drawdown/i });
        this.performanceHeader = page.getByRole('heading', { name: /Performance/i });

        // Widget Selection Checkboxes
        this.widgetSelectionDropdownButton = page
            .locator('header')
            .getByRole('button')
            .filter({ has: page.locator('svg path[d*="M10 13.5a3.5"]') });
        this.performanceWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Performance' })
            .locator('span')
            .first();
        this.drawdownWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Drawdown' })
            .locator('span')
            .first();
        this.summaryStatisticsWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Summary Statistics' })
            .locator('span')
            .first();
        this.riskVsReturnWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Risk vs Return' })
            .locator('span')
            .first();
        this.assetAllocationWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Asset Allocation & Holdings' })
            .locator('span')
            .first();
        this.stressTestWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Stress Test' })
            .locator('span')
            .first();
        this.returnByStrategyWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Return by Strategy' })
            .locator('span')
            .first();
        this.investmentApproachWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Investment Approach' })
            .locator('span')
            .first();
        this.upsideDownsideWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: 'Upside/Downside Capture' })
            .locator('span')
            .first();

        // Widget graph containers - has header and content
        this.performanceGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Performance' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.drawdownGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Drawdown' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.summaryStatisticsGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Summary Statistics' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.riskVsReturnGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Risk vs Return' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.assetAllocationGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Asset Allocation & Holdings' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.stressTestGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Stress Test' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.returnByStrategyGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Return by Strategy' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.investmentApproachGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Investment Approach' })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.upsideDownsideGraphContainer = page
            .locator('article')
            .filter({ hasText: 'Upside/Downside Capture' })
            .first()
            .locator('div[class*="widget-component__content"]');

        // Widget Content Elements - specific chart/graph elements for validation
        this.performanceGraphContent = this.performanceGraphContainer.locator('svg text');
        this.drawdownGraphContent = this.drawdownGraphContainer.locator('tbody tr');
        this.summaryStatisticsGraphContent = this.summaryStatisticsGraphContainer.locator('tbody tr');
        this.riskVsReturnGraphContent = this.riskVsReturnGraphContainer.locator('svg circle');
        this.assetAllocationGraphContent = this.assetAllocationGraphContainer.locator(
            'svg path[class*="recharts-sector"]'
        );
        this.stressTestGraphContent = this.stressTestGraphContainer.locator('div[class*="tick"]');
        this.returnByStrategyGraphContent = this.returnByStrategyGraphContainer.locator('svg rect');
        this.investmentApproachGraphContent = this.investmentApproachGraphContainer.locator(
            'svg path[class*="recharts-sector"]'
        );
        this.upsideDownsideGraphContent = this.upsideDownsideGraphContainer.locator('svg rect');

        // Portfolio Management Buttons
        this.managePortfoliosButton = page.getByRole('button', { name: 'Manage Portfolios' });
        this.createNewModelPortfolioButton = page.getByRole('button', { name: 'Create New Model Portfolio' });
        this.strategySaveButton = page
            .locator('[class*="popup-component__footer"], [class*="management-footer"]')
            .getByRole('button', { name: 'Save' });
        this.portfolioCloseButton = page
            .locator('[class*="popup-component__footer"], [class*="management-footer"]')
            .getByRole('button', { name: 'Close' });
        this.createProposalButton = page.getByRole('button', { name: 'Create Proposal' });

        // Portfolio Management - Delete Elements
        this.portfolioDeleteControlButton = page
            .locator('[class*="popup-component"]')
            .locator('button[class*="button-icon"]')
            .filter({ has: page.locator('svg[viewBox="0 0 17 17"]') })
            .first();
        this.portfolioDeleteText = page
            .locator('[class*="popover-controls-component__action"]')
            .getByText('Delete', { exact: true });
        this.portfolioDeleteConfirmButton = page.getByRole('button', { name: 'Delete' });
        this.previewProposalButton = page.getByRole('button', { name: 'Preview Proposal' });
        this.saveProposalButton = page.getByRole('button', { name: 'save proposal' });
        this.viewDocumentsButton = page.getByRole('button', { name: 'View Documents' });
        this.quitProposalButton = page.locator('img[src*="x-icon"]').first();

        // Portfolio Creation Elements
        this.assetMarkPlatformStrategiesText = page.getByText('AssetMark Platform Strategies', { exact: true });
        this.SavosPersonalStrategyText = page.getByText('Savos Personal Portfolio Custom', { exact: true });
        this.strategySearchBox = page.getByRole('textbox', { name: 'Search' });
        this.addToPortfolioText = page.getByText('Add to Portfolio');
        this.modelPortfolioNameTextbox = page.getByRole('textbox', { name: 'Model Portfolio Name' });
        this.investmentAllocationText = page
            .locator('[class*="sidebar-portfolio-component"]')
            .locator('[class*="sectionTwo"]');

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
        this.timeHorizonNineYearsRadio = page.getByRole('radio', { name: '6 - 9 years' });
        this.declineFiftyPercentRadio = page.getByRole('radio', { name: '25 - 50%' });
        this.riskToleranceModerateRadio = page.getByRole('radio', { name: '3 - Moderate' });

        // Proposal Creation - Account Setup
        this.selectCustodianDropdown = page
            .locator('[class*="custodian"], [class*="dropdown"]')
            .getByRole('img', { name: 'ArrowDown' })
            .first();
        this.fidelityText = page.getByRole('listitem').filter({ hasText: /^Fidelity$/ });
        this.assetMarkText = page.getByRole('listitem').filter({ hasText: /^AssetMark Trust$/ });
        this.schwabText = page.getByRole('listitem').filter({ hasText: /^Schwab$/ });
        this.pershingAdvisorSolutionsText = page
            .getByRole('listitem')
            .filter({ hasText: /^Pershing Advisor Solutions$/ });
        this.addRegistrationButton = page.locator('img[class*="accounts_icon"]').first();
        this.registrationNameTextbox = page.getByRole('textbox');
        this.registrationTypeDropdown = page
            .locator('[class*="accounts_regType"]')
            .locator('[class*="accounts-select-dropdown_secondSelectCss"]');
        this.individualCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Individual' })
            .locator('p')
            .first();
        this.trustCategory = page
            .locator('[class*="accounts-select-dropdown_parentList"]')
            .filter({ hasText: 'Trust' })
            .locator('p');
        this.jointCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Joint' })
            .locator('p')
            .first();
        this.irasCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "IRA's" })
            .locator('p')
            .first();
        this.retirementPlansCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Retirement Plans' })
            .locator('p')
            .first();
        this.businessAccountsCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Business Accounts' })
            .locator('p')
            .first();
        this.organizationsCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Organizations' })
            .locator('p')
            .first();
        this.otherCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: 'Other' })
            .locator('p')
            .first();
        this.addAccountButton = page.locator('img[class*="addAccIcon"]');
        this.modelListConfirm = page
            .locator('[class*="accounts-popUp"]')
            .getByRole('button', { name: 'CONFIRM', exact: true });
        this.investmentAmountInput = page.locator('input[name="investmentAmount"]');
        this.enrollInTaxRadio = page.getByRole('radio', { name: 'Enroll in Tax Management Services', exact: true });
        this.doNotEnrollInTaxRadio = page.getByRole('radio', { name: 'Do not enroll in Tax' });
        this.confirmText = page.getByText('CONFIRM', { exact: true });

        // Proposal Creation - Verification Elements
        this.proposedAccountsContainer = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleCta"]');
        this.proposedAccountsHeader = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleHeader"]');
        this.proposedAccountsAmount = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleAmount"]');
        this.accountHolderName = page.locator('[class*="proposedAccounts-sidebar-toggle_regName"]');
        this.multipleStrategyAccountName = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleDataName"]');
        this.multipleStrategyAccountAmount = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleDataValue"]');
        this.enterFeePercentageTextbox = page.getByRole('textbox', { name: 'Enter %' });
        this.feeDetailsContainer = page.locator('[class*="fees_feeDetails"]');
        this.portfolioValueLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Portfolio Value' })
            .locator('div')
            .first();
        this.portfolioValueAmount = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Portfolio Value' })
            .locator('div')
            .last();
        this.financialAdvisorFeeLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Financial Advisor' })
            .locator('div')
            .first();
        this.financialAdvisorFee = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Financial Advisor' })
            .locator('div')
            .last();
        this.platformFeeLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Platform' })
            .locator('div')
            .first();
        this.platformFee = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: 'Platform' })
            .locator('div')
            .last();
        this.totalFeeLabel = this.feeDetailsContainer.locator('[class*="fees_totalFee"]').locator('div').first();
        this.totalFee = this.feeDetailsContainer.locator('[class*="fees_totalFee"]').locator('div').last();
        this.continueButton = page.getByRole('button', { name: 'Continue' });
        this.fundedAccountsDiv = page
            .locator('div')
            .filter({ hasText: /^Funded Accounts\(0\) \$0$/ })
            .first();
        this.oneCombinedDocumentText = page.getByText('One Combined Document');

        // Strategy Checkboxes
        this.assetMarkIncomeBuilderCheckbox = page.getByRole('checkbox', {
            name: 'AssetMark Income Builder, Profile 2, Conservative',
        });
        this.blackRockEquityDividendCheckbox = page.getByRole('checkbox', { name: 'BlackRock Equity Dividend' });
        this.savosUSRiskCheckbox = page.getByRole('checkbox', { name: 'Savos US Risk Controlled Strategy, Profile 6' });
        this.alphaSimplexCheckbox = page.getByRole('checkbox', {
            name: 'AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth',
        });
        this.jpMorganAbsoluteReturnCheckbox = page.getByRole('checkbox', {
            name: 'JPMorgan Absolute Return - Profile 1',
        });

        // Strategy Display Text
        this.assetMarkIncomeBuilderText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: 'AssetMark Income Builder, Profile 2, Conservative' });
        this.blackRockEquityDividendText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: 'BlackRock Equity Dividend' });
        this.savosUSRiskText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: 'Savos US Risk Controlled Strategy, Profile 6' });
        this.alphaSimplexText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: 'AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth' });
        this.jpMorganAbsoluteReturnText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: 'JPMorgan Absolute Return - Profile 1' });

        // Proposal Document Sections - Checkboxes
        this.introductionCheckbox = page.locator('.th-Introduction-wrap .checkbox-container .clsA');
        this.pursuingYourGoalsCheckbox = page.locator('.th-wrap.th-Investing .checkbox-container .clsA');
        this.investingIsPersonalCheckbox = page
            .locator('.th-listview-title.listview-child .checkbox-container .clsA')
            .first();
        this.equitiesVsBondsCheckbox = page.locator('.th-wrap.th-Growth .checkbox-container .clsA').first();
        this.cycleOfEmotionsCheckbox = page.locator('.th-wrap.th-The.Cycle .checkbox-container .clsA');
        this.stayingInvestedCheckbox = page.locator('.th-wrap.th-Growth .checkbox-container .clsA').nth(1);
        this.yourInvestmentTeamCheckboxTop = page.locator('.th-wrap.th-Your .checkbox-container .clsA').first();
        this.yourInvestmentTeamCheckboxInside = page.locator('.th-wrap.th-Your .checkbox-container .clsA').nth(1);
        this.portfolioStrategistsCheckbox = page.locator('.th-wrap.th-Portfolio .checkbox-container .clsA');
        this.custodianSelectionCheckbox = page.locator('.th-wrap.th-Custodian .checkbox-container .clsA');
        this.ongoingReviewCheckbox = page.locator('.th-wrap.th-Ongoing .checkbox-container .clsA');
        this.recommendedInvestmentPortfolioCheckbox = page
            .locator('.th-wrap.th-Recommended .checkbox-container .clsA')
            .first();
        this.allocationByAssetClassCheckbox = page.locator('.th-wrap.th-Allocation .checkbox-container .clsA');
        this.topHoldingsCheckbox = page.locator('.th-wrap.th-Top .checkbox-container .clsA');
        this.proposedAccountsEstimatedYieldCheckbox = page.locator('.th-wrap.th-Proposed .checkbox-container .clsA');
        this.hypotheticalHistoricalPerformanceCheckbox = page
            .locator('.th-wrap.th-Hypothetical .checkbox-container .clsA')
            .first();
        this.hypotheticalGrowthOfProposedAccountsCheckbox = page
            .locator('.th-wrap.th-Hypothetical .checkbox-container .clsA')
            .nth(1);
        this.ratesCheckbox = page.locator('.th-wrap.th-Rates .checkbox-container .clsA');
        this.calendarYearReturnsCheckbox = page.locator('.th-wrap.th-Calendar .checkbox-container .clsA');
        this.historicalCumulativePerformanceCheckbox = page.locator('.th-wrap.th-Historical .checkbox-container .clsA');
        this.riskVersusReturnCheckbox = page.locator('.th-wrap.th-Risk .checkbox-container .clsA');
        this.annualPortfolioFeesCheckbox = page.locator('.th-wrap.th-Fee .checkbox-container .clsA').first();
        this.tieredFeeScheduleCheckbox = page.locator('.th-wrap.th-Tiered .checkbox-container .clsA');
        this.estimateExpenseCheckbox = page.locator('.th-wrap.th-Estimated .checkbox-container .clsA');
        this.clientSignatureCheckbox = page.locator('.th-wrap.th-Client .checkbox-container .clsA');
        this.investmentPolicyStatementCheckbox = page.locator('.th-wrap.th-Investment .checkbox-container .clsA');

        // Proposal Document Sections - Dropdown Icons (using stable section-specific patterns)
        this.pursuingYourGoalsDropdownIcon = page.locator('.th-wrap.th-Investing .icon-holder i');
        this.recommendedInvestmentPortfolioDropdownIcon = page
            .locator('.th-wrap.th-Recommended .icon-holder i')
            .first();
        this.hypotheticalHistoricalPerformanceDropdownIcon = page
            .locator('.th-wrap.th-Hypothetical .icon-holder i')
            .first();
        this.annualPortfolioFeesDropdownIcon = page.locator('.th-wrap.th-Fee .icon-holder i').first();

        // Proposal Document Verification - Click Elements (using stable patterns with class combinations)
        this.coverPageHeader = page.locator('.th-header').first();
        this.pursueYourGoalsText = page.getByText('Pursue Your Goals', { exact: true });
        this.tableOfContentsText = page.getByText('Table Of Contents', { exact: true });
        this.introductionHeader = page
            .getByRole('heading', { name: /Introduction/i })
            .or(page.locator('.th-wrap.th-Introduction-wrap .th-header'));
        this.investingIsPersonalText = page.getByText('Investing is Personal', { exact: true });
        this.equitiesVsBondsTitle = page
            .locator('.th-wrap.th-Growth .th-title')
            .filter({ hasText: 'Equities vs. Bonds' });
        this.cycleOfEmotionsHeader = page
            .getByRole('heading', { name: /Cycle of Emotions/i })
            .or(page.locator('.th-wrap.th-The.Cycle .th-header'));
        this.stayingInvestedTitle = page
            .locator('.th-wrap.th-Growth .th-title')
            .filter({ hasText: 'Staying Invested' });
        this.yourInvestmentTeamDiv = page.getByText('Your Investment Team (3)');
        this.portfolioStrategistsSection = page.locator('.th-wrap.th-Portfolio');
        this.custodianSelectionHeader = page
            .getByRole('heading', { name: /Custodian Selection/i })
            .or(page.locator('.th-wrap.th-Custodian .th-header'));
        this.ongoingReviewText = page.getByText('Ongoing Review of Your Portfolio', { exact: true });
        this.yourFinancialAnalysisHeader = page.locator('.th-wrap.th-Your.Financial');
        this.recommendedPortfolioDiv = page
            .locator('.th-title.th-listview-title.listview-child')
            .filter({ hasText: 'Recommended Portfolio' });
        this.allocationByAssetClassHeader = page
            .getByRole('heading', { name: /Allocation by Asset Class/i })
            .or(page.locator('.th-wrap.th-Allocation .th-header'));
        this.topHoldingsText = page.getByText('Top Holdings').first();
        this.proposedAccountsTitle = page.locator('.th-wrap.th-Proposed .th-title');
        this.hypotheticalHistoricalPerformanceDiv = page
            .locator('.th-wrap.th-Hypothetical .th-title')
            .filter({ hasText: 'Hypothetical Historical Performance' })
            .first();
        this.hypotheticalSectionTitle = page
            .locator('.th-wrap.th-Hypothetical .th-title')
            .filter({ hasText: 'Hypothetical Historical Performance' })
            .last();
        this.ratesHeader = page
            .getByRole('heading', { name: /Rates/i })
            .or(page.locator('.th-wrap.th-Rates .th-header'));
        this.calendarYearReturnsText = page.locator('.th-wrap.th-Calendar .th-header');
        this.historicalCumulativeText = page
            .locator('.th-wrap.th-Historical > .th-header > .th-title')
            .filter({ hasText: 'Historical Cumulative' });
        this.riskVersusReturnSection = page.locator('.th-wrap.th-Risk');
        this.feeScheduleDiv = page
            .locator('div')
            .filter({ hasText: /^Annual Portfolio Fees \(3\)$/ })
            .first();
        //getByText('Fee Schedule').nth(1);
        this.tieredFeeScheduleHeader = page
            .getByRole('heading', { name: /Tiered Fee Schedule/i })
            .or(page.locator('.th-wrap.th-Tiered .th-header'));
        this.estimateExpenseTitle = page.locator('.th-wrap.th-Estimated .th-title');
        this.importantInformationText = page.getByText('Important Information and Standardized Performance Returns', {
            exact: true,
        });
        this.disclosuresTitle = page.locator('.th-wrap.th-Disclosures .th-title');
        this.clientSignatureText = page.getByText('Client Signature', { exact: true });
        this.investmentPolicyStatementText = page.getByText('Investment Policy Statement', { exact: true });

        // Proposal Document Verification - Content Visibility (targeting canvas elements directly)
        this.previewLayoutContentFirst = page.locator('canvas').first();
        this.tableOfContentsContent = page.locator('.page-wrap.Table canvas');
        this.introductionContent = page.locator('.page-wrap.Introduction-page-component-wrap canvas');
        this.investingContent = page.locator('.page-wrap.Investing canvas');
        this.growthContentFirst = page.locator('.page-wrap.Growth canvas').first();
        this.theContent = page.locator('.page-wrap.The canvas');
        this.growthContentSecond = page.locator('.page-wrap.Growth canvas').nth(1);
        this.yourContentCanvas = page.locator('.page-wrap.Your canvas').first();
        this.portfolioContent = page.locator('.page-wrap.Portfolio canvas');
        this.custodianContent = page.locator('.page-wrap.Custodian canvas');
        this.ongoingContent = page.locator('.page-wrap.Ongoing canvas');
        this.yourFinancialContent = page.locator('.page-wrap.Your.Financial canvas');
        this.recommendedContent = page.locator('.page-wrap.Recommended canvas');
        this.allocationContent = page.locator('.page-wrap.Allocation canvas');
        this.topHoldingsContent = page.locator('.page-wrap.Top canvas');
        this.proposedContentFirst = page.locator('.page-wrap.Proposed canvas').first();
        this.hypotheticalContent = page.locator('.page-wrap.Hypothetical canvas');
        this.ratesContent = page.locator('.page-wrap.Rates canvas');
        this.calendarContent = page.locator('.page-wrap.Calendar canvas');
        this.historicalContent = page.locator('.page-wrap.Historical canvas');
        this.riskContent = page.locator('.page-wrap.Risk canvas');
        this.feeContentFirst = page.locator('.page-wrap.Fee canvas').first();
        this.tieredContent = page.locator('.page-wrap.Tiered canvas');
        this.estimatedExpenseCanvas = page.locator('.page-wrap.Estimated.Expense canvas');
        this.importantInformationCanvas = page.locator('.page-wrap.Important.Information canvas');
        this.disclosuresCanvas = page.locator('.page-wrap.Disclosures canvas');
        this.clientSignatureCanvas = page.locator('.page-wrap.Client canvas');
        this.investmentPolicyCanvas = page.locator('.page-wrap.Investment.Policy canvas');

        // Client Search Elements
        this.loadingImageModal = page.locator('#loadingImageModal');
        this.clientSearchInput = page
            .getByRole('textbox', { name: 'client_search_input' })
            .or(page.locator('#client_search_input'));
        this.searchButton = page.getByRole('button', { name: 'search' }).or(page.locator('#searchbutton'));
        this.noClientsFoundMessage = page.getByText('No search results were found.');
        //this.clientCollapsedLink = page.locator('#ClientListGrid tbody tr.jqgrow').first().locator('td[aria-describedby="ClientListGrid_subgrid"] a');
        this.clientCollapsedLink = page.locator('td[role="gridcell"][aria-describedby="ClientListGrid_clientName"]');
        this.guyDudeIndividualLink = page.getByRole('link', { name: 'Guy Dude, Individual' });
        this.viewDocumentHistoryLink = page.getByRole('link', { name: 'View Document History' });
        this.portfolioDetailsLink = page.getByRole('link', { name: 'Portfolio Details' });
        this.deleteClientLink = page.getByRole('link', { name: 'Delete Client' });
        this.newClientExperienceDecline = page.getByRole('button', { name: 'No, Thank You' });
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
        return this.page.locator('[class*="portfolio-valid-item"]').locator('input[type="text"]').nth(index);
    }

    /**
     * Create a new portfolio with default strategies if one doesn't already exist
     * @param portfolioName - Name for the portfolio (defaults to 'E2E Test Portfolio')
     */
    async createPortfolioIfNeeded(portfolioName: string = 'Generic Portfolio'): Promise<void> {
        if (await this.getStartedButton.isVisible()) {
            await this.getStartedButton.click();
        } else if (await this.managePortfoliosButton.isVisible()) {
            await this.managePortfoliosButton.click();

            // Check for existing portfolio with today's date and portfolio name
            const existingPortfolio = this.page
                .locator('tr')
                .filter({ hasText: portfolioName })
                .filter({ hasText: this.getTodayDate() })
                .first();

            if (await existingPortfolio.isVisible()) {
                // Portfolio already exists, select it and close
                await existingPortfolio.click();
                await this.portfolioCloseButton.click();
                return;
            }
        }

        // Create new model portfolio
        await this.createNewModelPortfolioButton.click();
        await this.assetMarkPlatformStrategiesText.click();

        // Add strategies to the portfolio
        await this.addStrategyToPortfolio('assetmark income builder, profile 2, conservative');
        await this.addStrategyToPortfolio('blackrock equity dividend');
        await this.addStrategyToPortfolio('savos us risk controlled strategy, profile 6');
        await this.addStrategyToPortfolio('alphasimplex, alternative model portfolio, profile 5, growth');
        await this.addStrategyToPortfolio('jpmorgan absolute return - profile 1');

        await this.modelPortfolioNameTextbox.fill(portfolioName);
        await this.strategySaveButton.click();
        await this.strategySaveButton.waitFor({ state: 'detached' });
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
        await this.hypotheticalGrowthOfProposedAccountsCheckbox.setChecked(true);
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
     * @param index - Index of the client in the search results (default is 0)
     * @returns Number of total items found
     */
    async searchForClient(clientName: string): Promise<void> {
        await this.clientsLink.click();
        await this.page.waitForLoadState();
        await selectIfVisible(this.newClientExperienceDecline);
        await this.clientSearchInput.fill(clientName);
        await this.searchButton.click();
    }

    /**
     * Select a registration type from the dropdown
     * @param registrationType - The specific registration type to select (e.g., 'Individual', 'Traditional IRA', 'Trust')
     */
    async selectRegistrationType(registrationType: string): Promise<void> {
        // Check if it's a top-level simple option (Select, Trust)
        const simpleOption = this.page
            .locator('[class*="accounts-select-dropdown_parentList"]')
            .filter({ hasText: registrationType });
        if ((await simpleOption.count()) > 0) {
            await simpleOption.click();
            return;
        }

        // Map of registration types to their parent categories for nested options
        const categoryMap: { [key: string]: string } = {
            Individual: 'Individual',
            'Individual TOD': 'Individual',
            'Community Property': 'Joint',
            'Community Property with Rights of Survivorship': 'Joint',
            'Community Property with Rights of Survivorship TOD': 'Joint',
            'Joint Tenant with Rights of Survivorship': 'Joint',
            'Joint Tenant with Rights of Survivorship TOD': 'Joint',
            'Tenants in Common': 'Joint',
            'Tenants by Entirety': 'Joint',
            'Tenants by Entirety TOD': 'Joint',
            'Traditional IRA': "IRA's",
            'Rollover IRA': "IRA's",
            'Roth IRA': "IRA's",
            'SEP-IRA': "IRA's",
            'Simple IRA': "IRA's",
            'Beneficiary IRA Individual': "IRA's",
            'Beneficiary Roth IRA Individual': "IRA's",
            'Beneficiary IRA Trust': "IRA's",
            'Beneficiary Roth IRA Trust': "IRA's",
            '401(k)': 'Retirement Plans',
            'Individual 401(k)': 'Retirement Plans',
            'Defined Benefit Pension Plan': 'Retirement Plans',
            'Money Purchase Pension Plan': 'Retirement Plans',
            'Profit Sharing Plan': 'Retirement Plans',
            Corporation: 'Business Accounts',
            'Limited Liability Company': 'Business Accounts',
            Partnership: 'Business Accounts',
            'Sole Proprietor': 'Business Accounts',
            'Sub-Custodian FBO': 'Business Accounts',
            '501(c)': 'Organizations',
            'Endowment (Non-Taxable)': 'Organizations',
            'Endowment (Taxable)': 'Organizations',
            'Foundation (Non-Taxable)': 'Organizations',
            'Foundation (Taxable)': 'Organizations',
            'Uniform Gift to Minors': 'Other',
            'Uniform Transfer to Minors': 'Other',
            Guardianship: 'Other',
            Estate: 'Other',
        };

        const category = categoryMap[registrationType];
        if (!category) {
            throw new Error(`Registration type '${registrationType}' not found in category map`);
        }

        // Hover over the parent category to reveal nested options
        const parentCategory = this.page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: category })
            .locator('p')
            .first();
        await parentCategory.hover();

        // Click the exact nested option using regex for exact match
        const nestedOption = this.page
            .locator('[class*="accounts-select-dropdown_nestedListItem"]')
            .filter({ hasText: new RegExp(`^${registrationType}$`) });
        await nestedOption.click();
    }

    /**
     * Navigate to client's portfolio details
     */
    async navigateToClientPortfolioDetails(): Promise<void> {
        await selectIfVisible(this.viewDocumentHistoryLink);
        await this.portfolioDetailsLink.click();
    }

    /**
     * Navigate to client's portfolio details
     * @param clientName - Full name of the client (e.g., 'Guy Dude, Individual')
     */
    async deleteClient(): Promise<void> {
        // Clicks delete and accepts confirmation dialog, waits for page redirect before moving on
        this.page.once('dialog', async dialog => {
            logger.debug(dialog.message());
            await dialog.accept();
        });
        await this.deleteClientLink.click();
        await this.page.getByText('There are two ways to get started.').waitFor({ state: 'visible', timeout: 10000 });
    }

    /**
     * Select all widgets if they are not already selected
     */
    async selectAllWidgetsIfNeeded(): Promise<void> {
        await this.widgetSelectionDropdownButton.click();
        const widgets = [
            this.performanceWidgetCheckbox,
            this.drawdownWidgetCheckbox,
            this.summaryStatisticsWidgetCheckbox,
            this.riskVsReturnWidgetCheckbox,
            this.assetAllocationWidgetCheckbox,
            this.stressTestWidgetCheckbox,
            this.returnByStrategyWidgetCheckbox,
            this.investmentApproachWidgetCheckbox,
            this.upsideDownsideWidgetCheckbox,
        ];

        for (const widget of widgets) {
            const isChecked = await widget.evaluate(el => {
                // Check if the parent li has a class indicating checked state
                const listItem = el.closest('li');
                return (
                    listItem?.classList.contains('selected') ||
                    listItem?.classList.contains('checked') ||
                    el.getAttribute('aria-checked') === 'true' ||
                    window.getComputedStyle(el).opacity === '1'
                );
            });

            if (!isChecked) {
                await widget.click();
            }
        }
    }

    /**
     * Get the control button (3-dot menu) for a specific portfolio by date or name
     * @param identifier - The date (e.g., '12/18/25') or unique identifier of the portfolio
     * @example
     * const button = portfolioEnginePage.getPortfolioControlButton('12/18/25');
     * await button.click();
     */
    getPortfolioControlButton(identifier: string): Locator {
        // Find the row containing the identifier, then get the 3-dot button in that row
        return this.page
            .locator('[class*="popup-component"]')
            .locator('tbody tr')
            .filter({ hasText: identifier })
            .locator('button[class*="button-icon"]')
            .filter({ has: this.page.locator('svg[viewBox="0 0 17 17"]') })
            .first();
    }

    /**
     * Delete all portfolios matching the specified identifier (date or name). Defaults to today's date if no identifier provided.
     * @param identifier - The date (e.g., '12/18/25') or portfolio name to delete. If not provided, uses today's date.
     */
    async deletePortfolio(identifier?: string): Promise<void> {
        const dateToUse = identifier ?? this.getTodayDate();
        let hasMatchingPortfolios = true;

        while (hasMatchingPortfolios) {
            // Try to find the control button for the matching portfolio
            const controlButton = this.getPortfolioControlButton(dateToUse);
            const isVisible = await controlButton.isVisible().catch(() => false);

            if (isVisible) {
                await controlButton.click();
                await this.portfolioDeleteText.click();
                await this.portfolioDeleteConfirmButton.click();
            } else {
                hasMatchingPortfolios = false;
            }
        }
    }

    /**
     * Delete all portfolios in the manage portfolios view regardless of date or name
     * @example
     * await portfolioEnginePage.managePortfoliosButton.click();
     * await portfolioEnginePage.deleteAllPortfolios();
     */
    async deleteAllPortfolios(): Promise<void> {
        let hasPortfolios = true;

        while (hasPortfolios) {
            // Find all control buttons in the portfolio table
            const controlButtons = this.page
                .locator('[class*="popup-component"]')
                .locator('tbody tr')
                .locator('button[class*="button-icon"]')
                .filter({ has: this.page.locator('svg[viewBox="0 0 17 17"]') });

            const count = await controlButtons.count();

            if (count > 0) {
                // Click the first control button
                await controlButtons.first().click();
                await this.portfolioDeleteText.click();
                await this.portfolioDeleteConfirmButton.click();
            } else {
                hasPortfolios = false;
            }
        }
    }

    /**
     * Validate that a canvas element has rendered content
     * @param canvas - The canvas locator to validate
     * @returns Promise<boolean> - True if canvas has rendered content, false otherwise
     */
    async validateCanvas(canvas: Locator): Promise<boolean> {
        const hasRenderedContent = await canvas.evaluate((el: HTMLCanvasElement) => {
            if (!el) return false;
            const ctx = el.getContext('2d');
            if (!ctx) return false;

            // Check dimensions
            if (el.width === 0 || el.height === 0) return false;

            // Check if canvas has actual pixel data (not blank)
            const imageData = ctx.getImageData(0, 0, el.width, el.height);
            const pixelData = imageData.data;

            // Check if any pixel is non-transparent or non-white
            for (let i = 0; i < pixelData.length; i += 4) {
                const alpha = pixelData[i + 3];
                if (alpha > 0) {
                    // Found a non-transparent pixel, canvas has content
                    return true;
                }
            }

            return false; // Canvas is completely transparent/blank
        });
        return hasRenderedContent;
    }

    /**
     * Verify a proposal section by clicking the element and validating its content
     * @param clickElement - The element to click
     * @param content - The content locator to verify
     * @returns Promise<boolean> - True if section is verified successfully
     */
    async verifyProposalSection(clickElement: Locator, content: Locator): Promise<boolean> {
        await clickElement.click();
        await content.waitFor({ state: 'visible' });
        return await this.validateCanvas(content);
    }

    /**
     * Get today's date formatted as M/D/YY
     * @returns Today's date string (e.g., '12/18/25')
     */
    private getTodayDate(): string {
        const today = new Date();
        const month = today.getMonth() + 1; // getMonth() returns 0-11
        const day = today.getDate();
        const year = today.getFullYear().toString().slice(-2);
        return `${month}/${day}/${year}`;
    }
}
