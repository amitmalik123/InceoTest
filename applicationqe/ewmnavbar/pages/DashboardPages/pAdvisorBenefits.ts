import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class AdvisorBenefitsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smAdvisorBenefitsHL: Locator;

    // --- iFrame & Content ---
    readonly secAdvisorBenefits: Locator; // The actual <iframe> element
    
    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       // Locator INSIDE the iFrame (New App)
    readonly secLegacySiteCore: Locator; // Locator ON the page (Legacy App)

    // --- Cards (Inside iFrame) ---
    readonly cardEvents: Locator;
    readonly cardYourBenefits: Locator;
    readonly cardYourBenefitsDashboard: Locator;
    readonly cardYourProgress: Locator;
    readonly cardYourStatus: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Advisor Benefits"]';
        const contentSelector = ".AdvisorDashboard_content__DF0tl";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Navigation
        this.smAdvisorBenefitsHL = page.locator('a.active', { hasText: 'Advisor Benefits' });
        
        // Main Sections
        this.secAdvisorBenefits = page.getByTitle('Advisor Benefits');
        this.secIFrameContent = iFrameContext.locator('.AppComponent_App__1PJsb'); 
        this.secSiteCore = iFrameContext.locator(contentSelector);
        
        // Legacy
        this.secLegacySiteCore = page.locator(contentSelector);

        // Cards inside iFrame
        this.cardEvents = iFrameContext.locator('.EventsWidget_cardHeading__1O5T2:has-text("Events")');
        this.cardYourBenefits = iFrameContext.locator('.YourBenefits_cardHeading__hUAqG:has-text("Your Benefits")');
        this.cardYourBenefitsDashboard = iFrameContext.locator('.Overviewcard_contentHeading__2jFxT:has-text("Your Benefits Dashboard")');
        this.cardYourProgress = iFrameContext.locator('div[data-test-id="counter"]:has-text("Your Progress")');
        this.cardYourStatus = iFrameContext.locator('div[data-test-id="mainStatus"]:has-text("Your Status")');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smAdvisorBenefitsHL, 'Advisor Benefits Highlight');

        const src = await this.secAdvisorBenefits.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secAdvisorBenefits).toHaveAttribute(
            'src',
            /advisorbenefits\/dashboard$/
        );
        
        await this.fElement.log('✅ Landed on Page: Dashboard > Advisor Benefits');
    }

    async ElementsExist() {
        await this.fElement.log('📢 Verifying Advisor Benefits Dashboard Cards...');
        
        await this.fElement.elemVisible(this.cardEvents, 'card Events');
        await this.fElement.elemVisible(this.cardYourBenefits, 'card Your Benefits');
        await this.fElement.elemVisible(this.cardYourBenefitsDashboard, 'card Your Benefits Dashboard');
        await this.fElement.elemVisible(this.cardYourProgress, 'card Your Progress');
        await this.fElement.elemVisible(this.cardYourStatus, 'card Your Status');
    
        await this.fElement.log('✅ All Advisor Benefits cards are visible.');
    }
}