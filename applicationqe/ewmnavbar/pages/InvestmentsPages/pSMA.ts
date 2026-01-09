import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class SMAPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smSMAHL: Locator;
    readonly secSMA: Locator;
    readonly txtManagement: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="SMA"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smSMAHL = page.locator('a.active',{ hasText: 'SMA' });
        this.secSMA = page.getByTitle('SMA');
        // Note: Check if txtManagement is inside the iframe or main page. 
        // Assuming main page based on original code, but if it fails, switch to iFrameContext.getByText(...)
        this.txtManagement = page.getByText('Clients look to you to help reach their unique financial goals. Now you have access to a curated suite of professionally managed SMAs on the AssetMark platform, designed to help tailor clients');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smSMAHL, 'submenu SMA (Highlighted)');

        const src = await this.secSMA.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secSMA).toHaveAttribute(
            'src',
            /Investments\/SMA\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > SMA');
    }
}