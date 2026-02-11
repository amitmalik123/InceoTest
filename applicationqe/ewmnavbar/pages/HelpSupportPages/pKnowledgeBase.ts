import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class KnowledgeBasePage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smKnowledgeBaseHL: Locator;
    readonly secKnowledgeBase: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Knowledge Base"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smKnowledgeBaseHL = page.locator('a.active',{ hasText: 'Knowledge Base' });
        this.secKnowledgeBase = page.getByTitle('Knowledge Base');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smKnowledgeBaseHL, 'submenu Knowledge Base (Highlighted)');

        const src = await this.secKnowledgeBase.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secKnowledgeBase).toHaveAttribute(
            'src',
            /Administration\/Overview\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Help & Support > Knowledge Base');
    }
}