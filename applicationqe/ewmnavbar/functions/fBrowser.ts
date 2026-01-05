import { Page, BrowserContext, Locator, expect } from "@playwright/test";
import { ElementHelper } from "./fElement";

export type Logger = (msg: string) => Promise<void> | void;

export class BrowserActions {
    private context: BrowserContext;

    constructor(private page: Page, private logger?: Logger) {
        this.context = page.context();
    }

    /**
     * PRIVATE HELPER: Centralized Error Handling
     */
    private async wrap<T>(
        action: () => Promise<T>,
        successMsg: string,
        failMsg: string
    ): Promise<T> {
        try {
            const result = await action();
            if (this.logger) await this.logger(successMsg);
            return result;
        } catch (error: any) {
            const detailedError = `${failMsg}\nReason: ${error.message}`;
            if (this.logger) await this.logger(detailedError);
            throw new Error(detailedError);
        }
    }

    // ==========================================================
    // 🌍 NAVIGATION & URL
    // ==========================================================
    async goToURL(url: string) {
        await this.wrap(
            async () => await this.page.goto(url),
            `🌍 Navigated to: ${url}`,
            `❌ Failed to navigate to ${url}`
        );
    }

    async getCurrentURL(): Promise<string> {
        const url = this.page.url();
        if (this.logger) await this.logger(`🔗 Current URL: ${url}`);
        return url;
    }

    async refresh() {
        await this.wrap(
            async () => await this.page.reload(),
            "🔄 Page refreshed",
            "❌ Failed to refresh page"
        );
    }

    async goBack() {
        await this.page.goBack();
        if (this.logger) await this.logger("⬅️ Navigated Back");
    }

    // ==========================================================
    // 🧠 WAITING & STATE
    // ==========================================================
    async verifyTitle(title: string) {
        await this.wrap(
            async () => await expect(this.page).toHaveTitle(new RegExp(title), { timeout: 5000 }),
            `✅ Title verified: contains '${title}'`,
            `❌ Title mismatch. Expected '${title}'`
        );
    }

    async waitForNetworkIdle(timeout = 5000) {
        await this.wrap(
            async () => await this.page.waitForLoadState('networkidle', { timeout }),
            "🧠 Network is idle (Page loaded)",
            "⚠️ Network did not become idle (Background calls still running)"
        );
    }

    async hardWait(ms: number) {
        await this.page.waitForTimeout(ms);
        if (this.logger) await this.logger(`⏳ Hard wait for ${ms}ms`);
    }

    // ==========================================================
    // 🖥️ WINDOW & VIEWPORT
    // ==========================================================
    async sizeMax() {
        try {
            const session = await this.context.newCDPSession(this.page);
            const { windowId } = await session.send("Browser.getWindowForTarget");
            await session.send("Browser.setWindowBounds", {
                windowId,
                bounds: { windowState: "maximized" },
            });
            if (this.logger) await this.logger("✅ Browser window maximized");
        } catch (err) {
            if (this.logger) await this.logger("⚠️ Maximize not supported. Falling back to desktop size.");
            await this.sizeDesktop();
        }
    }

    async sizeDesktop() {
        await this.page.setViewportSize({ width: 1920, height: 1080 });
        if (this.logger) await this.logger("🖥️ Viewport: Desktop (1920x1080)");
    }

    // ==========================================================
    // 📂 TABS & POPUPS
    // ==========================================================
    async newTab(url?: string) {
        const newPage = await this.context.newPage();
        if (url) await newPage.goto(url);
        if (this.logger) await this.logger(`🆕 New tab opened ${url ? `-> ${url}` : ''}`);
        return newPage;
    }

    /**
     * Clicks a locator and waits for the new tab to open.
     */
    async expectNewTab(trigger: Locator, name: string): Promise<Page> {
        return await this.wrap(
            async () => {
                const [newPage] = await Promise.all([
                    this.context.waitForEvent('page'),
                    trigger.click()
                ]);
                await newPage.waitForLoadState();
                return newPage;
            },
            `📑 ${name} successfully opened a new tab`,
            `❌ ${name} did NOT open a new tab`
        );
    }

    async closeTabs(keepFirst = true) {
        const pages = this.context.pages();
        const start = keepFirst ? 1 : 0;
        for (let i = start; i < pages.length; i++) {
            await pages[i].close();
        }
        if (this.logger) await this.logger(keepFirst ? "🚪 Closed extra tabs" : "🚪 Closed all tabs");
    }

    // ==========================================================
    // 🍪 STORAGE & COOKIES
    // ==========================================================
    async localStorageSet(key: string, value: string) {
        await this.page.evaluate(({ k, v }) => localStorage.setItem(k, v), { k: key, v: value });
        if (this.logger) await this.logger(`💾 LocalStorage set: ${key}=${value}`);
    }

    async localStorageClear() {
        await this.page.evaluate(() => localStorage.clear());
        if (this.logger) await this.logger("🧹 LocalStorage cleared");
    }

    async cookieAdd(name: string, value: string, domain: string) {
        await this.context.addCookies([{ name, value, domain, path: "/", httpOnly: false, secure: false }]);
        if (this.logger) await this.logger(`🍪 Cookie added: ${name}`);
    }

    async cookieDeleteAll() {
        await this.context.clearCookies();
        if (this.logger) await this.logger("🗑️ All cookies deleted");
    }

    async getAllCookies() {
        return await this.wrap(
            async () => await this.page.context().cookies(),
            "🍪 Snapshot: All browser cookies retrieved",
            "⚠️ Failed to capture cookies"
        );
    }

    // ==========================================================
    // 🛠️ DEBUGGING & SYSTEM
    // ==========================================================
    async takeScreenshot(name: string) {
        const path = `./screenshots/${name}_${Date.now()}.png`;
        await this.wrap(
            async () => await this.page.screenshot({ path, fullPage: true }),
            `📸 Screenshot saved: ${path}`,
            `❌ Failed to take screenshot`
        );
    }

    async handleDialog(action: 'accept' | 'dismiss' = 'accept') {
        this.page.once('dialog', async dialog => {
            const msg = dialog.message();
            if (action === 'accept') await dialog.accept();
            else await dialog.dismiss();
            if (this.logger) await this.logger(`💬 Dialog handled (${action}): "${msg}"`);
        });
    }

    async getClipboardText(): Promise<string> {
        return await this.wrap(
            async () => await this.page.evaluate(() => navigator.clipboard.readText()),
            `📋 Read text from clipboard`,
            `❌ Failed to read clipboard`
        );
    }

    // ==========================================================
    // 🖱️ PAGE INTERACTIONS
    // ==========================================================
    async scrollBy(yDistance: number) {
        await this.page.evaluate((y) => window.scrollBy(0, y), yDistance);
        if (this.logger) await this.logger(`⬇️ Scrolled by ${yDistance}px`);
    }

    async uploadFile(selector: string, filePath: string) {
        await this.wrap(
            async () => await this.page.locator(selector).setInputFiles(filePath),
            `📂 Uploaded file: ${filePath}`,
            `❌ Failed to upload file`
        );
    }

    // ==========================================================
    // 🧠 Network Call
    // ==========================================================

    async getNetworkRequest(urlFilter: string | RegExp) {
        return await this.wrap(
            async () => {
                const requests: any[] = [];
                this.page.on('request', (request) => {
                    if (request.url().match(urlFilter)) {
                        requests.push({
                            url: request.url(),
                            method: request.method(),
                            headers: request.headers(),
                            postData: request.postDataJSON(),
                        });
                    }
                });
                return requests;
            },
            `🔍 Monitoring outgoing requests matching: ${urlFilter}`,
            `⚠️ Failed to attach request listener`
        );
    }

    async getAllNetworkRequests() {
        const requests: any[] = [];
        this.page.on('request', (req) => {
            requests.push({
                url: req.url(),
                method: req.method(),
                headers: req.headers(),
                payload: req.postData()

            });
        });
        return requests;
    }

    async getNetworkResponse(urlFilter: string | RegExp) {
        return await this.wrap(
            async () => {
                const responses: any[] = [];
                this.page.on('response', async (response) => {
                    if (response.url().match(urlFilter)) {
                        responses.push({
                            url: response.url(),
                            status: response.status(),
                            headers: response.headers(),
                            body: await response.json().catch(() => ({})),
                        });
                    }
                });
                return responses;
            },
            `📥 Monitoring incoming responses matching: ${urlFilter}`,
            `⚠️ Failed to attach response listener`
        );
    }

    async getAllNetworkResponses() {
        const responses: any[] = [];
        this.page.on('response', async (res) => {
            responses.push({
                url: res.url(),
                status: res.status(),
                headers: res.headers(),
                body: await res.json().catch(() => ({})),
            });
        });
        return responses;
    }

    // Inside your Auth Class
    // Inside your Browser/Framework class
    async collectTrafficDuringAction(action: () => Promise<void>) {
        const traffic = { requests: [] as any[], responses: [] as any[] };

        // 1. Start Listening
        const reqListener = (req) => traffic.requests.push({ url: req.url(), method: req.method() });
        const resListener = async (res) => {
            const entry = { url: res.url(), status: res.status(), body: {} };
            // Try to get JSON but don't crash if it's an image/html
            if (res.headers()['content-type']?.includes('application/json')) {
                entry.body = await res.json().catch(() => ({}));
            }
            traffic.responses.push(entry);
        };

        this.page.on('request', reqListener);
        this.page.on('response', resListener);

        // 2. Perform the actual login or navigation
        await action();

        // 3. Stop Listening (cleanup)
        this.page.off('request', reqListener);
        this.page.off('response', resListener);

        return traffic;
    }
}
