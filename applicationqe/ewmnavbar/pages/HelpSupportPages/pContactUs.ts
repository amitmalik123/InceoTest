import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class ContactUsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smContactUsHL: Locator;
    readonly secContactUs: Locator;
    readonly lnkContactUs: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.smContactUsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Contact Us' });
        this.secContactUs = page.getByTitle('Contact Us');

        const iFrame = page.frameLocator('iframe[title="Contact Us"]');
        const site = ".override-english";

        this.secIFrameContent = iFrame.locator('#Content');
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

    }

    async LoadsPage() {
        await this.logger((await this.secContactUs.getAttribute('src')).toString());
        await expect(this.secContactUs).toHaveAttribute(
            'src',
            /ContactUs$/
        );
        await expect(this.smContactUsHL).toBeVisible();
        await this.logger((await this.secContactUs.getAttribute('src')).toString());
        await this.logger('Page loaded for Help & Support > Contact Us');
    }
}