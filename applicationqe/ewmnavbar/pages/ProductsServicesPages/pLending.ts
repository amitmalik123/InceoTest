
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class LendingPage {
    readonly page: Page;
    private logger: Logger;

    readonly smLendingHL: Locator;
    readonly secLending: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Lending"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smLendingHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Lending' });
        this.secLending = page.getByTitle('Lending');
    }

    async LoadsPage() {
        await this.logger((await this.secLending.getAttribute('src')).toString());

        await expect(this.secLending).toHaveAttribute(
            'src',
            /Investments\/Lending-Solutions\.aspx$/
        );
        await this.logger((await this.secLending.getAttribute('src')).toString());
        await elemVisible(this.smLendingHL, 'submenu Lending is Highlighted', this.logger);
        await this.logger('Page loaded for Products & Services > Lending');
    }
}