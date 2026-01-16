import { test as base, createBdd } from 'playwright-bdd';
import { expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPageObjectModel';
import { SwitchIDPage } from '../pages/SwitchIDPageObjectModel';
import { PortfolioEnginePage } from '../pages/PortfolioEngineObjectModel';
import { EwmPage } from '../pages/ewmPageObjectModel';
import { loadEnvironment } from '../utils/env-loader';

// Load environment variables
loadEnvironment();

type Fixtures = {
    loginPage: LoginPage;
    switchIDPage: SwitchIDPage;
    portfolioEnginePage: PortfolioEnginePage;
    ewmPage: EwmPage;
};

export const test = base.extend<Fixtures>({
    loginPage: async ({ page }, use) => {
        await use(new LoginPage(page));
    },

    switchIDPage: async ({ page }, use) => {
        await use(new SwitchIDPage(page));
    },

    portfolioEnginePage: async ({ page }, use) => {
        await use(new PortfolioEnginePage(page));
    },

    ewmPage: async ({ page }, use) => {
        await use(new EwmPage(page));
    },
});

// Export BDD helpers
export const { Given, When, Then, Before, After } = createBdd(test);

export { expect };