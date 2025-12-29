
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class OverviewPage {
    readonly page: Page;
    private logger: Logger;

    readonly secDashboardPage: Locator;
    readonly ddlAdvisorID: Locator;
    readonly secRotator: Locator;



    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.secDashboardPage = page.locator('.dashboard-page');
        this.ddlAdvisorID = page.locator('button[role="combobox"] label[title="All"]');
        this.secRotator = page.locator('.max-w-screen-2xl.m-auto.px-4.mt-2');

    }

    async ElementsExist() {
        await elemVisible(this.secRotator, 'Rotator Section', this.logger, 30000);
        await elemVisible(this.secDashboardPage, 'Dashboard Page Section', this.logger);
        await this.logger('Page loaded for Dashboard > Overview');
    }
}