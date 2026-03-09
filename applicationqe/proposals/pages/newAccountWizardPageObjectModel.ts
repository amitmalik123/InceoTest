import { type Locator, type Page } from '@playwright/test';

export class NewAccountWizardPage {
    readonly page: Page;

    // Dropdowns
    readonly agentDropdown: Locator;
    readonly clientTypeDropdown: Locator;
    readonly registrationTypeDropdown: Locator;
    readonly selectCustodianDropdown: Locator;
    readonly accountTypeDropdown: Locator;

    // Textboxes
    readonly firstNameInput: Locator;
    readonly lastNameInput: Locator;
    readonly registrationNameInput: Locator;
    readonly investmentAmountInput: Locator;
    readonly advFlatFeeInput: Locator;
    readonly percentLabelsInputs: Locator;

    // Fiduciary radios
    readonly fiduciaryRadios: Locator; // group locator
    readonly fiduciaryDiscretionary: Locator;
    readonly fiduciaryNonDiscretionary: Locator;

    //  profile radios
    readonly ProfileRadios: Locator;
    readonly Conservative: Locator;
    readonly ModerateConservative: Locator;
    readonly Moderate: Locator;
    readonly ModerateGrowth: Locator;
    readonly Growth: Locator;
    readonly MaximumGrowth: Locator;

    //Risk return profile radios
    readonly conservativeRiskReturnRadio: Locator;
    readonly moderateConservativeRiskReturnRadio: Locator;
    readonly moderateRiskReturnRadio: Locator;
    readonly moderateGrowthRiskReturnRadio: Locator;
    readonly growthRiskReturnRadio: Locator;
    readonly maximumGrowthRiskReturnRadio: Locator;

    // Risk Assessment radios
    readonly lowRiskRadio: Locator;
    readonly moderateRiskRadio: Locator;
    readonly highRiskRadio: Locator;
    readonly veryHighRiskRadio: Locator;
    readonly twoYearsOrLessRadio: Locator;
    readonly threeToFiveYearsRadio: Locator;
    readonly sixToNineYearsRadio: Locator;
    readonly tenYearsPlusRadio: Locator;
    readonly over75PercentRadio: Locator;
    readonly fiftyTo75PercentRadio: Locator;
    readonly twentyFiveTo50PercentRadio: Locator;
    readonly lessThan25PercentRadio: Locator;

    // Links & Buttons
    readonly riskToleranceQuestionnaireLink: Locator;
    readonly backButton: Locator;
    readonly nextButton: Locator;
    readonly confirmButton: Locator;
    readonly tmsOptionsYes: Locator;
    readonly tmsOptionsNo: Locator;
    readonly promptLeaveNoButton: Locator;
    readonly promptLeaveYesButton: Locator;
    readonly addInvestmentButton: Locator;
    readonly reviewButton: Locator;

    // Strategy rows
    readonly coreStrategyRow: Locator;
    readonly tacticalEnhancedStrategyRow: Locator;
    readonly tacticalLimitStrategyRow: Locator;
    readonly diversifyingEquityStrategyRow: Locator;
    readonly diversifyingBondStrategyRow: Locator;

    // Portfolio summary widget
    readonly assetAllocationSummaryWidget: Locator;
    readonly coreMarketsSection: Locator;
    readonly tacEnhancedSection: Locator;
    readonly tacLimitSection: Locator;
    readonly divEquitySection: Locator;
    readonly divBondsSection: Locator;
    readonly additionalInvestmentsSection: Locator;

    // Portfolio fee summary table
    readonly portfolioFeeSummaryTable: Locator;
    readonly financialAdvisorFeeRow: Locator;
    readonly platformFeeRow: Locator;
    readonly taxManagementServicesFeeRow: Locator;
    readonly portfolioTotalValueRow: Locator;
    readonly totalFeeRow: Locator;

    constructor(page: Page) {
        this.page = page;

        // Dropdowns
        this.agentDropdown = page.locator('#ctl00_cphContentArea_ddlAgentID');
        this.clientTypeDropdown = page.locator('#ctl00_cphContentArea_ddlClientType');
        // Custom dropdowns - prefer stable ID-based locators scoped to containers
        this.registrationTypeDropdown = page.locator('#registration_container #registration_type_dropdown');
        this.selectCustodianDropdown = page.locator('#registration_custodian');
        this.accountTypeDropdown = page.locator('#account_type_partial_container #account_type_dropdown');

        // Name Textboxes
        // Use stable IDs present in the DOM rather than role-based labels
        this.firstNameInput = page.locator('#ctl00_cphContentArea_txtFirstName');
        this.lastNameInput = page.locator('#ctl00_cphContentArea_txtLastName');
        this.registrationNameInput = page.locator('#registrationName');
        this.investmentAmountInput = page.locator('#AccountSectionInvestmentAmount');
        this.advFlatFeeInput = page.locator('#advFlatFee');
        this.percentLabelsInputs = page.locator('input[name="percentsLabels"]');

        // Fiduciary radios
        this.fiduciaryDiscretionary = page.getByRole('cell', { name: 'Discretionary', exact: true });
        this.fiduciaryNonDiscretionary = page.getByRole('cell', { name: 'Non-Discretionary', exact: true });

        // Risk return profile radios (use label text for reliable matching)
        this.conservativeRiskReturnRadio = page.getByLabel('1-Conservative');
        this.moderateConservativeRiskReturnRadio = page.getByLabel('2-Moderate Conservative');
        this.moderateRiskReturnRadio = page.getByLabel('3-Moderate');
        this.moderateGrowthRiskReturnRadio = page.getByLabel('4-Moderate Growth');
        this.growthRiskReturnRadio = page.getByLabel('5-Growth');
        this.maximumGrowthRiskReturnRadio = page.getByLabel('6-Maximum Growth');
        // Risk assessment radio buttons
        this.lowRiskRadio = page.locator('[id="336"]');
        this.moderateRiskRadio = page.locator('[id="337"]');
        this.highRiskRadio = page.locator('[id="338"]');
        this.veryHighRiskRadio = page.locator('[id="339"]');
        this.twoYearsOrLessRadio = page.locator('[id="340"]');
        this.threeToFiveYearsRadio = page.locator('[id="341"]');
        this.sixToNineYearsRadio = page.locator('[id="342"]');
        this.tenYearsPlusRadio = page.locator('[id="343"]');
        this.over75PercentRadio = page.locator('[id="344"]');
        this.fiftyTo75PercentRadio = page.locator('[id="345"]');
        this.twentyFiveTo50PercentRadio = page.locator('[id="346"]');
        this.lessThan25PercentRadio = page.locator('[id="347"]');

        this.riskToleranceQuestionnaireLink = page.getByRole('link', { name: 'Risk Tolerance Questionnaire' });
        this.backButton = page.getByRole('button', { name: 'Back' });
        this.nextButton = page.getByRole('button', { name: 'Next' });
        this.confirmButton = page.getByRole('button', { name: 'Confirm' });
        this.tmsOptionsNo = page.locator('#tmsOptionsNo');
        this.tmsOptionsYes = page.locator('#tmsOptionsYes');
        this.reviewButton = page.getByRole('button', { name: 'Review' });

        //Investment Section Buttons
        this.addInvestmentButton = page.getByRole('button', { name: 'Add Investment' });

        // Strategy rows
        this.coreStrategyRow = page.locator('#Core');
        this.tacticalEnhancedStrategyRow = page.locator('#TacticalEnhanced');
        this.tacticalLimitStrategyRow = page.locator('#TacticalLimit');
        this.diversifyingEquityStrategyRow = page.locator('#DiversifyingEquity');
        this.diversifyingBondStrategyRow = page.locator('#DiversifyingBond');

        // Portfolio summary widget
        this.assetAllocationSummaryWidget = page.locator('#asset-allocation-summary-widget');
        this.coreMarketsSection = this.assetAllocationSummaryWidget.locator(
            '.asset-class:has(span:has-text("Core Markets"))'
        );
        this.tacEnhancedSection = this.assetAllocationSummaryWidget.locator(
            '.asset-class:has-text("Enhanced Return Focus")'
        );
        this.tacLimitSection = this.assetAllocationSummaryWidget.locator('.asset-class:has-text("Limit Loss Focus")');
        this.divEquitySection = this.assetAllocationSummaryWidget.locator(
            '.asset-class:has-text("Equity Alternatives")'
        );
        this.divBondsSection = this.assetAllocationSummaryWidget.locator('.asset-class:has-text("Bonds")');
        this.additionalInvestmentsSection = this.assetAllocationSummaryWidget.locator(
            '.asset-class:has-text("Additional Investments")'
        );

        // Portfolio fee summary table (use specific selector to avoid matching outer table)
        this.portfolioFeeSummaryTable = page.locator('#feeSummaryTable .portfolioFeeSummaryTbl');
        this.financialAdvisorFeeRow = this.portfolioFeeSummaryTable.locator('tr:has(td:has-text("Financial Advisor"))');
        this.platformFeeRow = this.portfolioFeeSummaryTable.locator('tr:has(td:has-text("Platform"))');
        this.taxManagementServicesFeeRow = this.portfolioFeeSummaryTable.locator('tr:has(td:has-text("Tax Management Services"))');
        this.portfolioTotalValueRow = this.portfolioFeeSummaryTable.locator('tr:has(td.portfolioFeeTotalData)');
        this.totalFeeRow = this.portfolioFeeSummaryTable.locator(
            'tr:has(td.portfolioAnnualColumnLabel:has-text("Total"))'
        );
    }

    /**
     * Select a registration type from the multilevel dropdown
     * @param registrationType - The specific registration type to select (e.g., 'Individual', 'Traditional IRA', 'Trust')
     */
    async selectRegistrationType(registrationType: string): Promise<void> {
        // Map of registration types to their parent categories for nested options
        const categoryMap: { [key: string]: string } = {
            Individual: 'Individual',
            'Individual TOD': 'Individual',
            Trust: 'Trust',
            'Community Property': 'Joint',
            'Community Property with Rights of Survivorship': 'Joint',
            'Community Property with Rights of Survivorship TOD': 'Joint',
            'Joint Tenant with Rights of Survivorship': 'Joint',
            'Joint Tenant with Rights of Survivorship TOD': 'Joint',
            'Tenants in Common': 'Joint',
            'Tenants by Entirety': 'Joint',
            'Tenants by Entirety TOD': 'Joint',
            'Traditional IRA': 'IRAs',
            'Rollover IRA': 'IRAs',
            'Roth IRA': 'IRAs',
            'SEP-IRA': 'IRAs',
            'Simple IRA': 'IRAs',
            'Beneficiary IRA Individual': 'IRAs',
            'Beneficiary Roth IRA Individual': 'IRAs',
            'Beneficiary IRA Trust': 'IRAs',
            'Beneficiary Roth IRA Trust': 'IRAs',
            '401(k)': 'RetirementPlans',
            'Individual 401(k)': 'RetirementPlans',
            '403(b) Plan': 'RetirementPlans',
            'Defined Benefit Pension Plan': 'RetirementPlans',
            'Money Purchase Pension Plan': 'RetirementPlans',
            'Profit Sharing Plan': 'RetirementPlans',
            'Self-Directed Brokerage Account': 'RetirementPlans',
            'Self-Directed Brokerage Account - 403(b)': 'RetirementPlans',
            Corporation: 'BusinessAccounts',
            'Limited Liability Company': 'BusinessAccounts',
            Partnership: 'BusinessAccounts',
            'Sole Proprietor': 'BusinessAccounts',
            'Sub-Custodian FBO': 'BusinessAccounts',
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

        // Click the main dropdown to open it
        await this.registrationTypeDropdown.click();

        // Hover the parent category to expand it
        const parentCategory = this.registrationTypeDropdown.locator(`dt.groupedmenu a[data-group-name="${category}"]`);
        await parentCategory.hover();

        // Click the specific nested option
        const nestedOption = this.registrationTypeDropdown.locator(
            `ul#${category} li[data-name="${registrationType}"]`
        );
        await nestedOption.click();
    }

    /**
     * Select a random custodian from the dropdown
     */
    async selectCustodian(): Promise<void> {
        const dropdownTrigger = this.selectCustodianDropdown.locator('dt.firstmenu a');
        const optionSelector = '#registration_custodian dd dl dd a';
        const options = this.selectCustodianDropdown.locator('dd dl dd a');

        // Wait for the dropdown container to exist and be visible
        await this.selectCustodianDropdown.waitFor({ state: 'visible' });

        // Wait for option elements to be present in the DOM (dropdown can't be clicked until registration type is selected, so this ensures the dropdown is ready)
        await this.page.waitForFunction(sel => document.querySelectorAll(sel).length > 0, optionSelector);

        // Now open the dropdown and wait for the options to become visible
        await dropdownTrigger.click();
        await options.first().waitFor({ state: 'visible' });

        // Get count and select random option
        const count = await options.count();
        const randomIndex = Math.floor(Math.random() * count);
        await options.nth(randomIndex).click();
    }

    /**
     * Select an account type from the multilevel dropdown
     * @param accountType - The account type to select (e.g., 'GPS Fund Strategies', 'Single Strategy Account', 'Savos Personal Portfolio Custom')
     */
    async selectAccountType(accountType: string): Promise<void> {
        const dropdownTrigger = this.accountTypeDropdown.locator('dt.firstmenu a');
        const optionSelector = '#account_type_partial_container #account_type_dropdown dd a';
        const options = this.accountTypeDropdown.locator('dd a');

        // Wait for the dropdown container to exist
        await this.accountTypeDropdown.waitFor({ state: 'visible' });

        // Wait for option elements to appear in the DOM (they may be initialized later)
        await this.page.waitForFunction(sel => document.querySelectorAll(sel).length > 0, optionSelector);

        // Open the dropdown and wait for options to be visible
        await dropdownTrigger.click();
        await options.first().waitFor({ state: 'visible' });

        // Find the matching option and click it
        const option = this.accountTypeDropdown.locator(`dd a`).filter({ hasText: accountType });
        if ((await option.count()) === 0) {
            throw new Error(`Account type option with text "${accountType}" not found`);
        }
        await option.first().click();
    }

    /**
     * Fill the registration name field
     * @param name - The registration name to enter
     */
    async fillRegistrationName(name: string): Promise<void> {
        await this.registrationNameInput.fill(name);
    }

    /**
     * Fill the investment amount field
     * @param amount - The investment amount (can be string or number)
     */
    async fillInvestmentAmount(amount: string): Promise<void> {
        await this.investmentAmountInput.fill(amount);
    }

    async fillName(first: string, last: string): Promise<void> {
        await this.firstNameInput.fill(first);
        await this.lastNameInput.fill(last);
    }

    /**
     * Add a strategy to the account by searching and selecting it
     * @param strategyName - The name of the strategy to search for and add
     */
    async addStrategy(strategyName: string): Promise<void> {
        // Click the Add Investment button
        await this.addInvestmentButton.click();

        // Fill in the search field and press Enter
        const searchBox = this.page.getByRole('textbox', { name: 'Search solution type or' });
        await searchBox.fill(strategyName);
        await searchBox.press('Enter');

        // Click the first matching result cell
        const resultCell = this.page.getByRole('cell', { name: strategyName });
        await resultCell.click();
        await this.page.getByRole('button', { name: 'Ok' }).click();

        // Move mouse slowly accross screen to re-enable the add investments button after closing the pop-up window
        const box = await this.addInvestmentButton.boundingBox();
        if (box) {
            const targetX = box.x + box.width / 2;
            const targetY = box.y + box.height / 2;

            // Move from top-left to the button gradually
            const startX = 0;
            const startY = 0;
            const steps = 20; // Increase steps for slower movement

            for (let i = 0; i <= steps; i++) {
                const progress = i / steps;
                const currentX = startX + (targetX - startX) * progress;
                const currentY = startY + (targetY - startY) * progress;
                await this.page.mouse.move(currentX, currentY);
                await this.page.waitForTimeout(10); // Small delay between steps for slower speed
            }
        }
    }
}

export default NewAccountWizardPage;
