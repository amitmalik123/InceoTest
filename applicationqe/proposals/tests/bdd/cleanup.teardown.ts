import { test as teardown } from '@playwright/test';
import { navigateToHomePage } from '../../helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '../../helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../../pages/PortfolioEngineObjectModel';
import { logger } from '../../utils/logger';

teardown.describe('Teardown', () => {
    teardown.use({ storageState: './authfiles/role1.json' });

    teardown('Delete E2E Test Portfolio', async ({ page }) => {
        logger.debug('\nDeleting E2E Test Portfolios...');

        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        await Promise.race([
            portfolioEnginePage.getStartedButton.waitFor({ state: 'visible' }),
            portfolioEnginePage.managePortfoliosButton.waitFor({ state: 'visible' }),
        ]);
        if (await portfolioEnginePage.getStartedButton.isVisible()) {
            logger.debug('No portfolios to delete');
            return;
        } else if (await portfolioEnginePage.managePortfoliosButton.isVisible()) {
            await portfolioEnginePage.managePortfoliosButton.click();
            await portfolioEnginePage.deletePortfolio();
            logger.debug('Portfolios deleted');
        }
    });

    teardown('Delete E2E Test Clients', async ({ page }) => {
        logger.debug('\nDeleting test clients...');

        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(page);

        // First check if any clients exist
        let totalItems = await portfolioEnginePage.searchForClient('guy dude', 0);

        if (totalItems === 0) {
            logger.debug('No test clients found to delete');
            return;
        }

        let index = 0;
        while (index < totalItems) {
            if (index < totalItems) {
                await portfolioEnginePage.deleteClientLink.waitFor({ state: 'visible' });
                await portfolioEnginePage.deleteClient();
                index++;
                if (index < totalItems) {
                    totalItems = await portfolioEnginePage.searchForClient('guy dude', index);
                }
            } else {
                break; // No more clients to delete
            }
        }

        logger.debug('All test clients deleted');
    });
});
