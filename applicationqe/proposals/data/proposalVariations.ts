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
    const custodians = [
        currentPage.fidelityText,
        currentPage.assetMarkText,
        currentPage.schwabText,
        currentPage.pershingAdvisorSolutionsText,
    ];
    const randomIndex = Math.floor(Math.random() * custodians.length);
    const randomCustodian = custodians[randomIndex];
    await randomCustodian.click();
    return;
}

/**
 * Select a registration type from the dropdown, works for Portfolio Engine and New Account Wizard
 * @param currentPage - The current page object
 * @param registrationType - Category of the registration to select
 * @param registrationName - Name of the registration to enter in each category
 */
export async function selectRegistrationType(
    currentPage: ProposalPageLike,
    registrationCategory: Locator,
    registrationName: Locator
): Promise<void> {
    await currentPage.registrationTypeDropdown.click();
    const registrationCategoryText = await registrationCategory.innerText();
    const registrationNameText = await registrationName.innerText();
    switch (registrationCategoryText) {
        case 'Individual':
            if (registrationNameText === 'Individual') {
                await currentPage.individualCategory.hover();
                await currentPage.individualOption.click();
            } else if (registrationNameText === 'Individual TOD') {
                await currentPage.individualTODOption.click();
            }
            break;
        case 'Trust':
            if (registrationNameText === 'Trust') {
                await currentPage.trustOption.click();
            }
            break;
        default:
            throw new Error(`Registration Type: ${registrationCategoryText} - ${registrationNameText} is not valid`);
    }
}
