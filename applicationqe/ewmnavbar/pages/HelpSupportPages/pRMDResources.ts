import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class RMDResourcesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smRMDResourcesHL: Locator;
    readonly secRMDResources: Locator;
    readonly imgRMDResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="RMD Resources"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smRMDResourcesHL =page.locator('a.active',{ hasText: 'RMD Resources' });
        this.secRMDResources = page.getByTitle('RMD Resources');
        this.imgRMDResources = iFrameContext.getByAltText('RMD Resources');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smRMDResourcesHL, 'submenu RMD Resources (Highlighted)');

        const src = await this.secRMDResources.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secRMDResources).toHaveAttribute(
            'src',
            /Administration\/Tax-Resources\/rmd_center\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Help & Support > RMD Resources');
    }
}