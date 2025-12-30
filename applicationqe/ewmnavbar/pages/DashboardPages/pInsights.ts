import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class InsightsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation & Tabs ---
    readonly smInsightsHL: Locator;
    readonly tabAssetsHL: Locator;
    readonly tabFees: Locator;
    readonly tabFlows: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.smInsightsHL = page.locator('a.active', { hasText: 'Insights' });
        
        this.tabAssetsHL = page.locator('[role="tab"][aria-selected="true"]').filter({ hasText: 'Assets' });
        this.tabFees = page.locator('[role="tab"][aria-selected="false"]').filter({ hasText: 'Fees' });
        this.tabFlows = page.locator('[role="tab"][aria-selected="false"]').filter({ hasText: 'Flows' });
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smInsightsHL, 'Insights Highlight');
        await this.fElement.log('✅ Landed on Page: Dashboard > Insights');
    }

    async ElementsExist() {
        await this.fElement.log('📢 Verifying Insights Tabs...');
        await this.fElement.elemVisible(this.tabAssetsHL, 'Assets Tab (Selected)', 15000);
        await this.fElement.elemVisible(this.tabFees, 'Fees Tab');
        await this.fElement.elemVisible(this.tabFlows, 'Flows Tab');        
        await this.fElement.log('✅ All Insights tabs are visible.');
    }
}