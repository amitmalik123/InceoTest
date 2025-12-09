import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class StrategistsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smStrategistsHL: Locator;
    readonly secStrategists: Locator;
    readonly imgStrategists: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Strategists"]');
        const site = "#StrategistList"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smStrategistsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Strategists' });
        this.secStrategists = page.getByTitle('Strategists');
        this.imgStrategists = iFrame.getByAltText('Strategists');

    }

    async LoadsPage() {
        await this.logger((await this.secStrategists.getAttribute('src')).toString());

        await expect(this.secStrategists).toHaveAttribute(
            'src',
            /StrategistsAnalysis\/Clients\/StrategistList$/
        );
        await expect(this.smStrategistsHL).toBeVisible();
        await this.logger('Page loaded for Clients > Strategists');
    }
}