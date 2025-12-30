import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class StrategiesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smStrategiesHL: Locator;
    readonly tblStrategies: Locator;
    readonly secStrategies: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Strategies"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smStrategiesHL = page.locator('a.active',{ hasText: 'Strategies' });
        this.secStrategies = page.getByTitle('Strategies');
        // If tblStrategies is inside the iframe, use iFrameContext.locator(...) instead of page.locator(...)
        this.tblStrategies = page.locator('.strategyPanelContent');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smStrategiesHL, 'submenu Strategies (Highlighted)');

        const src = await this.secStrategies.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secStrategies).toHaveAttribute(
            'src',
            /Investments\/Strategies\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > Strategies');
    }
}