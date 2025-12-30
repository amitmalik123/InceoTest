import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class MorningstarPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smMorningstarHL: Locator;
    readonly secMorningstar: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Renamed to HL (Highlighted) to indicate it checks the active state
        this.smMorningstarHL = page.locator('a.active',{ hasText: 'Morningstar' });
        this.secMorningstar = page.getByTitle('Morningstar');
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smMorningstarHL, 'submenu Morningstar (Highlighted)');

        const src = await this.secMorningstar.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secMorningstar).toHaveAttribute(
            'src',
            /Investments\/MorningstarLimitedOffering\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Investments > Morningstar');
    }
}