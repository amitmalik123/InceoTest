import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class RetirementServicesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smRetirementServicesHL: Locator;
    readonly secRetirementServices: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Retirement Services"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smRetirementServicesHL = page.locator('a.active',{ hasText: 'Retirement Services' });
        this.secRetirementServices = page.getByTitle('Retirement Services');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smRetirementServicesHL, 'submenu Retirement Services (Highlighted)');

        const src = await this.secRetirementServices.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secRetirementServices).toHaveAttribute(
            'src',
            /retirement\/Overview\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Products & Services > Retirement Services');
    }
}