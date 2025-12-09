import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class ActionItemsPage {
    readonly page: Page;
    private logger: Logger;

    readonly hActionItems: Locator;
    readonly smNeedsAction: Locator;
    readonly smOpenItems: Locator;
    readonly smClosed: Locator;
    readonly txtNeedsAction: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.hActionItems = page.locator('h1[class*="pageHeader"]:has-text("Action Items")');
        this.smNeedsAction = page.getByRole('link', { name: 'Needs Action' });
        this.smOpenItems = page.getByRole('link', { name: 'Open Items' });
        this.smClosed = page.getByRole('link', { name: 'Closed' });
        this.txtNeedsAction = page.locator('.MuiBadge-badge.MuiBadge-colorError');
    }

    async goToPage() {
        await this.page.goto('/trackingcenter');
    }

    async LoadsPage() {
        await expect(this.hActionItems).toBeVisible({ timeout: 1000000 });

        console.log('on Page Action Items');
    }

    async SubMenusExist() {
        await expect(this.smNeedsAction).toBeVisible();
        await expect(this.smOpenItems).toBeVisible();
        await expect(this.smClosed).toBeVisible();
    }

    async getItemsCount() {
        await this.txtNeedsAction.waitFor({ state: 'visible' });
        const text = await this.txtNeedsAction.textContent(); // Playwright equivalent of getText()
        if (!text) {
            throw new Error("Badge element content is empty or null.");
        }
        return parseInt(text.trim(), 10);
    }
}
