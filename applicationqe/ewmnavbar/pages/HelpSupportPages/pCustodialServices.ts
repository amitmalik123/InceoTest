import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class CustodialServicesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smCustodialServicesHL: Locator;
    readonly secCustodialServices: Locator;
    readonly imgCustodialServices: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Custodial Services"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smCustodialServicesHL = page.locator('a.active',{ hasText: 'Custodial Services' });
        
        this.secCustodialServices = page.getByTitle('Custodial Services');
        this.imgCustodialServices = iFrameContext.getByAltText('Custodial Services');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smCustodialServicesHL, 'submenu Custodial Services (Highlighted)');
        
        const src = await this.secCustodialServices.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secCustodialServices).toHaveAttribute(
            'src',
            /Administration\/Custodial-Services\/Custodial-Services\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Help & Support > Custodial Services');
    }
}