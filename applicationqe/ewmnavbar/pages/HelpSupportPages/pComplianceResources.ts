
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class ComplianceResourcesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smComplianceResourcesHL: Locator;
    readonly secComplianceResources: Locator;
    readonly imgComplianceResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Compliance Resources"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smComplianceResourcesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Compliance Resources' });
        this.secComplianceResources = page.getByTitle('Compliance Resources');
        this.imgComplianceResources = iFrame.getByAltText('Compliance Resources');

    }

    async LoadsPage() {
        await this.logger((await this.secComplianceResources.getAttribute('src')).toString());

        await expect(this.secComplianceResources).toHaveAttribute(
            'src',
            /Administration\/compliance-resources\/compliance-resources\.aspx$/
        );
        await elemVisible(this.smComplianceResourcesHL, 'submenu Compliance Resources is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > ComplianceResources');
    }
}