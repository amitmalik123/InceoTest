import { test as teardown } from '@playwright/test';
import { navigateToHomePage } from '../../helperfunctions/navigateToHomePage';
import { navigateToPortfolioEngine } from '../../helperfunctions/navigateToPortfolioEngine';
import { PortfolioEnginePage } from '../../pages/PortfolioEngineObjectModel';
import { logger } from '../../utils/logger';
import { cleanupDownloads } from '../../utils/pdfUtils';

import { deleteTestClient } from './steps/shared/clientCleanupHelper';

teardown.describe('Teardown', () => {
    teardown.use({ storageState: './authfiles/role1.json' });

    teardown('Delete Test Portfolio', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePage = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        //await portfolioEnginePage.deleteAllPortfolios(); // uncomment this line to do bulk cleanup, comment out remaining lines
        logger.debug('\nDeleting Test Portfolios...');

        // Dismiss privacy dialog
        await portfolioEnginePage.dismissPrivacyDialog();

        await Promise.race([
            portfolioEnginePage.getStartedButton.waitFor({ state: 'visible' }),
            portfolioEnginePage.managePortfoliosButton.waitFor({ state: 'visible' }),
        ]);
        if (await portfolioEnginePage.getStartedButton.isVisible()) {
            logger.debug('No portfolios to delete');
            return;
        } else if (await portfolioEnginePage.managePortfoliosButton.isVisible()) {
            await portfolioEnginePage.managePortfoliosButton.click();
            await portfolioEnginePage.deletePortfolio(['Widget Test Portfolio', 'E2E Test Portfolio']);
            logger.debug('Portfolios deleted');
        }
    });

    teardown('Delete Test Client', async ({ page }) => {
        await navigateToHomePage(page);
        const portfolioEnginePageInstance = new PortfolioEnginePage(await navigateToPortfolioEngine(page));
        //await portfolioEnginePage.deleteAllPortfolios(); // uncomment this line to do bulk cleanup, comment out remaining lines
        logger.debug('\nDeleting Test Clients...');

        // Dismiss privacy dialog
        await portfolioEnginePageInstance.dismissPrivacyDialog();

        await deleteTestClient(portfolioEnginePageInstance, ['Guy NAWE2E', 'Guy PeE2E', 'Guy NAWTMS']);
    });

    teardown('Clean up downloads folder', async () => {
        logger.debug('\nCleaning up downloads folder...');
        cleanupDownloads();
    });
});
