import { expect, type Page, Locator } from "@playwright/test";
import { ModalCookiesPage } from "../pages/HomePages/pModalCookies";
import { getImage } from '../helper/getImage';

// Define the type for the elements we are tracking
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
        this.testInfo = testInfo;
    }

    // ------------------------------------------------------------------
    // Helper Function to strip the 'locator(...)' wrapper
    // ------------------------------------------------------------------
    private extractSelectorString(locator: Locator): string {
        const fullString = locator.toString();
        const match = fullString.match(/locator\((.*)\)/);

        if (match && match[1]) {
            return match[1].replace(/^['"]|['"]$/g, '');
        }

        return fullString;
    }

    // ------------------------------------------------------------------
    // ⭐ NEW: Generic method to count all tracked elements in a locator
    // ------------------------------------------------------------------
    private async countElements(
        parentLocator: Locator,
        contextName: 'NavBar' | 'Legacy'
    ): Promise<ElementCounts> {
        const counts: Partial<ElementCounts> = {};

        await this.logger(`--- Counting elements on ${contextName} page context ---`);

        for (const tag of this.trackedElements) {
            const selector = tag as string;
            const count = await parentLocator.locator(selector).count();
            counts[tag] = count;
            let logMsg = `${contextName} No. of: <${tag}> elements: ${count}`;
            if (tag === 'img') logMsg = logMsg.replace(/<\w+>/, '🖼️ Images');
            if (tag === 'a') logMsg = logMsg.replace(/<\w+>/, '🔗 Links');

            await this.logger(logMsg);
        }

        return counts as ElementCounts;
    }

    // ------------------------------------------------------------------
    // 1. High-Level Helper Method 
    // ------------------------------------------------------------------
    async compareNavBarwithLegacy(
        iframeLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        const iFrameUrl = await iframeLocator.getAttribute('src');
        const defaultCounts: ElementCounts = {
            img: 0, a: 0, p: 0, span: 0, label: 0, input: 0
        };

        if (!iFrameUrl) {
            await this.logger('❌ Comparission Skipped: Could not find iFrame URL (iFrame src).');
            return {
                ...defaultCounts, // Return all counts as 0
                mismatch: true,
                legacyUrl: null,
            };
        }

        const {
            navCounts,
            legacyCounts
        } = await this.compareContentCounts(
            iFrameUrl,
            iframeLocator,
            auditContentLocator,
            originalContentLocator
        );

        let mismatch = false;

        // Compare all tracked element counts
        for (const tag of this.trackedElements) {
            if (navCounts[tag] !== legacyCounts[tag]) {
                mismatch = true;
                await this.logger(`⚠️ Mismatch - <${tag}>: NavBar (${navCounts[tag]}) does not match with Legacy (${legacyCounts[tag]})`);
            } else {
                await this.logger(`✅ Match - <${tag}>: NavBar (${navCounts[tag]}) match with Legacy (${legacyCounts[tag]})`);
            }
        }

        return {
            ...navCounts,
            ...legacyCounts,
            navCounts,
            legacyCounts,
            mismatch,
            legacyUrl: iFrameUrl,
        };
    }

    // ------------------------------------------------------------------
    // 2. Core Comparison Method (Fix applied here)
    // ------------------------------------------------------------------
    async compareContentCounts(
        iFrameUrl: string,
        navBarIFrameLocator: Locator,
        auditContentLocator: Locator,
        originalContentLocator: Locator
    ) {
        // Initialize counts
        let navCounts: ElementCounts = { img: 0, a: 0, p: 0, span: 0, label: 0, input: 0 };
        let legacyCounts: ElementCounts = { img: 0, a: 0, p: 0, span: 0, label: 0, input: 0 };

        // --- Dynamic Modal Handling (inside iFrame) ---
        const iFrameSelector = this.extractSelectorString(navBarIFrameLocator);
        const iFrameContext = this.page.frameLocator(iFrameSelector);
        const navBarIFrameModal = new ModalCookiesPage(iFrameContext, this.logger);

        try {
            await navBarIFrameModal.closeModal();
            await expect(navBarIFrameLocator).toBeVisible({ timeout: 10000 });
        } catch (error) {
            this.logger(`⚠️ Modal handling failed inside NavBar iFrame.`);
        }

        // --- 1. Count on the NavBar Page Context (using NEW helper) ---
        navCounts = await this.countElements(originalContentLocator, 'NavBar');

        // --- 2. Open the NEW Page for Audit ---
        const context = this.page.context();
        const newPage = await context.newPage();
        await newPage.goto(iFrameUrl, { waitUntil: 'domcontentloaded' });
        await this.logger(`🆕 Opened Legacy page link: ${iFrameUrl}`);

        // --- Capture screenshot of the legacy app ---
        const imgHelper = new getImage(newPage, this.testInfo);
        await imgHelper.wholePage('LegacyAppScreenshot');

        // --- 3. Dynamic Modal Handling (on Legacy/Audit page) & Stabilization FIX ---
        const legacyPageModal = new ModalCookiesPage(newPage, this.logger);

        // --- Get the clean selector string ---
        const LegacyLocatorString = this.extractSelectorString(auditContentLocator);
        const LegacyLocator = newPage.locator(LegacyLocatorString);

        try {
            await legacyPageModal.closeModal();
            await expect(LegacyLocator).toBeVisible({ timeout: 10000 });
        } catch (error) {
            this.logger(`⚠️ Modal handling or post-modal stabilization failed on audit page.`);
        }

        // --- 4. Count on the Legacy Page (using NEW helper) ---
        let locatorFound = false;

        try {
            const locatorCount = await LegacyLocator.count();

            if (locatorCount > 0) {
                locatorFound = true;
                // Count all elements within the Legacy Locator
                legacyCounts = await this.countElements(LegacyLocator, 'Legacy');
            } else {
                await this.logger(`⚠️ Locator ${LegacyLocatorString} count was 0 (Element not found in DOM).`);
            }

        } catch (e) {
            this.logger(`❌ Counting elements failed for '${LegacyLocatorString}'.`);
            this.logger(`   Full Error: ${e}`);
        }

        // --- 5. Cleanup & Comparison ---
        await newPage.close();
        await this.page.bringToFront();

        // The comparison logic 
        return {
            navCounts,
            legacyCounts
        };
    }
}