import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class AllClientsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smAllClientsHL: Locator;
    readonly secAllClients: Locator;
    readonly imgAllClients: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="All Clients"]');
        const site = "#ClientList";

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smAllClientsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'All Clients' });
        this.secAllClients = page.getByTitle('All Clients');
        this.imgAllClients = iFrame.getByAltText('All Clients');

    }

    async LoadsPage() {
        await this.logger((await this.secAllClients.getAttribute('src')).toString());

        await expect(this.secAllClients).toHaveAttribute(
            'src',
            /AccountsAnalysis\/Clients\/ClientList$/
        );
        await expect(this.smAllClientsHL).toBeVisible();
        await this.logger('Page loaded for Clients > All Clients');
    }
}