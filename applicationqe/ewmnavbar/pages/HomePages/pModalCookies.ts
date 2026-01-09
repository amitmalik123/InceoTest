import { type Page, type Locator, type FrameLocator, expect } from "@playwright/test";
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ModalCookiesPage {
    
    readonly context: Page | FrameLocator; 
    private fElement: ElementHelper;

    readonly modalCookies: Locator;
    readonly btnAllowAll: Locator;
    readonly ovlFilter: Locator;
    readonly maintenanceCloseIcon: Locator;

    constructor(context: Page | FrameLocator, logger: Logger) {
        this.context = context;
        this.fElement = new ElementHelper(logger);

        // Locators (OneTrust)
        this.modalCookies = context.locator('#onetrust-pc-content').or(context.locator('#onetrust-pc-sdk'));
        this.btnAllowAll = context.locator('#accept-recommended-btn-handler');
        this.ovlFilter = context.locator('.onetrust-pc-dark-filter.ot-fade-in');
        
        // Locators (Maintenance / Other Overlays)
        this.maintenanceCloseIcon = context.locator('.AdvisorDashboard_closeNewIcon__3vWMT');
    }

    // ==========================================================
    // 🍪 Modal Actions
    // ==========================================================
    async closeModal() {
        // Check visibility with a short timeout (5s) to avoid slowing down tests if modal isn't there
        const isVisible = await this.modalCookies.isVisible({ timeout: 5000 });

        if (isVisible) {
            await this.fElement.log('🍪 One Trust modal found. Attempting to close...');
            
            await this.fElement.clickElem(this.btnAllowAll, 'button Allow All Cookies');
            
            // Ensure the dark overlay filter fades out
            await expect(this.ovlFilter).toBeHidden();
            
            // Small stability wait for the DOM to settle after overlay removal
            // (Safe way to wait regardless of whether context is Page or Frame)
            await new Promise(resolve => setTimeout(resolve, 1000));
            await this.fElement.log('✅ Modal closed and overlay cleared.');
        
        } else {
            await this.fElement.log('ℹ️ Cookie modal not visible. Proceeding.');
        }
    }

    async closeModalIframe() {
        // Placeholder for future logic if OneTrust appears inside a frame
    }
}