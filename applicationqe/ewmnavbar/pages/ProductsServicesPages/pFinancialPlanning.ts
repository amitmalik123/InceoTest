import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class FinancialPlanningPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smFinancialPlanningHL: Locator;
    readonly secFinancialPlanning: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Financial Planning"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smFinancialPlanningHL = page.locator('a.active',{ hasText: 'Financial Planning' });
        this.secFinancialPlanning = page.getByTitle('Financial Planning');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smFinancialPlanningHL, 'submenu Financial Planning (Highlighted)');

        const src = await this.secFinancialPlanning.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secFinancialPlanning).toHaveAttribute(
            'src',
            /Planning\/Overview\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Products & Services > Financial Planning');
    }
}