import { expect, type Page, Locator, test } from "@playwright/test";
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

    /**
     * NEW: Ensures the iFrame and its internal content are actually ready
     */
    private async waitForIFrameReady(iframeLocator: Locator, contentLocator: Locator) {
        await this.logger('⏳ Waiting for iFrame and Content to stabilize...');
        
        // 1. Wait for the iFrame element itself to be visible
        await expect(iframeLocator).toBeVisible({ timeout: 15000 });

        // 2. Ensure the src isn't empty or about:blank
        await expect(iframeLocator).toHaveAttribute('src', /.+/, { timeout: 10000 });

        // 3. Wait for the actual content container INSIDE the iFrame to be visible
        await expect(contentLocator).toBeVisible({ timeout: 15000 });
        
        // 4. Brief pause for JS rendering
        await this.page.waitForTimeout(1000); 
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
            let icon = tag === 'img' ? '🖼️' : tag === 'a' ? '🔗' : '🔹';
            await this.logger(`${icon} ${contextName}: Found ${count} <${tag}> elements`);
        }

        return counts as ElementCounts;
    }

    async compareNavBarwithLegacy(
        iframeLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        // --- STEP 0: Wait for iFrame to actually LOAD before grabbing URL ---
        await this.waitForIFrameReady(iframeLocator, originalContentLocator);

        const iFrameUrl = await iframeLocator.getAttribute('src');

        if (!iFrameUrl) {
            await this.logger('❌ Comparison Skipped: Could not find iFrame URL.');
            return { mismatch: true, legacyUrl: null, navCounts: null, legacyCounts: null };
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

        return { navCounts, legacyCounts, mismatch, legacyUrl: iFrameUrl };
    }

    async compareContentCounts(
        iFrameUrl: string,
        navBarIFrameLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        const iFrameSelector = this.extractSelectorString(navBarIFrameLocator);
        const iFrameContext = this.page.frameLocator(iFrameSelector); 
        const navBarModal = new ModalCookiesPage(iFrameContext as any, this.logger);

        try {
            await navBarModal.closeModal();
            await expect(originalContentLocator).toBeVisible({ timeout: 5000 });
        } catch (error) {
            await this.logger(`⚠️ Warning: Modal handling/visibility failed inside NavBar iFrame.`);
        }

        const navCounts = await this.countElements(originalContentLocator, 'NavBar');

        // --- Open Legacy Page ---
        const context = this.page.context();
        const newPage = await context.newPage();
        
        await this.logger(`🆕 Opening Legacy URL: ${iFrameUrl}`);
        // Wait for network idle to ensure legacy scripts finish
        await newPage.goto(iFrameUrl, { waitUntil: 'networkidle' });

        const legacyModal = new ModalCookiesPage(newPage, this.logger);
        const legacySelectorString = this.extractSelectorString(auditContentLocator);
        const legacyLocator = newPage.locator(legacySelectorString);

        try {
            await legacyModal.closeModal();
            await expect(legacyLocator).toBeVisible({ timeout: 10000 });
        } catch (error) {
            await this.logger(`⚠️ Warning: Modal/Wait failed on Legacy page.`);
        }

        // --- 📸 ATTACH SCREENSHOT ---
        try {
            const screenshot = await newPage.screenshot({ fullPage: true });
            await this.testInfo.attach('Legacy App Screenshot', { 
                body: screenshot, 
                contentType: 'image/png' 
            });
        } catch (e) {
            await this.logger(`⚠️ Screenshot Failed: ${e}`);
        }

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

        await newPage.close();
        await this.page.bringToFront();

        return { navCounts, legacyCounts };
    }
}