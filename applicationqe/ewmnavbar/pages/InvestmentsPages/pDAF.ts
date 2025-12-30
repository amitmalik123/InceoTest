import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class DAFPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smDAFHL: Locator;
    readonly secDAF: Locator;
    readonly txtWhatDAF: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="DAF"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smDAFHL = page.locator('a.active',{ hasText: 'DAF' });
        this.secDAF = page.getByTitle('DAF');
        this.txtWhatDAF = page.getByText('What are Donor-Advised Funds (DAFs)?');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smDAFHL, 'submenu DAF (Highlighted)');

        const src = await this.secDAF.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secDAF).toHaveAttribute(
            'src',
            /Investments\/DAF\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Investments > DAF');
    }
}