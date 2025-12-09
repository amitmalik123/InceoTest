import { expect, type Locator, type Page } from "@playwright/test";
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
        await expect(this.hModels).toBeVisible({ timeout: 1000000 });

        console.log('on Page Models');
    }

    async ElementsExist() {
        await expect(this.hModels).toBeVisible();
        await expect(this.btnCreateModel).toBeVisible();

    }

}

