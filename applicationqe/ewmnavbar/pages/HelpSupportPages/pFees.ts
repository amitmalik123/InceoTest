import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class FeesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smFeesHL: Locator;
    readonly secFees: Locator;
    readonly imgFees: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Fees"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smFeesHL = page.locator('a.active',{ hasText: 'Fees' });
        this.secFees = page.getByTitle('Fees');
        this.imgFees = iFrameContext.getByAltText('Fees');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smFeesHL, 'submenu Fees (Highlighted)');

        const src = await this.secFees.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secFees).toHaveAttribute(
            'src',
            /Administration\/advisor-fee-payments\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Help & Support > Fees');
    }
}