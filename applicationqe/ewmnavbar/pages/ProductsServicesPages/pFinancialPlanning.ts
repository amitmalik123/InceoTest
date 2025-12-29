
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class FinancialPlanningPage {
    readonly page: Page;
    private logger: Logger;

    readonly smFinancialPlanningHL: Locator;
    readonly secFinancialPlanning: Locator;
    readonly txtFinancialPlanning: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Financial Planning"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smFinancialPlanningHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Financial Planning' });
        this.secFinancialPlanning = page.getByTitle('Financial Planning');
        // this.txtFinancialPlanning = page.getByText('What are Donor-Advised Funds (DAFs)?');
    }

    async LoadsPage() {
        await this.logger((await this.secFinancialPlanning.getAttribute('src')).toString());

        await expect(this.secFinancialPlanning).toHaveAttribute(
            'src',
            /Planning\/Overview\.aspx$/
        );
        await elemVisible(this.smFinancialPlanningHL, 'submenu Financial Planning is Highlighted', this.logger);
        await this.logger('Page loaded for Products & Services > Financial Planning');
    }
}