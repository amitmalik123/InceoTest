import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ContactUsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smContactUsHL: Locator;

    // --- iFrame & Content ---
    readonly secContactUs: Locator; 

    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       
    readonly secLegacySiteCore: Locator; 

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Contact Us"]';
        const contentSelector = ".override-english";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Navigation
        this.smContactUsHL = page.locator('a.active',{ hasText: 'Contact Us' });

        // Main Sections
        this.secContactUs = page.getByTitle('Contact Us');

        // Content
        this.secIFrameContent = iFrameContext.locator('#Content');
        this.secSiteCore = iFrameContext.locator(contentSelector);

        // Legacy
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smContactUsHL, 'submenu Contact Us (Highlighted)');

        const src = await this.secContactUs.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secContactUs).toHaveAttribute(
            'src',
            /ContactUs$/
        );

        await this.fElement.log('✅ Landed on Page: Help & Support > Contact Us');
    }
}