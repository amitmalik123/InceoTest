import { When } from '../../../../fixtures/fixtures';
import { logger } from '../../../../utils/logger';
import { PortfolioEnginePage } from '@pages/PortfolioEngineObjectModel';
import NewAccountWizardPage from '@pages/newAccountWizardPageObjectModel';
import { EwmPage } from '@pages/ewmPageObjectModel';

// Export pom instance so all steps can use it
export let portfolioEnginePageInstance: PortfolioEnginePage;
export let newAccountWizardPageInstance: NewAccountWizardPage;
export let ewmPageInstance: EwmPage;

When('I click on the Account Wizard link', async ({ page }) => {
    ewmPageInstance = new EwmPage(page);
    await ewmPageInstance.openAccountWizard();
});

When('I decide to create a new client', async ({}) => {
    await ewmPageInstance.createNewClient.click();
});

When(
    'I complete the client profile with first name {string} and last name {string}',
    async ({}, firstName: string, lastName: string) => {
        newAccountWizardPageInstance = new NewAccountWizardPage(ewmPageInstance.page);
        logger.debug('\nFilling out new client profile');

        if (newAccountWizardPageInstance.agentDropdown.isEditable()) {
            await newAccountWizardPageInstance.agentDropdown.click();
            await newAccountWizardPageInstance.selectAgent(process.env.userID);
        }
        await newAccountWizardPageInstance.fillName(firstName, lastName);
        await newAccountWizardPageInstance.fiduciaryDiscretionary.check();
        await newAccountWizardPageInstance.sixToNineYearsRadio.check();
        await newAccountWizardPageInstance.twentyFiveTo50PercentRadio.check();
        await newAccountWizardPageInstance.growthRiskReturnRadio.check();
        await newAccountWizardPageInstance.nextButton.click();
    }
);

When('make a filled to hide error', async ({ page }) => {
    await page.locator('#ctl00_cphContentArea_ddlAgentID').selectOption('AGATS8');
    await page.goto('https://test10.ewealthmanager.com/DNeWM/NBT/Profile/Profile.aspx');
    await page.locator('#ctl00_cphContentArea_txtFirstName').click();
    await page.locator('#ctl00_cphContentArea_txtFirstName').fill('guy');
    await page.locator('#ctl00_cphContentArea_txtFirstName').press('Tab');
    await page.locator('#ctl00_cphContentArea_txtLastName').fill('dude');
    await page.getByRole('radio', { name: 'Discretionary', exact: true }).check();
    await page.locator('[id="338"]').check();
    await page.locator('[id="342"]').check();
    await page.locator('[id="346"]').check();
    await page.getByText('-Growth').click();
    await page.getByRole('button', { name: 'Next' }).click();
    await page.goto('https://test10.ewealthmanager.com/Portfolio/Construct?clientId=W1Y73J');
    await page.locator('#registration_type_dropdown a').filter({ hasText: 'Select' }).click();
    await page.locator('#Individual').getByText('Individual', { exact: true }).click();
    await page.locator('a').filter({ hasText: 'AssetMark Trust' }).first().click();
    await page.getByText('Fidelity').click();
    await page
        .locator('a')
        .filter({ hasText: /^Select$/ })
        .click();
    await page.getByRole('link', { name: 'Multiple Strategy Account' }).click();
    await page.goto('https://test10.ewealthmanager.com/Portfolio/Construct?clientId=W1Y73J');
    await page.locator('#AccountSectionInvestmentAmount').click();
    await page.locator('#AccountSectionInvestmentAmount').press('ArrowRight');
    await page.getByRole('button', { name: 'Add Investment' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).fill('assetmark income builder');
    await page.getByRole('textbox', { name: 'Search solution type or' }).press('Enter');
    await page.getByRole('cell', { name: 'AssetMark Income Builder, Profile 2, Conservative' }).click();
    await page.getByRole('button', { name: 'Ok' }).click();
    await page.getByRole('button', { name: 'Add Investment' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).fill('blackrock equity');
    await page.getByRole('textbox', { name: 'Search solution type or' }).press('Enter');
    await page.getByRole('cell', { name: 'BlackRock Equity Dividend' }).click();
    await page.getByRole('button', { name: 'Ok' }).click();
    await page.getByRole('button', { name: 'Add Investment' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).fill('alphasimplex');
    await page.getByRole('textbox', { name: 'Search solution type or' }).press('Enter');
    await page.getByRole('cell', { name: 'AlphaSimplex, Alternative' }).click();
    await page.getByRole('button', { name: 'Ok' }).click();
    await page.getByRole('button', { name: 'Add Investment' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).fill('jpmorgan absolute return - profile 1');
    await page.getByRole('textbox', { name: 'Search solution type or' }).press('Enter');
    await page.getByRole('cell', { name: 'JPMorgan Absolute Return - Profile' }).click();
    await page.getByRole('button', { name: 'Ok' }).click();
    await page.getByRole('button', { name: 'Add Investment' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).click();
    await page.getByRole('textbox', { name: 'Search solution type or' }).fill('savos us risk controlled strategy');
    await page.getByRole('textbox', { name: 'Search solution type or' }).press('Enter');
    await page.getByRole('cell', { name: 'Savos US Risk Controlled' }).click();
    await page.getByRole('button', { name: 'Ok' }).click();
    await page.locator('#URIBS2_percent').click();
    await page.locator('#URIBS2_percent').fill('20');
    await page.locator('#ULKED6_percent').click();
    await page.locator('#ULKED6_percent').fill('20');
    await page.locator('#UVSTLL_percent').click();
    await page.locator('#UVSTLL_percent').fill('20');
    await page.locator('#USXAM5_percent').click();
    await page.locator('#USXAM5_percent').fill('20');
    await page.locator('#UPMAR1_percent').click();
    await page.locator('#UPMAR1_percent').fill('20');
    await page.locator('#UPMAR1_percent').press('Enter');
    await page.getByRole('button', { name: 'Review' }).click();
    await page.locator('#tmsOptionsNo').check();
    await page.getByRole('button', { name: 'Confirm' }).click();
    await page.goto('https://test10.ewealthmanager.com/Portfolio/Construct?clientId=W1Y73J');
    await page.getByRole('button', { name: 'Next' }).click();
    await page.goto('https://test10.ewealthmanager.com/AccountWizard/Fees/Index?clientId=W1Y73J');
    await page.locator('#advFlatFee').click();
    await page.locator('#advFlatFee').fill('1');
    await page.getByRole('button', { name: 'Next' }).click();
    await page.getByRole('button', { name: 'Next' }).click();
    await page.getByRole('button', { name: 'Preview Proposal' }).click();
});
