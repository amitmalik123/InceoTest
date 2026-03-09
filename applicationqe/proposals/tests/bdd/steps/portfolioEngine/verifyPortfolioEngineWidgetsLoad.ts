import { When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { getPortfolioEnginePageInstance } from '../shared/instanceManager';
import { logger } from '../../../../utils/logger';

When('I enable all Portfolio Engine widgets', async () => {
    logger.debug('\nEnabling all widgets');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await portfolioEnginePageInstance.selectAllWidgetsIfNeeded();
});

Then('the Portfolio Engine widgets should load successfully', async () => {
    // Verify all widget headers are loaded
    logger.debug('\nVerifying widget headers are visible');
    const portfolioEnginePageInstance = getPortfolioEnginePageInstance();
    await expect(portfolioEnginePageInstance.upsideDownsideCaptureHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.investmentApproachHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.returnByStrategyHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.stressTestHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.assetAllocationHoldingsHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.riskVsReturnHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.summaryStatisticsHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.drawdownHeader).toBeVisible();
    await expect(portfolioEnginePageInstance.performanceHeader).toBeVisible();

    // Verify all widgets have content loaded
    logger.debug('\nWaiting for all widgets to load content (this may take some time)');

    // Define widgets to verify
    const widgetsToVerify = [
        { name: 'Investment Approach', locator: portfolioEnginePageInstance.investmentApproachGraphContent },
        { name: 'Asset Allocation', locator: portfolioEnginePageInstance.assetAllocationGraphContent },
        { name: 'Drawdown', locator: portfolioEnginePageInstance.drawdownGraphContent },
        { name: 'Summary Statistics', locator: portfolioEnginePageInstance.summaryStatisticsGraphContent },
        { name: 'Risk vs Return', locator: portfolioEnginePageInstance.riskVsReturnGraphContent },
        { name: 'Stress Test', locator: portfolioEnginePageInstance.stressTestGraphContent },
        { name: 'Upside/Downside', locator: portfolioEnginePageInstance.upsideDownsideGraphContent },
        { name: 'Performance', locator: portfolioEnginePageInstance.performanceGraphContent },
        { name: 'Return by Strategy', locator: portfolioEnginePageInstance.returnByStrategyGraphContent },
    ];

    // Expect each widget to have content loaded
    for (const widget of widgetsToVerify) {
        logger.debug(`  Waiting for ${widget.name} to load content...`);
        await expect(widget.locator.first()).toBeVisible();
    }

    logger.debug('\nAll widgets finished loading');
});
