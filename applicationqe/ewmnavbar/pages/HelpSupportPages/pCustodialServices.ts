
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class CustodialServicesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smCustodialServicesHL: Locator;
    readonly secCustodialServices: Locator;
    readonly imgCustodialServices: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Custodial Services"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smCustodialServicesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Custodial Services' });
        this.secCustodialServices = page.getByTitle('Custodial Services');
        this.imgCustodialServices = iFrame.getByAltText('Custodial Services');

    }

    async LoadsPage() {
        await this.logger((await this.secCustodialServices.getAttribute('src')).toString());

        await expect(this.secCustodialServices).toHaveAttribute(
            'src',
            /Administration\/Custodial-Services\/Custodial-Services\.aspx$/
        );
        await elemVisible(this.smCustodialServicesHL, 'submenu Custodial Services is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > CustodialServices');
    }
}