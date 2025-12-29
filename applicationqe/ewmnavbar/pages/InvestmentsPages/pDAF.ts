
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class DAFPage {
    readonly page: Page;
    private logger: Logger;

    readonly smDAFHL: Locator;
    readonly secDAF: Locator;
    readonly txtWhatDAF: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="DAF"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smDAFHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'DAF' });
        this.secDAF = page.getByTitle('DAF');
        this.txtWhatDAF = page.getByText('What are Donor-Advised Funds (DAFs)?');
    }

    async LoadsPage() {
        await this.logger((await this.secDAF.getAttribute('src')).toString());

        await expect(this.secDAF).toHaveAttribute(
            'src',
            /Investments\/DAF\.aspx$/
        );
        await this.logger((await this.secDAF.getAttribute('src')).toString());
        await elemVisible(this.smDAFHL, 'submenu DAF is Highlighted', this.logger);
        await this.logger('Page loaded for Investments > DAF');
    }
}