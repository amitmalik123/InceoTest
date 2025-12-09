import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class AdvisorBenefitsPage {
    readonly page: Page;
    private logger: Logger;

    readonly cardEvents: Locator;
    readonly cardYourBenefits: Locator;
    readonly cardYourBenefitsDashboard: Locator;
    readonly cardYourProgress: Locator;
    readonly cardYourStatus: Locator;
    readonly smAdvisorBenefitsHL: Locator;
    readonly secAdvisorBenefits: Locator;
    
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.smAdvisorBenefitsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Advisor Benefits' });
        this.secAdvisorBenefits = page.getByTitle('Advisor Benefits');

        const iFrame = page.frameLocator('iframe[title="Advisor Benefits"]');
        const site = ".AdvisorDashboard_content__DF0tl" 

        this.secIFrameContent = iFrame.locator('.AppComponent_App__1PJsb'); 
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);


        this.cardEvents = iFrame.locator('.EventsWidget_cardHeading__1O5T2:has-text("Events")');
        this.cardYourBenefits = iFrame.locator('.YourBenefits_cardHeading__hUAqG:has-text("Your Benefits")');
        this.cardYourBenefitsDashboard = iFrame.locator('.Overviewcard_contentHeading__2jFxT:has-text("Your Benefits Dashboard")');
        this.cardYourProgress = iFrame.locator('div[data-test-id="counter"]:has-text("Your Progress")');
        this.cardYourStatus = iFrame.locator('div[data-test-id="mainStatus"]:has-text("Your Status")');
    }

    async LoadsPage() {
        await expect(this.smAdvisorBenefitsHL).toBeVisible({ timeout: 20000 });
        await expect(this.secAdvisorBenefits).toHaveAttribute(
            'src',
            /advisorbenefits\/dashboard$/
        );
        await this.logger('Page loaded for Dashboard > Advisor Benefits');
    }

    async ElementsExist() {

        await expect(this.secAdvisorBenefits).toHaveAttribute(
            'src',
            /advisorbenefits\/dashboard$/
        );

        await expect(this.cardEvents).toBeVisible();
        await expect(this.cardYourBenefits).toBeVisible();
        await expect(this.cardYourBenefitsDashboard).toBeVisible();
        await expect(this.cardYourProgress).toBeVisible();
        await expect(this.cardYourStatus).toBeVisible();
        await expect(this.smAdvisorBenefitsHL).toBeVisible();

    }
}