
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class GlossaryPage {
    readonly page: Page;
    private logger: Logger;

    readonly smGlossaryHL: Locator;
    readonly secGlossary: Locator;
    readonly imgGlossary: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Glossary"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smGlossaryHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Glossary' });
        this.secGlossary = page.getByTitle('Glossary');
        this.imgGlossary = iFrame.getByAltText('Glossary');

    }

    async LoadsPage() {
        await this.logger((await this.secGlossary.getAttribute('src')).toString());

        await expect(this.secGlossary).toHaveAttribute(
            'src',
            /help\/glossary\.aspx$/
        );
        await elemVisible(this.smGlossaryHL, 'submenu Glossary is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > Glossary');
    }
}