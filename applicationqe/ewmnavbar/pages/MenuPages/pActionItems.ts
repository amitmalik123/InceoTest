import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ActionItemsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly hActionItems: Locator;
    readonly smNeedsAction: Locator;
    readonly smOpenItems: Locator;
    readonly smClosed: Locator;
    readonly txtNeedsAction: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hActionItems = page.locator('h1.pageHeader', { hasText: 'Action Items' });
        this.smNeedsAction = page.getByRole('link', { name: 'Needs Action' });
        this.smOpenItems = page.getByRole('link', { name: 'Open Items' });
        this.smClosed = page.getByRole('link', { name: 'Closed' });
        
        this.txtNeedsAction = page.locator('.MuiBadge-badge.MuiBadge-colorError');
    }

    async goToPage() {
        await this.fBrowser.goToURL('/trackingcenter');
        await this.fElement.log('Going to main menu page - Action Items');
    }

    async LoadsPage() {
        await this.fElement.elemVisible(this.hActionItems, 'Action Items Header', 10000); 
        await this.fElement.log('✅ Landed on Page: Action Items');
    }

    async SubMenusExist() {
        await this.fElement.elemVisible(this.smNeedsAction, 'Needs Action Submenu');
        await this.fElement.elemVisible(this.smOpenItems, 'Open Items Submenu');
        await this.fElement.elemVisible(this.smClosed, 'Closed Submenu');
    }

    async getItemsCount() {
        await this.fElement.elemVisible(this.txtNeedsAction, 'Needs Action Bubble');
        
        const text = await this.txtNeedsAction.textContent();
        if (!text) {
            const msg = '❌ Bubble element content is empty or null.';
            await this.fElement.log(msg);
            throw new Error(msg);
        }
        
        const count = parseInt(text.trim(), 10);
        await this.fElement.log(`ℹ️ Action Items Count: ${count}`);
        return count;
    }
}