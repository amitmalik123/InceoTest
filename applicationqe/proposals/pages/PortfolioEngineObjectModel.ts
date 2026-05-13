import { selectIfVisible } from "../helperfunctions/selectIfVisible";
import { type Locator, type Page } from "@playwright/test";
import { logger } from "../utils/logger";

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
    readonly taxManagementServicesText: Locator;
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
    readonly taxManagementServicesCanvas: Locator;
    readonly clientSignatureCanvas: Locator;
    readonly investmentPolicyCanvas: Locator;

    // Asset Allocation Summary - Investment Approach Rows
    readonly coreMarketsRow: Locator;
    readonly tacticalEnhancedReturnRow: Locator;
    readonly tacticalLimitLossRow: Locator;
    readonly diversifyingEquityAlternativesRow: Locator;
    readonly diversifyingBondsRow: Locator;
    readonly additionalInvestmentsRow: Locator;

    // Client Search Elements
    readonly loadingImageModal: Locator;
    readonly clientSearchInput: Locator;
    readonly searchButton: Locator;
    readonly noClientsFoundMessage: Locator;
    readonly noResultsMessage: Locator;
    readonly clientCollapsedLink: Locator;
    readonly viewDocumentHistoryLink: Locator;
    readonly deleteClientLink: Locator;
    readonly portfolioDetailsLink: Locator;
    readonly newClientExperienceDecline: Locator;
    readonly okButton: Locator;
    readonly privacyPolicyButton: Locator;
    readonly privacyDialogRejectAllButton: Locator;

    constructor(page: Page) {
        this.page = page;

        // Navigation Links (Main Page)
        this.investmentsLink = page.getByRole("link", { name: "Investments" });
        this.portfolioEngineLink = page.getByRole("link", {
            name: "PortfolioEngine",
            exact: true,
        });
        this.launchPortfolioEngineImg = page
            .getByRole("img", { name: "Launch Portfolio Engine" })
            .first();
        this.clientsLink = page.locator(
            'a[href="/AccountsAnalysis/Clients/ClientList"]',
        );
        this.getStartedButton = page.getByRole("button", {
            name: "Get Started...",
        });

        // Widget Headers
        this.upsideDownsideCaptureHeader = page.getByRole("heading", {
            name: /Upside.*Downside Capture/i,
        });
        this.investmentApproachHeader = page.getByRole("heading", {
            name: /Investment Approach/i,
        });
        this.returnByStrategyHeader = page.getByRole("heading", {
            name: /Return by Strategy/i,
        });
        this.stressTestHeader = page.getByRole("heading", {
            name: /Stress Test/i,
        });
        this.assetAllocationHoldingsHeader = page.getByRole("heading", {
            name: /Asset Allocation.*Holdings/i,
        });
        this.riskVsReturnHeader = page.getByRole("heading", {
            name: /Risk vs Return/i,
        });
        this.summaryStatisticsHeader = page.getByRole("heading", {
            name: /Summary Statistics/i,
        });
        this.drawdownHeader = page.getByRole("heading", { name: /Drawdown/i });
        this.performanceHeader = page.getByRole("heading", {
            name: /Performance/i,
        });

        // Widget Selection Checkboxes
        this.widgetSelectionDropdownButton = page
            .locator("header")
            .getByRole("button")
            .filter({ has: page.locator('svg path[d*="M10 13.5a3.5"]') });
        this.performanceWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Performance" })
            .locator("span")
            .first();
        this.drawdownWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Drawdown" })
            .locator("span")
            .first();
        this.summaryStatisticsWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Summary Statistics" })
            .locator("span")
            .first();
        this.riskVsReturnWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Risk vs Return" })
            .locator("span")
            .first();
        this.assetAllocationWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Asset Allocation & Holdings" })
            .locator("span")
            .first();
        this.stressTestWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Stress Test" })
            .locator("span")
            .first();
        this.returnByStrategyWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Return by Strategy" })
            .locator("span")
            .first();
        this.investmentApproachWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Investment Approach" })
            .locator("span")
            .first();
        this.upsideDownsideWidgetCheckbox = page
            .locator('[class*="menu-component__item"]')
            .filter({ hasText: "Upside/Downside Capture" })
            .locator("span")
            .first();

        // Widget graph containers - has header and content
        this.performanceGraphContainer = page
            .locator("article")
            .filter({ hasText: "Performance" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.drawdownGraphContainer = page
            .locator("article")
            .filter({ hasText: "Drawdown" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.summaryStatisticsGraphContainer = page
            .locator("article")
            .filter({ hasText: "Summary Statistics" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.riskVsReturnGraphContainer = page
            .locator("article")
            .filter({ hasText: "Risk vs Return" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.assetAllocationGraphContainer = page
            .locator("article")
            .filter({ hasText: "Asset Allocation & Holdings" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.stressTestGraphContainer = page
            .locator("article")
            .filter({ hasText: "Stress Test" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.returnByStrategyGraphContainer = page
            .locator("article")
            .filter({ hasText: "Return by Strategy" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.investmentApproachGraphContainer = page
            .locator("article")
            .filter({ hasText: "Investment Approach" })
            .first()
            .locator('div[class*="widget-component__content"]');
        this.upsideDownsideGraphContainer = page
            .locator("article")
            .filter({ hasText: "Upside/Downside Capture" })
            .first()
            .locator('div[class*="widget-component__content"]');

        // Widget Content Elements - specific chart/graph elements for validation
        this.performanceGraphContent =
            this.performanceGraphContainer.locator("svg text");
        this.drawdownGraphContent =
            this.drawdownGraphContainer.locator("tbody tr");
        this.summaryStatisticsGraphContent =
            this.summaryStatisticsGraphContainer.locator("tbody tr");
        this.riskVsReturnGraphContent =
            this.riskVsReturnGraphContainer.locator("svg circle");
        this.assetAllocationGraphContent =
            this.assetAllocationGraphContainer.locator(
                'svg path[class*="recharts-sector"]',
            );
        this.stressTestGraphContent =
            this.stressTestGraphContainer.locator('div[class*="tick"]');
        this.returnByStrategyGraphContent =
            this.returnByStrategyGraphContainer.locator("svg rect");
        this.investmentApproachGraphContent =
            this.investmentApproachGraphContainer.locator(
                'svg path[class*="recharts-sector"]',
            );
        this.upsideDownsideGraphContent =
            this.upsideDownsideGraphContainer.locator("svg rect");

        // Portfolio Management Buttons
        this.managePortfoliosButton = page.getByRole("button", {
            name: "Manage Portfolios",
        });
        this.createNewModelPortfolioButton = page.getByRole("button", {
            name: "Create New Model Portfolio",
        });
        this.strategySaveButton = page
            .locator(
                '[class*="popup-component__footer"], [class*="management-footer"]',
            )
            .getByRole("button", { name: "Save" });
        this.portfolioCloseButton = page
            .locator(
                '[class*="popup-component__footer"], [class*="management-footer"]',
            )
            .getByRole("button", { name: "Close" });
        this.createProposalButton = page.getByRole("button", {
            name: "Create Proposal",
        });

        // Portfolio Management - Delete Elements
        this.portfolioDeleteControlButton = page
            .locator('[class*="popup-component"]')
            .locator('button[class*="button-icon"]')
            .filter({ has: page.locator('svg[viewBox="0 0 17 17"]') })
            .first();
        this.portfolioDeleteText = page
            .locator('[class*="popover-controls-component__action"]')
            .getByText("Delete", { exact: true });
        this.portfolioDeleteConfirmButton = page.getByRole("button", {
            name: "Delete",
        });
        this.previewProposalButton = page.getByRole("button", {
            name: "Preview Proposal",
        });
        this.saveProposalButton = page.getByRole("button", {
            name: "save proposal",
        });
        this.viewDocumentsButton = page.getByRole("button", {
            name: "View Documents",
        });
        this.quitProposalButton = page.locator('img[src*="x-icon"]').first();

        // Portfolio Creation Elements
        this.assetMarkPlatformStrategiesText = page.getByText(
            "AssetMark Platform Strategies",
            { exact: true },
        );
        this.SavosPersonalStrategyText = page.getByText(
            "Savos Personal Portfolio Custom",
            { exact: true },
        );
        this.strategySearchBox = page.getByRole("textbox", { name: "Search" });
        this.addToPortfolioText = page.getByText("Add to Portfolio");
        this.modelPortfolioNameTextbox = page.getByRole("textbox", {
            name: "Model Portfolio Name",
        });
        this.investmentAllocationText = page
            .locator('[class*="sidebar-portfolio-component"]')
            .locator('[class*="sectionTwo"]');

        // Proposal Creation - Client Type
        this.newClientRadio = page.getByRole("radio", { name: "New Client" });
        this.newClientText = page.getByText("New Client");
        this.existingClientRadio = page.getByRole("radio", {
            name: "Existing Client",
        });
        this.existingClientText = page.getByText("Existing Client");
        this.discretionaryRadio = page.getByRole("radio", {
            name: "Discretionary",
            exact: true,
        });
        this.discretionaryText = page.getByText("Discretionary", {
            exact: true,
        });
        this.nonDiscretionaryRadio = page.getByRole("radio", {
            name: "Non-Discretionary",
        });
        this.nonDiscretionaryText = page.getByText("Non-Discretionary");
        this.firstNameTextbox = page.getByRole("textbox", { name: "First" });
        this.lastNameTextbox = page.getByRole("textbox", { name: "Last" });
        this.nextButton = page.getByRole("button", { name: "NEXT" });

        // Proposal Creation - Risk Profile
        this.moderateRiskRadio = page.getByRole("radio", {
            name: "Moderate",
            exact: true,
        });
        this.timeHorizonNineYearsRadio = page.getByRole("radio", {
            name: "6 - 9 years",
        });
        this.declineFiftyPercentRadio = page.getByRole("radio", {
            name: "25 - 50%",
        });
        this.riskToleranceModerateRadio = page.getByRole("radio", {
            name: "3 - Moderate",
        });

        // Proposal Creation - Account Setup
        this.selectCustodianDropdown = page
            .locator('[class*="custodian"], [class*="dropdown"]')
            .getByRole("img", { name: "ArrowDown" })
            .first();
        this.fidelityText = page
            .getByRole("listitem")
            .filter({ hasText: /^Fidelity$/ });
        this.assetMarkText = page
            .getByRole("listitem")
            .filter({ hasText: /^AssetMark Trust$/ });
        this.schwabText = page
            .getByRole("listitem")
            .filter({ hasText: /^Schwab$/ });
        this.pershingAdvisorSolutionsText = page
            .getByRole("listitem")
            .filter({ hasText: /^Pershing Advisor Solutions$/ });
        this.addRegistrationButton = page
            .locator('img[class*="accounts_icon"]')
            .first();
        this.registrationNameTextbox = page.getByRole("textbox");
        this.registrationTypeDropdown = page
            .locator('[class*="accounts_regType"]')
            .locator('[class*="accounts-select-dropdown_secondSelectCss"]');
        this.individualCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Individual" })
            .locator("p")
            .first();
        this.trustCategory = page
            .locator('[class*="accounts-select-dropdown_parentList"]')
            .filter({ hasText: "Trust" })
            .locator("p");
        this.jointCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Joint" })
            .locator("p")
            .first();
        this.irasCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "IRA's" })
            .locator("p")
            .first();
        this.retirementPlansCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Retirement Plans" })
            .locator("p")
            .first();
        this.businessAccountsCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Business Accounts" })
            .locator("p")
            .first();
        this.organizationsCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Organizations" })
            .locator("p")
            .first();
        this.otherCategory = page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: "Other" })
            .locator("p")
            .first();
        this.addAccountButton = page.locator('img[class*="addAccIcon"]');
        this.modelListConfirm = page
            .locator('[class*="accounts-popUp"]')
            .getByRole("button", { name: "CONFIRM", exact: true });
        this.investmentAmountInput = page.locator(
            'input[name="investmentAmount"]',
        );
        this.enrollInTaxRadio = page.getByRole("radio", {
            name: "Enroll in Tax Management Services",
            exact: true,
        });
        this.doNotEnrollInTaxRadio = page.getByRole("radio", {
            name: "Do not enroll in Tax",
        });
        this.confirmText = page.getByText("CONFIRM", { exact: true });

        // Proposal Creation - Verification Elements
        this.proposedAccountsContainer = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_toggleCta"]',
        );
        this.proposedAccountsHeader = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_toggleHeader"]',
        );
        this.proposedAccountsAmount = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_toggleAmount"]',
        );
        this.accountHolderName = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_regName"]',
        );
        this.multipleStrategyAccountName = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_toggleDataName"]',
        );
        this.multipleStrategyAccountAmount = page.locator(
            '[class*="proposedAccounts-sidebar-toggle_toggleDataValue"]',
        );
        this.enterFeePercentageTextbox = page.getByRole("textbox", {
            name: "Enter %",
        });
        this.feeDetailsContainer = page.locator('[class*="fees_feeDetails"]');
        this.portfolioValueLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Portfolio Value" })
            .locator("div")
            .first();
        this.portfolioValueAmount = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Portfolio Value" })
            .locator("div")
            .last();
        this.financialAdvisorFeeLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Financial Advisor" })
            .locator("div")
            .first();
        this.financialAdvisorFee = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Financial Advisor" })
            .locator("div")
            .last();
        this.platformFeeLabel = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Platform" })
            .locator("div")
            .first();
        this.platformFee = this.feeDetailsContainer
            .locator('[class*="fees_feeValue"]')
            .filter({ hasText: "Platform" })
            .locator("div")
            .last();

        this.totalFeeLabel = this.feeDetailsContainer
            .locator('[class*="fees_totalFee"]')
            .locator("div")
            .first();
        this.totalFee = this.feeDetailsContainer
            .locator('[class*="fees_totalFee"]')
            .locator("div")
            .last();
        this.continueButton = page.getByRole("button", { name: "Continue" });
        this.fundedAccountsDiv = page
            .locator("div")
            .filter({ hasText: /^Funded Accounts\(0\) \$0$/ })
            .first();
        this.oneCombinedDocumentText = page.getByText("One Combined Document");

        // Strategy Checkboxes
        this.assetMarkIncomeBuilderCheckbox = page.getByRole("checkbox", {
            name: "AssetMark Income Builder, Profile 2, Conservative",
        });
        this.blackRockEquityDividendCheckbox = page.getByRole("checkbox", {
            name: "BlackRock Equity Dividend",
        });
        this.savosUSRiskCheckbox = page.getByRole("checkbox", {
            name: "Savos US Risk Controlled Strategy, Profile 6",
        });
        this.alphaSimplexCheckbox = page.getByRole("checkbox", {
            name: "AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth",
        });
        this.jpMorganAbsoluteReturnCheckbox = page.getByRole("checkbox", {
            name: "JPMorgan Absolute Return - Profile 1",
        });

        // Strategy Display Text
        this.assetMarkIncomeBuilderText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({
                hasText: "AssetMark Income Builder, Profile 2, Conservative",
            });
        this.blackRockEquityDividendText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: "BlackRock Equity Dividend" });
        this.savosUSRiskText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({
                hasText: "Savos US Risk Controlled Strategy, Profile 6",
            });
        this.alphaSimplexText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({
                hasText:
                    "AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth",
            });
        this.jpMorganAbsoluteReturnText = page
            .locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]')
            .filter({ hasText: "JPMorgan Absolute Return - Profile 1" });

        // Proposal Document Sections - Checkboxes
        this.introductionCheckbox = page.locator(
            ".th-Introduction-wrap .checkbox-container .clsA",
        );
        this.pursuingYourGoalsCheckbox = page
            .locator(".th-wrap.th-Investing .checkbox-container .clsA")
            .first();
        this.investingIsPersonalCheckbox = page
            .locator(".th-wrap.th-Investing .checkbox-container .clsA")
            .nth(1);
        this.equitiesVsBondsCheckbox = page
            .locator(".th-wrap.th-Growth .checkbox-container .clsA")
            .first();
        this.cycleOfEmotionsCheckbox = page.locator(
            ".th-wrap.th-The.Cycle .checkbox-container .clsA",
        );
        this.stayingInvestedCheckbox = page
            .locator(".th-wrap.th-Growth .checkbox-container .clsA")
            .nth(1);
        this.yourInvestmentTeamCheckboxTop = page
            .locator(".th-wrap.th-Your .checkbox-container .clsA")
            .first();
        this.yourInvestmentTeamCheckboxInside = page
            .locator(".th-wrap.th-Your .checkbox-container .clsA")
            .nth(1);
        this.portfolioStrategistsCheckbox = page.locator(
            ".th-wrap.th-Portfolio .checkbox-container .clsA",
        );
        this.custodianSelectionCheckbox = page.locator(
            ".th-wrap.th-Custodian .checkbox-container .clsA",
        );
        this.ongoingReviewCheckbox = page.locator(
            ".th-wrap.th-Ongoing .checkbox-container .clsA",
        );
        this.recommendedInvestmentPortfolioCheckbox = page
            .locator(".th-wrap.th-Recommended .checkbox-container .clsA")
            .first();
        this.allocationByAssetClassCheckbox = page.locator(
            ".th-wrap.th-Allocation .checkbox-container .clsA",
        );
        this.topHoldingsCheckbox = page.locator(
            ".th-wrap.th-Top .checkbox-container .clsA",
        );
        this.proposedAccountsEstimatedYieldCheckbox = page.locator(
            ".th-wrap.th-Proposed .checkbox-container .clsA",
        );
        this.hypotheticalHistoricalPerformanceCheckbox = page
            .locator(".th-wrap.th-Hypothetical .checkbox-container .clsA")
            .first();
        this.hypotheticalGrowthOfProposedAccountsCheckbox = page
            .locator(".th-wrap.th-Hypothetical .checkbox-container .clsA")
            .nth(1);
        this.ratesCheckbox = page.locator(
            ".th-wrap.th-Rates .checkbox-container .clsA",
        );
        this.calendarYearReturnsCheckbox = page.locator(
            ".th-wrap.th-Calendar .checkbox-container .clsA",
        );
        this.historicalCumulativePerformanceCheckbox = page.locator(
            ".th-wrap.th-Historical .checkbox-container .clsA",
        );
        this.riskVersusReturnCheckbox = page.locator(
            ".th-wrap.th-Risk .checkbox-container .clsA",
        );
        this.annualPortfolioFeesCheckbox = page
            .locator(".th-wrap.th-Fee .checkbox-container .clsA")
            .first();
        this.tieredFeeScheduleCheckbox = page.locator(
            ".th-wrap.th-Tiered .checkbox-container .clsA",
        );
        this.estimateExpenseCheckbox = page.locator(
            ".th-wrap.th-Estimated .checkbox-container .clsA",
        );
        this.clientSignatureCheckbox = page.locator(
            ".th-wrap.th-Client .checkbox-container .clsA",
        );
        this.investmentPolicyStatementCheckbox = page.locator(
            ".th-wrap.th-Investment .checkbox-container .clsA",
        );

        // Proposal Document Sections - Dropdown Icons (using stable section-specific patterns)
        this.pursuingYourGoalsDropdownIcon = page.locator(
            ".th-wrap.th-Investing .icon-holder i",
        );
        this.recommendedInvestmentPortfolioDropdownIcon = page
            .locator(".th-wrap.th-Recommended .icon-holder i")
            .first();
        this.hypotheticalHistoricalPerformanceDropdownIcon = page
            .locator(".th-wrap.th-Hypothetical .icon-holder i")
            .first();
        this.annualPortfolioFeesDropdownIcon = page
            .locator(".th-wrap.th-Fee .icon-holder i")
            .first();

        // Proposal Document Verification - Click Elements
        this.coverPageHeader = page.locator(".th-header").first();
        this.pursueYourGoalsText = page.getByText("Pursue Your Goals", {
            exact: true,
        });
        this.tableOfContentsText = page.getByText("Table Of Contents", {
            exact: true,
        });
        this.introductionHeader = page
            .getByRole("heading", { name: /Introduction/i })
            .or(page.locator(".th-wrap.th-Introduction-wrap .th-header"));
        this.investingIsPersonalText = page.getByText("Investing is Personal", {
            exact: true,
        });
        this.equitiesVsBondsTitle = page
            .locator(".th-wrap.th-Growth .th-title")
            .filter({ hasText: "Equities vs. Bonds" });
        this.cycleOfEmotionsHeader = page
            .getByRole("heading", { name: /Cycle of Emotions/i })
            .or(page.locator(".th-wrap.th-The.Cycle .th-header"));
        this.stayingInvestedTitle = page
            .locator(".th-wrap.th-Growth .th-title")
            .filter({ hasText: "Staying Invested" });
        this.yourInvestmentTeamDiv = page.getByText("Your Investment Team (3)");
        this.portfolioStrategistsSection = page.locator(
            ".th-wrap.th-Portfolio",
        );
        this.custodianSelectionHeader = page
            .getByRole("heading", { name: /Custodian Selection/i })
            .or(page.locator(".th-wrap.th-Custodian .th-header"));
        this.ongoingReviewText = page.getByText(
            "Ongoing Review of Your Portfolio",
            { exact: true },
        );
        this.yourFinancialAnalysisHeader = page.locator(
            ".th-wrap.th-Your.Financial",
        );
        this.recommendedPortfolioDiv = page
            .locator(".th-title.th-listview-title.listview-child")
            .filter({ hasText: "Recommended Portfolio" });
        this.allocationByAssetClassHeader = page
            .getByRole("heading", { name: /Allocation by Asset Class/i })
            .or(page.locator(".th-wrap.th-Allocation .th-header"));
        this.topHoldingsText = page.getByText("Top Holdings").first();
        this.proposedAccountsTitle = page.locator(
            ".th-wrap.th-Proposed .th-title",
        );
        this.hypotheticalHistoricalPerformanceDiv = page
            .locator(".th-wrap.th-Hypothetical .th-title")
            .filter({ hasText: "Hypothetical Historical Performance" })
            .first();
        this.hypotheticalSectionTitle = page
            .locator(".th-wrap.th-Hypothetical .th-title")
            .filter({ hasText: "Hypothetical Historical Performance" })
            .last();
        this.ratesHeader = page
            .getByRole("heading", { name: /Rates/i })
            .or(page.locator(".th-wrap.th-Rates .th-header"));
        this.calendarYearReturnsText = page.locator(
            ".th-wrap.th-Calendar .th-header",
        );
        this.historicalCumulativeText = page
            .locator(".th-wrap.th-Historical > .th-header > .th-title")
            .filter({ hasText: "Historical Cumulative" });
        this.riskVersusReturnSection = page.locator(".th-wrap.th-Risk");
        this.feeScheduleDiv = page
            .locator("div")
            .filter({ hasText: /^Annual Portfolio Fees \(3\)$/ })
            .first();

        this.tieredFeeScheduleHeader = page
            .getByRole("heading", { name: /Tiered Fee Schedule/i })
            .or(page.locator(".th-wrap.th-Tiered .th-header"));
        this.estimateExpenseTitle = page.locator(
            ".th-wrap.th-Estimated .th-title",
        );
        this.importantInformationText = page.getByText(
            "Important Information and Standardized Performance Returns",
            {
                exact: true,
            },
        );
        this.disclosuresTitle = page.locator(
            ".th-wrap.th-Disclosures .th-title",
        );
        this.taxManagementServicesText = page.locator(
            ".th-wrap.th-Tax.Management.Services-wrap .th-title",
        );
        this.clientSignatureText = page.getByText("Client Signature", {
            exact: true,
        });
        this.investmentPolicyStatementText = page.getByText(
            "Investment Policy Statement",
            { exact: true },
        );

        // Proposal Document Verification - Content Visibility
        this.previewLayoutContentFirst = page
            .locator(".page-component:not(.fainted) canvas")
            .first();
        this.tableOfContentsContent = page.locator(
            ".page-wrap.Table:not(.fainted) canvas",
        );
        this.introductionContent = page.locator(
            ".page-wrap.Introduction-page-component-wrap:not(.fainted) canvas",
        );
        this.investingContent = page.locator(
            ".page-wrap.Investing:not(.fainted) canvas",
        );
        this.growthContentFirst = page
            .locator(".page-wrap.Growth:not(.fainted) canvas")
            .first();
        this.theContent = page.locator(".page-wrap.The:not(.fainted) canvas");
        this.growthContentSecond = page
            .locator(".page-wrap.Growth:not(.fainted) canvas")
            .nth(1);
        this.yourContentCanvas = page
            .locator(".page-wrap.Your:not(.fainted) canvas")
            .first();
        this.portfolioContent = page.locator(
            ".page-wrap.Portfolio:not(.fainted) canvas",
        );
        this.custodianContent = page.locator(
            ".page-wrap.Custodian:not(.fainted) canvas",
        );
        this.ongoingContent = page.locator(
            ".page-wrap.Ongoing:not(.fainted) canvas",
        );
        this.yourFinancialContent = page.locator(
            ".page-wrap.Your.Financial:not(.fainted) canvas",
        );
        this.recommendedContent = page.locator(
            ".page-wrap.Recommended:not(.fainted) canvas",
        );
        this.allocationContent = page.locator(
            ".page-wrap.Allocation:not(.fainted) canvas",
        );
        this.topHoldingsContent = page.locator(
            ".page-wrap.Top:not(.fainted) canvas",
        );
        this.proposedContentFirst = page
            .locator(".page-wrap.Proposed:not(.fainted) canvas")
            .first();
        this.hypotheticalContent = page.locator(
            ".page-wrap.Hypothetical:not(.fainted) canvas",
        );
        this.ratesContent = page.locator(
            ".page-wrap.Rates:not(.fainted) canvas",
        );
        this.calendarContent = page.locator(
            ".page-wrap.Calendar:not(.fainted) canvas",
        );
        this.historicalContent = page.locator(
            ".page-wrap.Historical:not(.fainted) canvas",
        );
        this.riskContent = page.locator(".page-wrap.Risk:not(.fainted) canvas");
        this.feeContentFirst = page
            .locator(".page-wrap.Fee:not(.fainted) canvas")
            .first();
        this.tieredContent = page.locator(
            ".page-wrap.Tiered:not(.fainted) canvas",
        );
        this.estimatedExpenseCanvas = page.locator(
            ".page-wrap.Estimated.Expense:not(.fainted) canvas",
        );
        this.importantInformationCanvas = page.locator(
            ".page-wrap.Important.Information:not(.fainted) canvas",
        );
        this.disclosuresCanvas = page.locator(
            ".page-wrap.Disclosures:not(.fainted) canvas",
        );
        this.taxManagementServicesCanvas = page.locator(
            ".page-wrap.Tax.Management.Services-page-component-wrap:not(.fainted) canvas",
        );
        this.clientSignatureCanvas = page.locator(
            ".page-wrap.Client:not(.fainted) canvas",
        );
        this.investmentPolicyCanvas = page.locator(
            ".page-wrap.Investment.Policy:not(.fainted) canvas",
        );

        // Asset Allocation Summary - Investment Approach Rows
        this.coreMarketsRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(0);
        this.tacticalEnhancedReturnRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(1);
        this.tacticalLimitLossRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(2);
        this.diversifyingEquityAlternativesRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(3);
        this.diversifyingBondsRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(4);
        this.additionalInvestmentsRow = page
            .locator("#asset-allocation-summary-widget .asset-class")
            .nth(5);

        // Client Search Elements
        this.loadingImageModal = page.locator("#loadingImageModal");
        this.clientSearchInput = page
            .getByRole("textbox", { name: "client_search_input" })
            .or(page.locator("#client_search_input"));
        this.searchButton = page
            .getByRole("button", { name: "search" })
            .or(page.locator("#searchbutton"));
        this.noClientsFoundMessage = page.getByText(
            "No search results were found.",
        );
        this.noResultsMessage = page.getByText("No search results were found");
        this.clientCollapsedLink = page.locator(
            'td[role="gridcell"][aria-describedby="ClientListGrid_clientName"]',
        );
        this.viewDocumentHistoryLink = page.getByRole("link", {
            name: "View Document History",
        });
        this.portfolioDetailsLink = page.getByRole("link", {
            name: "Portfolio Details",
        });
        this.deleteClientLink = page.getByRole("link", {
            name: "Delete Client",
        });
        this.newClientExperienceDecline = page.getByRole("button", {
            name: "No, Thank You",
        });
        this.okButton = page.getByRole("button", { name: "OK" });
        this.privacyPolicyButton = page.getByRole("button", {
            name: "I Agree",
        });
        this.privacyDialogRejectAllButton = page.locator(
            '[class="ot-pc-refuse-all-handler"]',
        );
    }

    // Helper Methods

    /**
     * Dismiss the OneTrust privacy consent dialog (test11 only)
     */
    async dismissPrivacyDialog(): Promise<void> {
        if (process.env.ENVIRONMENT === "test11") {
            try {
                await this.privacyDialogRejectAllButton.click({
                    timeout: 10000,
                });
            } catch (err) {
                // Privacy dialog not present, continue
            }
        }
    }

    /**
     * Get client name cell by display name
     * @param displayName - Client name in display format (LastName, FirstName)
     */
    getClientNameCell(displayName: string): Locator {
        return this.page
            .locator("#ClientListGrid tbody tr.jqgrow td")
            .filter({ hasText: displayName })
            .first();
    }

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
        return this.page
            .locator('[class*="portfolio-valid-item"]')
            .locator('input[type="text"]')
            .nth(index);
    }

    /**
     * Fill client information for new client
     * @param firstName - Client's first name
     * @param lastName - Client's last name
     */
    async fillNewClientInfo(
        firstName: string,
        lastName: string,
    ): Promise<void> {
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

    async clickAndWaitForExpansion(clickElement: Locator): Promise<void> {
        await clickElement.click();
        await this.page.waitForTimeout(100);
    }

    /**
     * Set all proposal document section checkboxes
     */
    async setAllProposalSections(): Promise<void> {
        const setAndVerifyCheckbox = async (checkbox: Locator) => {
            // First, check if already checked to avoid unnecessary operations
            const currentState = await checkbox.isChecked().catch(() => false);
            if (currentState) {
                // Already checked, no action needed
                return;
            }

            // Set the checkbox using click for more reliable event handling
            await checkbox.click();

            // Wait for the UI to process the click and update the DOM
            await this.page.waitForTimeout(100);

            // Verify the checkbox is now checked with retry logic
            let isChecked = await checkbox.isChecked().catch(() => false);

            if (!isChecked) {
                // Retry once more with additional wait
                await this.page.waitForTimeout(150);
                isChecked = await checkbox.isChecked().catch(() => false);
            }

            if (!isChecked) {
                throw new Error(`Failed to check checkbox`);
            }
        };

        // Group 1: Introduction section
        await setAndVerifyCheckbox(this.introductionCheckbox);

        // Group 2: Pursuing Your Goals (expandable)
        await this.clickAndWaitForExpansion(this.pursuingYourGoalsDropdownIcon);

        // Group 3: Investing is Personal
        await setAndVerifyCheckbox(this.investingIsPersonalCheckbox);

        // Group 4: Equities vs Bonds
        await setAndVerifyCheckbox(this.equitiesVsBondsCheckbox);

        // Group 5: Cycle of Emotions
        await setAndVerifyCheckbox(this.cycleOfEmotionsCheckbox);

        // Group 6: Staying Invested
        await setAndVerifyCheckbox(this.stayingInvestedCheckbox);

        // Group 7: Investment Team (dual checkboxes)
        await setAndVerifyCheckbox(this.yourInvestmentTeamCheckboxInside);

        // Group 8: Portfolio Strategists
        await setAndVerifyCheckbox(this.portfolioStrategistsCheckbox);

        // Group 9: Custodian Selection
        await setAndVerifyCheckbox(this.custodianSelectionCheckbox);

        // Group 10: Ongoing Review
        await setAndVerifyCheckbox(this.ongoingReviewCheckbox);

        // Group 11: Recommended Investment Portfolio (expandable)
        await this.clickAndWaitForExpansion(
            this.recommendedInvestmentPortfolioDropdownIcon,
        );

        // Group 12: Asset Allocation and Holdings
        await setAndVerifyCheckbox(this.allocationByAssetClassCheckbox);
        await setAndVerifyCheckbox(this.topHoldingsCheckbox);
        await setAndVerifyCheckbox(this.proposedAccountsEstimatedYieldCheckbox);

        // Group 13: Hypothetical Performance (expandable)
        await this.clickAndWaitForExpansion(
            this.hypotheticalHistoricalPerformanceDropdownIcon,
        );
        await setAndVerifyCheckbox(
            this.hypotheticalGrowthOfProposedAccountsCheckbox,
        );

        // Group 14: Performance Data
        await setAndVerifyCheckbox(this.ratesCheckbox);
        await setAndVerifyCheckbox(this.calendarYearReturnsCheckbox);
        await setAndVerifyCheckbox(
            this.historicalCumulativePerformanceCheckbox,
        );
        await setAndVerifyCheckbox(this.riskVersusReturnCheckbox);

        // Group 15: Annual Portfolio Fees (expandable)
        await this.clickAndWaitForExpansion(
            this.annualPortfolioFeesDropdownIcon,
        );
        await setAndVerifyCheckbox(this.tieredFeeScheduleCheckbox);

        // Group 16: Final sections
        await setAndVerifyCheckbox(this.estimateExpenseCheckbox);
        await setAndVerifyCheckbox(this.clientSignatureCheckbox);
        await setAndVerifyCheckbox(this.investmentPolicyStatementCheckbox);

        // Wait for all UI updates to complete
        await this.page.waitForLoadState();
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
            Individual: "Individual",
            "Individual TOD": "Individual",
            "Community Property": "Joint",
            "Community Property with Rights of Survivorship": "Joint",
            "Community Property with Rights of Survivorship TOD": "Joint",
            "Joint Tenant with Rights of Survivorship": "Joint",
            "Joint Tenant with Rights of Survivorship TOD": "Joint",
            "Tenants in Common": "Joint",
            "Tenants by Entirety": "Joint",
            "Tenants by Entirety TOD": "Joint",
            "Traditional IRA": "IRA's",
            "Rollover IRA": "IRA's",
            "Roth IRA": "IRA's",
            "SEP-IRA": "IRA's",
            "Simple IRA": "IRA's",
            "Beneficiary IRA Individual": "IRA's",
            "Beneficiary Roth IRA Individual": "IRA's",
            "Beneficiary IRA Trust": "IRA's",
            "Beneficiary Roth IRA Trust": "IRA's",
            "401(k)": "Retirement Plans",
            "Individual 401(k)": "Retirement Plans",
            "403(b) Plan": "Retirement Plans",
            "Defined Benefit Pension Plan": "Retirement Plans",
            "Money Purchase Pension Plan": "Retirement Plans",
            "Profit Sharing Plan": "Retirement Plans",
            Corporation: "Business Accounts",
            "Limited Liability Company": "Business Accounts",
            Partnership: "Business Accounts",
            "Sole Proprietor": "Business Accounts",
            "Sub-Custodian FBO": "Business Accounts",
            "501(c)": "Organizations",
            "Endowment (Non-Taxable)": "Organizations",
            "Endowment (Taxable)": "Organizations",
            "Foundation (Non-Taxable)": "Organizations",
            "Foundation (Taxable)": "Organizations",
            "Uniform Gift to Minors": "Other",
            "Uniform Transfer to Minors": "Other",
            Guardianship: "Other",
            Estate: "Other",
        };

        const category = categoryMap[registrationType];
        if (!category) {
            throw new Error(
                `Registration type '${registrationType}' not found in category map`,
            );
        }

        // Hover over the parent category to reveal nested options
        const parentCategory = this.page
            .locator('[class*="accounts-select-dropdown_group"]')
            .filter({ hasText: category })
            .locator("p")
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
     * Delete the current client
     * Clicks delete link, handles confirmation dialog, and waits for redirect
     */
    async deleteClient(): Promise<void> {
        await Promise.all([
            this.page.waitForEvent("dialog").then(async (dialog) => {
                await dialog.accept();
            }),
            this.deleteClientLink.click(),
        ]);
        // Verify redirect completed
        await this.page.waitForLoadState();
        await this.page
            .getByText(/There are two ways to get started/i)
            .waitFor({ state: "visible", timeout: 10000 });
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
            const isChecked = await widget.evaluate((el) => {
                // Check if the parent li has a class indicating checked state
                const listItem = el.closest("li");
                return (
                    listItem?.classList.contains("selected") ||
                    listItem?.classList.contains("checked") ||
                    el.getAttribute("aria-checked") === "true" ||
                    window.getComputedStyle(el).opacity === "1"
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
            .locator("tbody tr")
            .filter({ hasText: identifier })
            .locator('button[class*="button-icon"]')
            .filter({ has: this.page.locator('svg[viewBox="0 0 17 17"]') })
            .first();
    }

    /**
     * Delete portfolios matching the specified names via API.
     * Fetches portfolios from /api/pe/v2/portfolios and deletes those with names matching any in the array.
     * @param names - Array of portfolio names to delete. If not provided, defaults to empty array.
     */
    async deletePortfolio(names?: Array<string>): Promise<void> {
        const namesToDelete = names ?? [];

        if (namesToDelete.length === 0) {
            logger.warn("No portfolio names provided to delete");
            return;
        }

        try {
            const baseUrl = new URL(this.page.url()).origin;

            // Fetch portfolios from API
            const response = await this.page.request.get(
                `${baseUrl}/api/pe/v2/portfolios`,
            );
            if (!response.ok()) {
                logger.error(
                    `Failed to fetch portfolios: ${response.status()}`,
                );
                return;
            }

            const data = (await response.json()) as
                | { id?: string; name?: string }[]
                | { id?: string; name?: string };
            const portfolios = Array.isArray(data) ? data : [data];

            logger.info(`Fetched ${portfolios.length} portfolios`);

            // Filter portfolios matching any of the provided names
            const portfoliosToDelete = portfolios.filter((portfolio) => {
                return portfolio.name && namesToDelete.includes(portfolio.name);
            });

            logger.info(
                `Found ${portfoliosToDelete.length} portfolios matching names: ${namesToDelete.join(", ")}`,
            );

            // Delete each matching portfolio
            for (const portfolio of portfoliosToDelete) {
                if (!portfolio.id) continue;

                try {
                    const deleteResponse = await this.page.request.delete(
                        `${baseUrl}/api/pe/v2/portfolio/${portfolio.id}`,
                    );
                    if (deleteResponse.ok()) {
                        logger.info(
                            `Successfully deleted portfolio ${portfolio.id} with name "${portfolio.name}"`,
                        );
                    } else {
                        logger.error(
                            `Failed to delete portfolio ${portfolio.id}: ${deleteResponse.status()}`,
                        );
                    }
                } catch (err) {
                    logger.error(
                        `Error deleting portfolio ${portfolio.id}: ${err instanceof Error ? err.message : String(err)}`,
                    );
                }
            }
        } catch (err) {
            logger.error(
                `Error in deletePortfolio: ${err instanceof Error ? err.message : String(err)}`,
            );
        }
    }

    /**
     * Delete portfolios created before 2025 via API.
     * Fetches all portfolios from /api/pe/v2/portfolios and /api/pe/v2/holisticPortfolio
     * and deletes those with createdOn year < 2025 or if value is null
     * Not used anywhere in the current test suite but can be used for bulk cleanup of old portfolios if needed
     * @example
     * await portfolioEnginePage.deleteAllPortfolios();
     */
    async deleteAllPortfolios(): Promise<void> {
        try {
            const baseUrl = new URL(this.page.url()).origin;

            // Fetch regular portfolios
            const response = await this.page.request.get(
                `${baseUrl}/api/pe/v2/portfolios`,
            );
            if (!response.ok()) {
                logger.error(
                    `Failed to fetch portfolios: ${response.status()}`,
                );
                return;
            }

            const data = (await response.json()) as
                | { id?: string; name?: string; createdOn?: string }[]
                | { id?: string; name?: string; createdOn?: string };
            const portfolios = Array.isArray(data) ? data : [data];

            logger.info(`Fetched ${portfolios.length} portfolios`);

            // Fetch holistic portfolios
            const holisticResponse = await this.page.request.get(
                `${baseUrl}/api/pe/v2/holisticPortfolios`,
            );
            let holisticPortfolios: {
                id?: string;
                name?: string;
                createdOn?: string;
            }[] = [];
            if (holisticResponse.ok()) {
                const holisticData = (await holisticResponse.json()) as
                    | { id?: string; name?: string; createdOn?: string }[]
                    | { id?: string; name?: string; createdOn?: string };
                holisticPortfolios = Array.isArray(holisticData)
                    ? holisticData
                    : [holisticData];
                logger.info(
                    `Fetched ${holisticPortfolios.length} holistic portfolios`,
                );
            } else {
                logger.warn(
                    `Failed to fetch holistic portfolios: ${holisticResponse.status()}`,
                );
            }

            // ============================================================
            // FILTER OPTION 1: Delete by year
            // Comment out this block to use name-based filtering instead
            // ============================================================
            const portfoliosToDelete = portfolios.filter((portfolio) => {
                if (!portfolio.createdOn) return true; // Delete if no date
                const createdYear = new Date(portfolio.createdOn).getFullYear();
                return createdYear < 2025;
            });

            const holisticPortfoliosToDelete = holisticPortfolios.filter(
                (portfolio) => {
                    if (!portfolio.createdOn) return true; // Delete if no date
                    const createdYear = new Date(
                        portfolio.createdOn,
                    ).getFullYear();
                    return createdYear < 2025;
                },
            );

            // ============================================================
            // FILTER OPTION 2: Delete by name (created before 2026)
            // Uncomment this block to delete MSAPerfModel or PerfHolisticTest portfolios
            // ============================================================
            // const portfoliosToDelete = portfolios.filter(portfolio => {
            //     if (!portfolio.name) return false;
            //     const hasTargetName =
            //         portfolio.name.includes('MSAPerfModel') || portfolio.name.includes('PerfHolisticTest');
            //     if (!hasTargetName) return false;
            //     if (!portfolio.createdOn) return true; // Delete if has target name but no date
            //     const createdYear = new Date(portfolio.createdOn).getFullYear();
            //     return createdYear < 2026;
            // });

            // const holisticPortfoliosToDelete = holisticPortfolios.filter(portfolio => {
            //     if (!portfolio.name) return false;
            //     const hasTargetName =
            //         portfolio.name.includes('MSAPerfModel') || portfolio.name.includes('PerfHolisticTest');
            //     if (!hasTargetName) return false;
            //     if (!portfolio.createdOn) return true; // Delete if has target name but no date
            //     const createdYear = new Date(portfolio.createdOn).getFullYear();
            //     return createdYear < 2026;
            // });

            logger.info(
                `Found ${portfoliosToDelete.length} portfolios to delete`,
            );
            logger.info(
                `Found ${holisticPortfoliosToDelete.length} holistic portfolios to delete`,
            );

            // Delete portfolios via API
            for (const portfolio of portfoliosToDelete) {
                if (!portfolio.id) continue;

                try {
                    const deleteResponse = await this.page.request.delete(
                        `${baseUrl}/api/pe/v2/portfolio/${portfolio.id}`,
                    );
                    if (deleteResponse.ok()) {
                        logger.info(
                            `Successfully deleted portfolio ${portfolio.id} with name ${portfolio.name} created on ${portfolio.createdOn}`,
                        );
                    } else {
                        logger.error(
                            `Failed to delete portfolio ${portfolio.id}: ${deleteResponse.status()}`,
                        );
                    }
                } catch (err) {
                    logger.error(
                        `Error deleting portfolio ${portfolio.id}: ${err instanceof Error ? err.message : String(err)}`,
                    );
                }
            }

            // Delete holistic portfolios via API
            for (const portfolio of holisticPortfoliosToDelete) {
                if (!portfolio.id) continue;

                try {
                    const deleteResponse = await this.page.request.delete(
                        `${baseUrl}/api/pe/v2/holisticPortfolio/${portfolio.id}`,
                    );
                    if (deleteResponse.ok()) {
                        logger.info(
                            `Successfully deleted holistic portfolio ${portfolio.id} with name ${portfolio.name} created on ${portfolio.createdOn}`,
                        );
                    } else {
                        logger.error(
                            `Failed to delete holistic portfolio ${portfolio.id}: ${deleteResponse.status()}`,
                        );
                    }
                } catch (err) {
                    logger.error(
                        `Error deleting holistic portfolio ${portfolio.id}: ${err instanceof Error ? err.message : String(err)}`,
                    );
                }
            }
        } catch (err) {
            logger.error(
                `Error in deleteAllPortfolios: ${err instanceof Error ? err.message : String(err)}`,
            );
        }
    }

    /**
     * Validate that a canvas element has rendered content
     * @param canvas - The canvas locator to validate
     * @returns Promise<boolean> - True if canvas has rendered content, false otherwise
     */
    async validateCanvas(canvas: Locator): Promise<boolean> {
        const hasRenderedContent = await canvas.evaluate(
            (el: HTMLCanvasElement) => {
                if (!el) return false;
                const ctx = el.getContext("2d");
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
            },
        );
        return hasRenderedContent;
    }

    /**
     * Verify a proposal section by clicking the element and validating its content
     * Ensures the content is visually enabled (not greyed out) and contains data
     * @param clickElement - The element to click (trigger/header)
     * @param content - The content locator to verify (canvas or HTML content)
     * @returns Promise<boolean> - True if section is verified and enabled
     * @throws Error if element is not visible or disabled
     */
    async verifyProposalSection(
        clickElement: Locator,
        content: Locator,
        checkBox?: Locator,
    ): Promise<boolean> {
        try {
            const sectionName = await clickElement
                .evaluate((el) => (el.textContent || "").trim())
                .catch(() => "Unknown section");
            //click into pdf section
            await clickElement.click();
            // ensure we actually have the checkbox locator
            if (checkBox) {
                // get current state (await!)
                const currentlyChecked = await checkBox
                    .isChecked()
                    .catch(() => false);

                if (!currentlyChecked) {
                    await checkBox.check();
                }
            }
            // Retry canvas validation a few times to allow client-side rendering
            const attempts = 3;
            for (let i = 0; i < attempts; i++) {
                const valid = await this.validateCanvas(content).catch(
                    () => false,
                );
                if (valid) {
                    return true;
                }
                // small backoff between attempts
                await this.page
                    .locator("body")
                    .evaluate(
                        (_, delayMs) =>
                            new Promise((resolve) =>
                                setTimeout(resolve, delayMs),
                            ),
                        200 + i * 100,
                    );
            }

            // Check parent containers for a 'fainted' class after canvas retries
            const parentClass = await content
                .evaluate((el: Element) => {
                    const parent =
                        el.closest(".page-component") ||
                        el.closest(".page-wrap") ||
                        el.parentElement;
                    return parent ? parent.className || "" : "";
                })
                .catch(() => "");

            if (
                typeof parentClass === "string" &&
                parentClass.includes("fainted")
            ) {
                // If the parent container has a 'fainted' class, it is likely greyed out/disabled
                const failureMessage = `Section appears to not be selected: ${sectionName}`;
                logger.warn(failureMessage);
                throw new Error(failureMessage);
            }

            // If we reached here, canvas didn't contain rendered pixels
            const failureMessage = `Canvas content validation failed for section: ${sectionName}`;
            logger.warn(failureMessage);
            throw new Error(failureMessage);
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            logger.warn(`verifyProposalSection error: ${message}`);
            throw err;
        }
    }
}
