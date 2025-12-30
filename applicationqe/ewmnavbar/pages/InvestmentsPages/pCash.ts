import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class CashPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smCashHL: Locator;
    readonly secCash: Locator;
    readonly txtManagement: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Cash"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smCashHL = page.locator('a.active',{ hasText: 'Cash' });
        this.secCash = page.getByTitle('Cash');
        // Note: txtManagement seems to be on the main page based on usage in your original code.
        // If it is inside the iframe, change 'page' to 'iFrameContext' below.
        this.txtManagement = page.getByText('At AssetMark, we understand the importance of optimizing cash management for your clients.');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smCashHL, 'submenu Cash (Highlighted)');

        const src = await this.secCash.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secCash).toHaveAttribute(
            'src',
            /Investments\/Cash-Solutions\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Investments > Cash');
    }
}