import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class SavosPage {
    readonly page: Page;
    private logger: Logger;

    readonly smSavosHL: Locator;
    readonly secSavos: Locator;
    readonly txtSavos: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Savos"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smSavosHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Savos' });
        this.secSavos = page.getByTitle('Savos');
        this.txtSavos = page.getByText('Savos Personal Portfolios');
    }

    async LoadsPage() {
        await this.logger((await this.secSavos.getAttribute('src')).toString());

        await expect(this.secSavos).toHaveAttribute(
            'src',
            /Investments\/Savos\.aspx$/
        );
        await this.logger((await this.secSavos.getAttribute('src')).toString());
        await expect(this.smSavosHL).toBeVisible();
        await this.logger('Page loaded for Investments > Savos');
    }
}