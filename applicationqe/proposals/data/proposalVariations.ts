import { Locator } from '@playwright/test';

// Interface for page objects used by these helpers
interface ProposalPageLike {
    selectCustodianDropdown: Locator;
    fidelityText: Locator;
    assetMarkText: Locator;
    schwabText: Locator;
    pershingAdvisorSolutionsText: Locator;

    registrationTypeDropdown?: Locator;
    individualCategory?: Locator;
    individualOption?: Locator;
    individualTODOption?: Locator;
    trustOption?: Locator;
}

/**
 * Select a custodian from the dropdown, works for Portfolio Engine and New Account Wizard
 * @param currentPage - The current page object
 * @param custodian - Name of the custodian to select
 */
export async function selectCustodian(currentPage: ProposalPageLike): Promise<void> {
    await currentPage.selectCustodianDropdown.click();

    // Define valid custodians (excludes "Select" placeholder)
    const custodians = [
        currentPage.fidelityText,
        currentPage.assetMarkText,
        currentPage.schwabText,
        currentPage.pershingAdvisorSolutionsText,
    ];

    // Filter to only visible custodians (in case some flows don't have all options)
    const visibleCustodians = [];
    for (const custodian of custodians) {
        if (await custodian.isVisible()) {
            visibleCustodians.push(custodian);
        }
    }

    // Select random visible custodian
    const randomIndex = Math.floor(Math.random() * visibleCustodians.length);
    await visibleCustodians[randomIndex].click();
}
