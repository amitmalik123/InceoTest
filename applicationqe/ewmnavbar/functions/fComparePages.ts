import { expect, type Page, Locator, test } from "@playwright/test"; // 
import { ModalCookiesPage } from "../pages/HomePages/pModalCookies";

export type ElementCounts = {
    img: number;
    a: number;
    p: number;
    span: number;
    label: number;
    input: number;
    [key: string]: number;
};

type Logger = (msg: string) => Promise<void>;

export class ComparePageFunction {
    private readonly page: Page;
    private readonly logger: Logger;
    private readonly testInfo: any;

    private readonly trackedElements: Array<keyof ElementCounts> = ['img', 'a', 'p', 'span', 'label', 'input'];

    constructor(page: Page, logger: Logger, testInfo: any) {
        this.page = page;
        this.logger = logger;
        this.testInfo = testInfo || test.info(); 
    }

    private extractSelectorString(locator: Locator): string {
        const fullString = locator.toString();
        const match = fullString.match(/locator\((.*)\)/);
        if (match && match[1]) {
            return match[1].replace(/^['"]|['"]$/g, '');
        }
        return fullString;
    }

    private async countElements(
        parentLocator: Locator,
        contextName: 'NavBar' | 'Legacy'
    ): Promise<ElementCounts> {
        const counts: Partial<ElementCounts> = {}; 
        
        await this.logger(`--- Counting elements on ${contextName} page context ---`);

        for (const tag of this.trackedElements) {
            const count = await parentLocator.locator(tag as string).count();
            counts[tag] = count;

            let icon = '🔹';
            if (tag === 'img') icon = '🖼️';
            if (tag === 'a') icon = '🔗';
            
            await this.logger(`${icon} ${contextName}: Found ${count} <${tag}> elements`);
        }

        return counts as ElementCounts;
    }

    async compareNavBarwithLegacy(
        iframeLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        const iFrameUrl = await iframeLocator.getAttribute('src');

        if (!iFrameUrl) {
            await this.logger('❌ Comparison Skipped: Could not find iFrame URL.');
            return {
                mismatch: true,
                legacyUrl: null,
                navCounts: null,
                legacyCounts: null
            };
        }

        const { navCounts, legacyCounts } = await this.compareContentCounts(
            iFrameUrl,
            iframeLocator,
            auditContentLocator,
            originalContentLocator
        );

        let mismatch = false;

        await this.logger('--- 📊 Comparing Results ---');
        for (const tag of this.trackedElements) {
            const nav = navCounts[tag];
            const leg = legacyCounts[tag];

            if (nav !== leg) {
                mismatch = true;
                await this.logger(`⚠️ Mismatch <${tag}>: NavBar (${nav}) vs Legacy (${leg})`);
            } else {
                await this.logger(`✅ Match <${tag}>: ${nav}`);
            }
        }

        return {
            navCounts,
            legacyCounts,
            mismatch,
            legacyUrl: iFrameUrl,
        };
    }

    async compareContentCounts(
        iFrameUrl: string,
        navBarIFrameLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        // --- Handle Modal in Current Page ---
        const iFrameSelector = this.extractSelectorString(navBarIFrameLocator);
        const iFrameContext = this.page.frameLocator(iFrameSelector); 
        const navBarModal = new ModalCookiesPage(iFrameContext as any, this.logger);

        try {
            await navBarModal.closeModal();
            await expect(navBarIFrameLocator).toBeVisible({ timeout: 10000 });
        } catch (error) {
            await this.logger(`⚠️ Warning: Modal handling failed inside NavBar iFrame.`);
        }

        // --- Count Elements on Current Page ---
        const navCounts = await this.countElements(originalContentLocator, 'NavBar');

        // --- Open Legacy Page ---
        const context = this.page.context();
        const newPage = await context.newPage();
        
        await this.logger(`🆕 Opening Legacy URL: ${iFrameUrl}`);
        await newPage.goto(iFrameUrl, { waitUntil: 'domcontentloaded' });

        // --- Handle Modal on Legacy Page ---
        const legacyModal = new ModalCookiesPage(newPage, this.logger);
        const legacySelectorString = this.extractSelectorString(auditContentLocator);
        const legacyLocator = newPage.locator(legacySelectorString);

        try {
            await legacyModal.closeModal();
            await expect(legacyLocator).toBeVisible({ timeout: 10000 });
        } catch (error) {
            await this.logger(`⚠️ Warning: Modal/Wait failed on Legacy page.`);
        }

        // --- 📸 SCREENSHOT  ---
        try {
            if (!this.testInfo) {
                console.error("❌ ERROR: testInfo is undefined! Screenshot cannot be attached.");
                await this.logger("❌ ERROR: testInfo is undefined. Check your test file arguments.");
            } else {
                const screenshot = await newPage.screenshot({ fullPage: true });
                await this.testInfo.attach('Legacy App Screenshot', { 
                    body: screenshot, 
                    contentType: 'image/png' 
                });
                await this.logger('📸 Screenshot successfully attached to report.');
            }
        } catch (e) {
            await this.logger(`⚠️ Screenshot Failed: ${e}`);
        }

        // --- Count Elements on Legacy Page ---
        let legacyCounts: ElementCounts = { img: 0, a: 0, p: 0, span: 0, label: 0, input: 0 };

        try {
            if (await legacyLocator.count() > 0) {
                legacyCounts = await this.countElements(legacyLocator, 'Legacy');
            } else {
                await this.logger(`⚠️ Legacy container '${legacySelectorString}' not found.`);
            }
        } catch (e) {
            await this.logger(`❌ Error counting on legacy page: ${e}`);
        }

        // --- Cleanup ---
        await newPage.close();
        await this.page.bringToFront();

        return { navCounts, legacyCounts };
    }
}