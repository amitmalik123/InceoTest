import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class DirectIndexingPage {
    readonly page: Page;
    private logger: Logger;

    readonly smDirectIndexing: Locator;
    readonly secDirectIndexing: Locator;
    // readonly txtManagement: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;
        this.smDirectIndexing = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Direct Indexing' });
        this.secDirectIndexing = page.getByTitle('Direct Indexing');
        // this.txtManagement = page.getByText('At AssetMark, we understand the importance of optimizing cash management for your clients.');
    }

    async ElementsExist() {
        // await expect(this.txtManagement).toBeVisible({
        //     timeout: 10000,
        // });
        await this.page.waitForTimeout(10000);

        await expect(this.secDirectIndexing).toHaveAttribute(
            'src',
            /Investments\/Direct_Indexing\.aspx$/
        );
        await expect(this.smDirectIndexing).toBeVisible();
        await this.logger((await this.secDirectIndexing.getAttribute('src')).toString());
        await this.logger('Page loaded for Investment > Cash');

    }
}