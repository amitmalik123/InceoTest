import { navigateToHomePage } from '@helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '@helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../pages/PortfolioEngineObjectModel';
import { EwmPage } from '../pages/ewmPageObjectModel';
import { test as teardown, expect } from '@playwright/test';

teardown.describe.configure({ mode: 'default' });

teardown.describe('Delete Portfolio', () => {
    teardown.use({ storageState: './authfiles/role1.json' });
    /*Move to teardown to ensure cleanup happens even if a test fails*/
    teardown('Cleanup - Delete created portfolio', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        await portfolioEnginePage.managePortfoliosButton.click();
        await portfolioEnginePage.deletePortfolio();

    });
});

teardown.describe('Delete Client', () => {
    teardown.use({ storageState: './authfiles/role1.json' });
    /*Move to teardown to ensure cleanup happens even if a test fails*/
    teardown('Cleanup - Delete created client', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(page);
        await portfolioEnginePage.searchForClient('guy dude');
        await portfolioEnginePage.deleteClient('guy dude')

    });
});


teardown.describe('Logout', () => {
    //apply storage state of role from auth file created in setup
    teardown.use({ storageState: './authfiles/role1.json' });
    teardown('Logout', async ({ page }) => {
        //logout
        await navigateToHomePage(page);
        const ewmPage = new EwmPage(page);
        await ewmPage.logout();
    });
});