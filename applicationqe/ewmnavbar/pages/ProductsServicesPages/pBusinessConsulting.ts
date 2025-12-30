import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class BusinessConsultingPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smBusinessConsultingHL: Locator;
    readonly secBusinessConsulting: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Business Consulting"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smBusinessConsultingHL = page.locator('a.active',{ hasText: 'Business Consulting' });
        this.secBusinessConsulting = page.getByTitle('Business Consulting');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smBusinessConsultingHL, 'submenu Business Consulting (Highlighted)');

        const src = await this.secBusinessConsulting.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secBusinessConsulting).toHaveAttribute(
            'src',
            /practice-management\/Overview\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Products & Services > Business Consulting');
    }
}