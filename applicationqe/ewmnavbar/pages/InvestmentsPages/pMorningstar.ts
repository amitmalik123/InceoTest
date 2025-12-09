import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class MorningstarPage {
    readonly page: Page;
    private logger: Logger;

    readonly smMorningstar: Locator;
    readonly secMorningstar: Locator;
    readonly txtMorningstar: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;
        this.smMorningstar = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Morningstar' });
        this.secMorningstar = page.getByTitle('Morningstar');
        // this.txtMorningstar = page.getByText('Guided Portfolio Solutions (GPS)');
    }

    async ElementsExist() {
        // await expect(this.txtMorningstar).toBeVisible({
        //     timeout: 10000,
        // });
        await this.page.waitForTimeout(10000);

        await expect(this.secMorningstar).toHaveAttribute(
            'src',
            /Investments\/MorningstarLimitedOffering\.aspx$/
        );
        await expect(this.smMorningstar).toBeVisible();
        await this.logger((await this.secMorningstar.getAttribute('src')).toString());
        await this.logger('Page loaded for Investment > Morningstar');

    }
}