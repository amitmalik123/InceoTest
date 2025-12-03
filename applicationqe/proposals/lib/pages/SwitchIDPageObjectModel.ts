import { type Locator, type Page } from '@playwright/test';
import { selectIfVisible } from '@helperfunctions/selectIfVisible'

export class SwitchIDPage {
    readonly page: Page;
    readonly idInput: Locator;
    readonly userIDLink: Locator;
    readonly roleRadioButton: Locator;
    readonly continueButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.idInput = page.locator('#ctl00_cphContentArea_txtLookUp');
        this.userIDLink = page.getByRole('link', { name: process.env.advisorID });
        this.roleRadioButton = page.locator('#radAgents');
        this.continueButton = page.getByRole('button', { name: 'Continue' });
    }

    //Switch role from eWm pages
    async gotoSwitchIDPage() {
        await this.page.getByRole('link', { name: 'Switch ID' }).click();
        await this.page.waitForLoadState('networkidle');
    }


    //Switch ID to advisor
    async selectID(advisorId: string) {
        await this.gotoSwitchIDPage();
        await this.idInput.click();
        await this.idInput.fill(advisorId);
        await this.idInput.press('Enter');
        await this.page.waitForLoadState('networkidle');
        await this.userIDLink.click();
        await this.page.waitForLoadState('networkidle');
        await selectIfVisible(this.roleRadioButton);
        await selectIfVisible(this.continueButton);
        await this.page.waitForLoadState('networkidle');
    }
}
