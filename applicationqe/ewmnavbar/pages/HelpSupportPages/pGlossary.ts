import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class GlossaryPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smGlossaryHL: Locator;
    readonly secGlossary: Locator;
    readonly imgGlossary: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Glossary"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smGlossaryHL =page.locator('a.active',{ hasText: 'Glossary' });
        this.secGlossary = page.getByTitle('Glossary');
        this.imgGlossary = iFrameContext.getByAltText('Glossary');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smGlossaryHL, 'submenu Glossary (Highlighted)');

        const src = await this.secGlossary.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secGlossary).toHaveAttribute(
            'src',
            /help\/glossary\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Help & Support > Glossary');
    }
}