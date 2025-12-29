
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class StrategiesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smStrategiesHL: Locator;
    readonly tblStrategies: Locator;
    readonly secStrategies: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Strategies"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smStrategiesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Strategies' });
        this.tblStrategies = page.locator('.strategyPanelContent');
        this.secStrategies = page.getByTitle('Strategies');
    }

    async LoadsPage() {
        await this.logger((await this.secStrategies.getAttribute('src')).toString());

        await expect(this.secStrategies).toHaveAttribute(
            'src',
            /Investments\/Strategies\.aspx$/
        );
        await this.logger((await this.secStrategies.getAttribute('src')).toString());
        await elemVisible(this.smStrategiesHL, 'submenu Strategies is Highlighted', this.logger);
        await this.logger('Page loaded for Investments > Strategies');
    }


}