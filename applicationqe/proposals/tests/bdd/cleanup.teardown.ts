import { test as teardown } from '@playwright/test';
import { navigateToHomePage } from '../../helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '../../helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../../pages/PortfolioEngineObjectModel';

teardown.describe('Teardown', () => {
    teardown.use({ storageState: './authfiles/role1.json' });

    teardown('Delete E2E Test Portfolio', async ({ page }) => {
        console.log('\nDeleting E2E Test Portfolios...');

        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        await portfolioEnginePage.managePortfoliosButton.click();
        await portfolioEnginePage.deletePortfolio();

        console.log('Portfolios deleted');
    });

    teardown('Delete E2E Test Clients', async ({ page }) => {
        console.log('\nDeleting test clients...');

        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(page);

        // First check if any clients exist
        let totalItems = await portfolioEnginePage.searchForClient('guy dude', 0);

        if (totalItems === 0) {
            console.log('No test clients found to delete');
            return;
        }

        let index = 0;
        while (index < totalItems) {
            // Search and delete, incrementing index since deleted clients remain visible in search
            totalItems = await portfolioEnginePage.searchForClient('guy dude', index);

            if (index < totalItems) {
                await portfolioEnginePage.deleteClientLink.waitFor({ state: 'visible', timeout: 5000 });
                await portfolioEnginePage.deleteClient();
                index++;
            } else {
                break; // No more clients to delete
            }
        }

        console.log('All test clients deleted');
    });
});
