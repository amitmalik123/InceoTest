import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class SavosPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smSavosHL: Locator;
    readonly secSavos: Locator;
    readonly txtSavos: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Savos"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smSavosHL = page.locator('a.active',{ hasText: 'Savos' });
        this.secSavos = page.getByTitle('Savos');
        this.txtSavos = page.getByText('Savos Personal Portfolios');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smSavosHL, 'submenu Savos (Highlighted)');

        const src = await this.secSavos.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secSavos).toHaveAttribute(
            'src',
            /Investments\/Savos\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > Savos');
    }
}