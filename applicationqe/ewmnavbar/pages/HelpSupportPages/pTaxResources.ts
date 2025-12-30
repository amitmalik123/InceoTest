import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class TaxResourcesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smTaxResourcesHL: Locator;
    readonly secTaxResources: Locator;
    readonly imgTaxResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Tax Resources"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smTaxResourcesHL = page.locator('a.active', { hasText: 'Tax Resources' });
        this.secTaxResources = page.getByTitle('Tax Resources');
        this.imgTaxResources = iFrameContext.getByAltText('Tax Resources');
 
        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smTaxResourcesHL, 'submenu Tax Resources (Highlighted)');

        const src = await this.secTaxResources.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secTaxResources).toHaveAttribute(
            'src',
            /Administration\/Tax-Resources\/tax_center\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Help & Support > Tax Resources');
    }
}