
import { type Page, type Locator, expect, type FrameLocator } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;


export class ModalCookiesPage {
    
    readonly context: Page | FrameLocator; 
    private logger: Logger;

    readonly ovlBody: Locator;
    readonly modalCookies: Locator;
    readonly btnAllowAll: Locator;
    readonly ovlFilter: Locator;
    readonly maintenanceCloseIcon: Locator;

    constructor(context: Page | FrameLocator, logger: Logger) {
        this.context = context;
        this.logger = logger;

        this.modalCookies = context.locator('#onetrust-pc-content').or(context.locator('#onetrust-pc-sdk'));
        this.btnAllowAll = context.locator('#accept-recommended-btn-handler');
        this.ovlFilter = context.locator('.onetrust-pc-dark-filter.ot-fade-in');
        this.maintenanceCloseIcon = context.locator('.AdvisorDashboard_closeNewIcon__3vWMT');

    }


    async closeModal() {
        try {
            await elemVisible(this.modalCookies, 'Cookie Modal', this.logger, 10000);

            console.log('🍪 One Trust modal found. Click button Allow All.');
            await this.btnAllowAll.scrollIntoViewIfNeeded();
            await this.btnAllowAll.click();
            await expect(this.ovlFilter).toBeHidden();
            await (this.context as Page).waitForTimeout(1000);
            await this.logger('⏳ Waiting 1 secs after modal closure...');

        } catch (e) {
            await this.logger('Cookie modal not visible within 5 seconds. Proceeding.');
        }
    }

    async closeMocalIframe() {
        

    }
}
