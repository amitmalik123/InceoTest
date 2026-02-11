import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class TMSPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smTMSHL: Locator;
    readonly secTMS: Locator;
    readonly txtWhatTMS: Locator;
    readonly imgTAX: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="TMS"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smTMSHL = page.locator('a.active',{ hasText: 'TMS' });
        this.secTMS = page.getByTitle('TMS');
        
        // Note: If these elements are inside the iFrame, change 'page' to 'iFrameContext'
        this.txtWhatTMS = page.getByText('AssetMark\'s Tax Management Services (TMS)');
        this.imgTAX = page.getByAltText('Tax Savings Report');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smTMSHL, 'submenu TMS (Highlighted)');

        const src = await this.secTMS.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secTMS).toHaveAttribute(
            'src',
            /Investments\/TMS\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > TMS');
    }
}