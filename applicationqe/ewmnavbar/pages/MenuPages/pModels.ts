import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ModelsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly hModels: Locator;
    readonly btnCreateModel: Locator;
    readonly btnPublished: Locator;
    readonly btnDrafts: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hModels = page.locator('h1[class*="pageHeader"]:has-text("Models")');
        this.btnCreateModel = page.getByRole('button', { name: 'Create Model', exact: true });
        this.btnPublished = page.getByRole('button', { name: 'Published', exact: true });
        this.btnDrafts = page.getByRole('button', { name: 'Drafts', exact: true });
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/modelmgmt');
        await this.fElement.log('Navigating to Models Page');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hModels, 'Models Header');
        await this.fElement.log('✅ Landed on Page: Models');
    }

    async ElementsExist() {
        await this.fElement.log('📢 Verifying Models Page Elements...');

        await this.fElement.elemVisible(this.hModels, 'heading Models');
        await this.fElement.elemVisible(this.btnCreateModel, 'button Create Model');
        await this.fElement.elemVisible(this.btnPublished, 'button Published');
        await this.fElement.elemVisible(this.btnDrafts, 'button Drafts');

        await this.fElement.log('✅ All Models page elements are visible.');
    }
}