import { navigateToHomePage } from '@helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '@helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../pages/PortfolioEngineObjectModel';
import { EwmPage } from '../pages/ewmPageObjectModel';
import { test as teardown } from '@playwright/test';

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

        let totalItems = 1;
        let index = 0;
        while (totalItems > index) {
            // Increment index to move down the list since deleted clients remain visible in search
            totalItems = await portfolioEnginePage.searchForClient('guy dude', index);
            await portfolioEnginePage.deleteClientLink.waitFor({ state: 'visible' });
            await portfolioEnginePage.deleteClient();
            index++;
        }
    });
});

teardown.describe.skip('Delete All Portfolios', () => {
    teardown.use({ storageState: './authfiles/role1.json' });
    teardown('Cleanup - Delete all portfolios regardless of date', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        await portfolioEnginePage.managePortfoliosButton.click();
        await portfolioEnginePage.deleteAllPortfolios();
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
