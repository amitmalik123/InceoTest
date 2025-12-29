
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class ModelsPage {
    readonly page: Page;
    private logger: Logger;

    readonly hModels: Locator;
    readonly btnCreateModel: Locator;
    readonly btnPublished: Locator;
    readonly btnDrafts: Locator;
    // readonly smOne: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.hModels = page.locator('h1[class*="pageHeader"]:has-text("Models")');
        this.btnCreateModel = page.getByRole('button', { name: 'Create Model', exact: true });
        this.btnPublished = page.getByRole('button', { name: 'Published', exact: true });
        this.btnDrafts = page.getByRole('button', { name: 'Drafts', exact: true });

    }

    async goToPage() {
        await this.page.goto('/modelmgmt');
    }

    async LoadsPage() {
        await elemVisible(this.hModels, 'Models Header', this.logger, 1000000);
        console.log('on Page Models');
    }

    async ElementsExist() {
        await elemVisible(this.hModels, 'heading Models', this.logger);
        await elemVisible(this.btnCreateModel, 'button Create Model', this.logger);
    }

}

