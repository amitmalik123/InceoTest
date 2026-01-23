import { test as teardown } from '@playwright/test';
import { navigateToHomePage } from '../../helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '../../helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../../pages/PortfolioEngineObjectModel';
import { logger } from '../../utils/logger';

teardown.describe('Teardown', () => {
    teardown.use({ storageState: './authfiles/role1.json' });

    teardown('Delete Test Portfolio', async ({ page }) => {
        logger.debug('\nDeleting Test Portfolios...');

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

    teardown('Delete Test Clients', async ({ page }) => {
        logger.debug('\nDeleting Test Clients...');
        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(page);
        // deleting pe e2e client
        await portfolioEnginePage.searchForClient('guy dude');
        await portfolioEnginePage.clientCollapsedLink.nth(0).click();
        await portfolioEnginePage.deleteClient();
        logger.debug('All test clients deleted');
    });
});
