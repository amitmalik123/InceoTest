import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class InsightsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smInsightsHL: Locator;
    readonly tabAssetsHL: Locator;
    readonly tabFees: Locator;
    readonly tabFlows: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;
        this.smInsightsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Insights' });
        this.tabAssetsHL = page.locator('[role="tab"][aria-selected="true"]').filter({ hasText: 'Assets' });
        this.tabFees = page.locator('[role="tab"][aria-selected="false"]').filter({ hasText: 'Fees' });
        this.tabFlows = page.locator('[role="tab"][aria-selected="false"]').filter({ hasText: 'Flows' });

    }

    async LoadsPage() {
        await expect(this.smInsightsHL).toBeVisible({ timeout: 1000000 });
        console.log('on Landing Page Insights');
    }

    async ElementsExist() {

        await expect(this.tabAssetsHL).toBeVisible({
            timeout: 500000,
        });
        await expect(this.tabFees).toBeVisible({ timeout: 100 });
        await expect(this.tabFlows).toBeVisible({ timeout: 100 });
        await this.logger('Page loaded for Dashboard > Insights');

    }
}