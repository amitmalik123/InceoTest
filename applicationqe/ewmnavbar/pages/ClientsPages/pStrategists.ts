import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class StrategistsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smStrategistsHL: Locator;

    // --- iFrame & Content ---
    readonly secStrategists: Locator; 
    readonly imgStrategists: Locator; 

    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       
    readonly secLegacySiteCore: Locator; 

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Strategists"]';
        const contentSelector = "#StrategistList";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Locators
        this.smStrategistsHL = page.locator('a.active', { hasText: 'Strategists' }); 
        
        this.secStrategists = page.getByTitle('Strategists');
        this.imgStrategists = iFrameContext.getByAltText('Strategists');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        const src = await this.secStrategists.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secStrategists).toHaveAttribute(
            'src',
            /AccountsAnalysis\/Clients\/StrategistList$/
        );
        
        await this.fElement.elemVisible(this.smStrategistsHL, 'submenu Strategists (Highlighted)');
        await this.fElement.log('✅ Landed on Page: Clients > Strategists');
    }
}