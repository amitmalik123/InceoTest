import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class AllClientsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smAllClientsHL: Locator;

    // --- iFrame & Content ---
    readonly secAllClients: Locator; // The actual <iframe> element
    readonly imgAllClients: Locator; // Image inside the iframe

    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       // Locator INSIDE the iFrame (New App)
    readonly secLegacySiteCore: Locator; // Locator ON the page (Legacy App)

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions for clarity
        const iFrameSelector = 'iframe[title="All Clients"]';
        const contentSelector = "#ClientList";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Locators
        this.smAllClientsHL = page.locator('a.active', { hasText: 'All Clients' });
        
        this.secAllClients = page.getByTitle('All Clients'); // The <iframe> tag
        this.imgAllClients = iFrameContext.getByAltText('All Clients');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        const src = await this.secAllClients.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secAllClients).toHaveAttribute(
            'src',
            /AccountsAnalysis\/Clients\/ClientList$/
        );

        await this.fElement.elemVisible(this.smAllClientsHL, 'submenu All Clients (Highlighted)');
        await this.fElement.log('✅ Landed on Page: Clients > All Clients');
    }
}