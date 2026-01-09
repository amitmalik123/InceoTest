import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class GuidedPortfoliosPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smGuidedPortfoliosHL: Locator;
    readonly secGuidedPortfolios: Locator;
    readonly txtGPS: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Guided Portfolios"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smGuidedPortfoliosHL = page.locator('a.active',{ hasText: 'Guided Portfolios' });
        this.secGuidedPortfolios = page.getByTitle('Guided Portfolios');
        this.txtGPS = page.getByText('Guided Portfolio Solutions (GPS)');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smGuidedPortfoliosHL, 'submenu Guided Portfolios (Highlighted)');

        const src = await this.secGuidedPortfolios.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secGuidedPortfolios).toHaveAttribute(
            'src',
            /Investments\/Guided-Portfolios\/About\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > Guided Portfolios');
    }
}