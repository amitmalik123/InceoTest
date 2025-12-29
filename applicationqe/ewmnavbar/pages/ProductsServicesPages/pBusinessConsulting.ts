
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class BusinessConsultingPage {
    readonly page: Page;
    private logger: Logger;

    readonly smBusinessConsultingHL: Locator;
    readonly secBusinessConsulting: Locator;
    readonly txtBusinessConsulting: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Business Consulting"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smBusinessConsultingHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Business Consulting' });
        this.secBusinessConsulting = page.getByTitle('Business Consulting');
    }

    async LoadsPage() {
        await this.logger((await this.secBusinessConsulting.getAttribute('src')).toString());

        await expect(this.secBusinessConsulting).toHaveAttribute(
            'src',
            /practice-management\/Overview\.aspx$/
        );
        await this.logger((await this.secBusinessConsulting.getAttribute('src')).toString());
        await elemVisible(this.smBusinessConsultingHL, 'submenu Business Consulting is Highlighted', this.logger);
        await this.logger('Page loaded for Products & Services > Business Consulting');
    }
}