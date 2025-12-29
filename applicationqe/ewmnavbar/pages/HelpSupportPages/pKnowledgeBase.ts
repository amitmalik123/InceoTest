
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class KnowledgeBasePage {
    readonly page: Page;
    private logger: Logger;

    readonly smKnowledgeBaseHL: Locator;
    readonly secKnowledgeBase: Locator;
    readonly secRotator: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Knowledge Base"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smKnowledgeBaseHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Knowledge Base' });
        this.secKnowledgeBase = page.getByTitle('Knowledge Base');
    }


    async LoadsPage() {
        await this.logger((await this.secKnowledgeBase.getAttribute('src')).toString());

        await expect(this.secKnowledgeBase).toHaveAttribute(
            'src',
            /Administration\/Overview\.aspx$/
        );
        await this.logger((await this.secKnowledgeBase.getAttribute('src')).toString());
        await elemVisible(this.smKnowledgeBaseHL, 'submenu Knowledge Base is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > Knowledge Base');
    }
}