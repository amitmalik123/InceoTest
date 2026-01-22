import { type Locator, type Page } from '@playwright/test';

export class NewAccountWizardPage {
    readonly page: Page;

    // Dropdowns
    readonly agentDropdown: Locator;
    readonly clientTypeDropdown: Locator;

    // Textboxes
    readonly firstNameInput: Locator;
    readonly lastNameInput: Locator;

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
    readonly promptLeaveNoButton: Locator;
    readonly promptLeaveYesButton: Locator;

    constructor(page: Page) {
        this.page = page;

        // Dropdowns
        this.agentDropdown = page.getByRole('combobox', { name: 'Choose an Advisor' });
        this.clientTypeDropdown = page.getByRole('combobox', { name: 'Client Type' });

        // Name Textboxes
        this.firstNameInput = page.getByRole('textbox', { name: 'First' });
        this.lastNameInput = page.getByRole('textbox', { name: 'Last' });

        // Fiduciary radios
        this.fiduciaryDiscretionary = page.getByRole('radio', { name: 'Discretionary' });
        this.fiduciaryNonDiscretionary = page.getByRole('radio', { name: 'Non-Discretionary' });

        // Risk return profile radios
        this.conservativeRiskReturnRadio = page.getByRole('radio', { name: '1-Conservative' });
        this.moderateConservativeRiskReturnRadio = page.getByRole('radio', { name: '2-Moderate Conservative' });
        this.moderateRiskReturnRadio = page.getByRole('radio', { name: '3-Moderate' });
        this.moderateGrowthRiskReturnRadio = page.getByRole('radio', { name: '4-Moderate Growth' });
        this.growthRiskReturnRadio = page.getByRole('radio', { name: '5-Growth' });
        this.maximumGrowthRiskReturnRadio = page.getByRole('radio', { name: '6-Maximum Growth' });
        // Risk assessment radio buttons
        this.lowRiskRadio = page.getByRole('radio', { name: 'Low' });
        this.moderateRiskRadio = page.getByRole('radio', { name: 'Moderate' }).first();
        this.highRiskRadio = page.getByRole('radio', { name: 'High' });
        this.veryHighRiskRadio = page.getByRole('radio', { name: 'Very High' });
        this.twoYearsOrLessRadio = page.getByRole('radio', { name: '2 yrs or less' });
        this.threeToFiveYearsRadio = page.getByRole('radio', { name: '3 - 5 yrs' });
        this.sixToNineYearsRadio = page.getByRole('radio', { name: '6 - 9 yrs' });
        this.tenYearsPlusRadio = page.getByRole('radio', { name: '10 years +' });
        this.over75PercentRadio = page.getByRole('radio', { name: 'over 75 %' });
        this.fiftyTo75PercentRadio = page.getByRole('radio', { name: '50 - 75 %' });
        this.twentyFiveTo50PercentRadio = page.getByRole('radio', { name: '25 - 50 %' });
        this.lessThan25PercentRadio = page.getByRole('radio', { name: 'less than 25%' });

        this.riskToleranceQuestionnaireLink = page.getByRole('link', { name: 'Risk Tolerance Questionnaire' });
        this.backButton = page.getByRole('button', { name: 'Back' });
        this.nextButton = page.getByRole('button', { name: 'Next' });
    }

    // Small helper methods
    async selectAgent(value: string): Promise<void> {
        // Check options for matching text
        const simpleOption = this.page
            .locator('select[name="ctl00$cphContentArea$ddlAgentID"] option')
            .filter({ hasText: value });
        if ((await simpleOption.count()) > 0) {
            await simpleOption.first().click();
            return;
        }

        // // Fallback: scan the <select> options for a partial match (case-insensitive)
        // const search = value.toLowerCase();
        // const options = this.page.locator('select[name="ctl00$cphContentArea$ddlAgentID"] option');
        // const count = await options.count();
        // for (let i = 0; i < count; i++) {
        //     const opt = options.nth(i);
        //     const label = (await opt.textContent()) ?? '';
        //     const optValue = (await opt.getAttribute('value')) ?? '';
        //     if (label.toLowerCase().includes(search) || optValue.toLowerCase().includes(search)) {
        //         await this.page.locator('select[name="ctl00$cphContentArea$ddlAgentID"]').selectOption({ value: optValue });
        //         return;
        //     }
        // }

        throw new Error(`Agent option containing "${value}" not found`);
    }

    async selectClientType(value: string): Promise<void> {
        await this.clientTypeDropdown.selectOption(value);
    }

    async fillName(first: string, last: string): Promise<void> {
        await this.firstNameInput.fill(first);
        await this.lastNameInput.fill(last);
    }
}

export default NewAccountWizardPage;
