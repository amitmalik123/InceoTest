
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class RetirementServicesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smRetirementServicesHL: Locator;
    readonly secRetirementServices: Locator;
    readonly txtRetirementServices: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Retirement Services"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smRetirementServicesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Retirement Services' });
        this.secRetirementServices = page.getByTitle('Retirement Services');
        // this.txtRetirementServices = page.getByText('What are Donor-Advised Funds (DAFs)?');
    }

    async LoadsPage() {
        await this.logger((await this.secRetirementServices.getAttribute('src')).toString());

        await expect(this.secRetirementServices).toHaveAttribute(
            'src',
            /retirement\/Overview\.aspx$/
        );
        await this.logger((await this.secRetirementServices.getAttribute('src')).toString());
        await elemVisible(this.smRetirementServicesHL, 'submenu Retirement Services is Highlighted', this.logger);
        await this.logger('Page loaded for Products & Services > Retirement Services');
    }
}