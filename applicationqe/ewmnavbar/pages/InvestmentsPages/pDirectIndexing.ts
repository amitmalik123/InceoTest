import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class DirectIndexingPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smDirectIndexingHL: Locator;
    readonly secDirectIndexing: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.smDirectIndexingHL = page.locator('a.active',{ hasText: 'Direct Indexing' });
        this.secDirectIndexing = page.getByTitle('Direct Indexing');
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smDirectIndexingHL, 'submenu Direct Indexing (Highlighted)');

        const src = await this.secDirectIndexing.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secDirectIndexing).toHaveAttribute(
            'src',
            /Investments\/Direct_Indexing\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > Direct Indexing');
    }
}