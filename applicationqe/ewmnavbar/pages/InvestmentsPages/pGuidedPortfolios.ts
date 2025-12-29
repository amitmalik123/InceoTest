
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class GuidedPortfoliosPage {
    readonly page: Page;
    private logger: Logger;

    readonly smGuidedPortfoliosHL: Locator;
    readonly secGuidedPortfolios: Locator;
    readonly txtGPS: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Guided Portfolios"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smGuidedPortfoliosHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Guided Portfolios' });
        this.secGuidedPortfolios = page.getByTitle('Guided Portfolios');
        this.txtGPS = page.getByText('Guided Portfolio Solutions (GPS)');
    }

    async LoadsPage() {
        await this.logger((await this.secGuidedPortfolios.getAttribute('src')).toString());

        await expect(this.secGuidedPortfolios).toHaveAttribute(
            'src',
            /Investments\/Guided-Portfolios\/About\.aspx$/
        );
        await this.logger((await this.secGuidedPortfolios.getAttribute('src')).toString());
        await elemVisible(this.smGuidedPortfoliosHL, 'submenu Guided Portfolios is Highlighted', this.logger);
        await this.logger('Page loaded for Investments > Guided Portfolios');
    }
}