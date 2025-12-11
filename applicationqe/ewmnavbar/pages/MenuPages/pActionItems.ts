
import { expect, type Locator, type Page } from "@playwright/test";
import { getImage } from '../../helper/getImage';
import { elemVisible, clickButton, typeinField, textExists, elemHasAttribute } from '../../functions/fElementHelper';
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

        this.hActionItems = page.locator('h1.pageHeader', { hasText: 'Action Items' });
        this.smNeedsAction = page.getByRole('link', { name: 'Needs Action' });
        this.smOpenItems = page.getByRole('link', { name: 'Open Items' });
        this.smClosed = page.getByRole('link', { name: 'Closed' });
        this.txtNeedsAction = page.locator('.MuiBadge-badge.MuiBadge-colorError');
    }


    async goToPage() {
        await this.page.goto('/trackingcenter');
        this.logger && await this.logger('Going to main menu page - Action Items');
    }


    async LoadsPage() {
        await elemVisible(this.hActionItems, 'Action Items Header', this.logger, 100000);
        this.logger && await this.logger('Landed on Page Action Items');
    }


    async SubMenusExist() {
        await elemVisible(this.smNeedsAction, 'Needs Action Submenu', this.logger);
        await elemVisible(this.smOpenItems, 'Open Items Submenu', this.logger);
        await elemVisible(this.smClosed, 'Closed Submenu', this.logger);
    }


    async getItemsCount() {
        await elemVisible(this.txtNeedsAction, 'Needs Action Bubble', this.logger);
        const text = await this.txtNeedsAction.textContent();
        if (!text) {
            this.logger && await this.logger('❌ Bubble element content is empty or null.');
            throw new Error("Bubble element content is empty or null.");
        }
        return parseInt(text.trim(), 10);
    }
}
