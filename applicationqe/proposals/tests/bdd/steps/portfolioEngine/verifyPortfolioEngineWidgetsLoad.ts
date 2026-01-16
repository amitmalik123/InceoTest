import { When, Then } from '../../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import { portfolioEnginePageInstance } from './addStrategiesToPortfolio';

When('I enable all Portfolio Engine widgets', async () => {
    console.log('\nEnabling all widgets');
    await portfolioEnginePageInstance.selectAllWidgetsIfNeeded();
});

Then('the Portfolio Engine widgets should load successfully', async () => {
    // Verify all widget headers are loaded
    console.log('\nVerifying widget headers are visible');
    await expect(portfolioEnginePageInstance.upsideDownsideCaptureHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.investmentApproachHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.returnByStrategyHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.stressTestHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.assetAllocationHoldingsHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.riskVsReturnHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.summaryStatisticsHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.drawdownHeader).toBeVisible({ timeout: 300000 });
    await expect(portfolioEnginePageInstance.performanceHeader).toBeVisible({ timeout: 300000 });

    // Verify all widgets have content loaded
    console.log('\nWaiting for all widgets to load content (this may take some time)');

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
        { name: 'Return by Strategy', locator: portfolioEnginePageInstance.returnByStrategyGraphContent }
    ];

    // Expect each widget to have content loaded
    for (const widget of widgetsToVerify) {
        console.log(`  Waiting for ${widget.name} to load content...`);
        await expect(widget.locator.first()).toBeVisible({ timeout: 20 * 60 * 1000 }); // Long timeout due to slow loads
    }

    console.log('\nAll widgets finished loading');
});
