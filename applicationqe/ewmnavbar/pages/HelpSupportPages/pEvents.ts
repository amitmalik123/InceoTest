
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class EventsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smEventsHL: Locator;
    readonly secEvents: Locator;
    readonly imgEvents: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Events"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smEventsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Events' });
        this.secEvents = page.getByTitle('Events');
        this.imgEvents = iFrame.getByAltText('Events');

    }

    async LoadsPage() {
        await this.logger((await this.secEvents.getAttribute('src')).toString());

        await expect(this.secEvents).toHaveAttribute(
            'src',
            /help-and-support\/events$/
        );
        await elemVisible(this.smEventsHL, 'submenu Events is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > Events');
    }
}