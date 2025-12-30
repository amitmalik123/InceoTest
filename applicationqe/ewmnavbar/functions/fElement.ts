import { expect, Locator, test } from "@playwright/test";
import { Logger } from "./fBrowser"; 

export class ElementHelper {
    constructor(private logger?: Logger, private defaultTimeout = 5000) { }

    /**
     * PRIVATE HELPER: Centralized Error Handling
     */
    private async wrap<T>(
        action: () => Promise<T>,
        successMsg: string,
        failMsg: string,
        element?: Locator 
    ): Promise<T> {
        try {
            const result = await action();
            if (this.logger) await this.logger(successMsg);
            return result;
        } catch (error: any) {
            const detailedError = `${failMsg}\nReason: ${error.message}`;
            
            // 📸 AUTO-SCREENSHOT ON FAIL
            const screenshot = await test.info().attach('failure-screenshot', {
                path: await test.info().outputPath('failure.png'),
                contentType: 'image/png',
            }).catch(() => null); 

            if (this.logger) {
                await this.logger(`📸 Screenshot captured for failure: ${failMsg}`);
                await this.logger(detailedError);
            }
            
            throw new Error(detailedError);
        }
    }

    // ==========================================================
    // 👁️ VISIBILITY & WAITS
    // ==========================================================
    async elemVisible(element: Locator, name: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await expect(element).toBeVisible({ timeout }),
            `✅ ${name} is visible`,
            `❌ ${name} is NOT visible`
        );
    }

    // // state: 'visible' | 'attached' | 'detached' | 'hidden' 
     async waitForElemVisible(element: Locator, name: string) {
        await this.wrap(
            async () => await element.waitFor({ state: 'visible' }),
            `✅ ${name} is present (State: visible)`,
            `❌ ${name} is NOT present (State: visible)`
        );
    }

    async waitForElemHidden(element: Locator, name: string) {
        await this.wrap(
            async () => await element.waitFor({ state: 'hidden' }),
            `✅ ${name} is present (State: hidden)`,
            `❌ ${name} is NOT present (State: hidden)`
        );
    }

    async waitForDisappearance(element: Locator, name: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await expect(element).not.toBeVisible({ timeout }),
            `✅ ${name} disappeared`,
            `❌ ${name} is stuck on screen`
        );
    }

    // ==========================================================
    // 🖱️ INTERACTIONS (Click, Type, Select)
    // ==========================================================
    async clickElem(element: Locator, name: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await element.click({ timeout }),
            `🖱️ Clicked ${name}`,
            `❌ Failed to click ${name}`
        );
    }

    async forceClick(element: Locator, name: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await element.click({ force: true, timeout }),
            `🔨 Force-clicked ${name}`,
            `❌ Failed to force-click ${name}`
        );
    }

    async hoverElem(element: Locator, name: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await element.hover({ timeout }),
            `👆 Hovered over ${name}`,
            `❌ Failed to hover over ${name}`
        );
    }

    async typeInField(element: Locator, name: string, text: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => {
                await element.fill(text, { timeout });
                // Optional: Fast verify the value
                await expect(element).toHaveValue(text, { timeout: 1000 });
            },
            `⌨️ Typed "${text}" into ${name}`,
            `❌ Failed to type into ${name}`
        );
    }

    async pressKey(element: Locator, name: string, key: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await element.press(key, { timeout }),
            `🎹 Pressed key "${key}" on ${name}`,
            `❌ Failed to press "${key}" on ${name}`
        );
    }

    async selectOption(element: Locator, name: string, valueOrLabel: string, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await element.selectOption({ label: valueOrLabel }, { timeout }),
            `🔽 Selected option "${valueOrLabel}" in ${name}`,
            `❌ Failed to select "${valueOrLabel}" in ${name}`
        );
    }

    // ==========================================================
    // 🔍 ATTRIBUTES & TEXT
    // ==========================================================
    async textExists(element: Locator, name: string, expectedText: string | RegExp, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await expect(element).toHaveText(expectedText, { timeout }),
            `✅ Text "${expectedText}" exists in ${name}`,
            `❌ Text "${expectedText}" does NOT exist in ${name}`
        );
    }

    async elemHasAttribute(element: Locator, name: string, attribute: string, expectedValue: string | RegExp, timeout = this.defaultTimeout) {
        await this.wrap(
            async () => await expect(element).toHaveAttribute(attribute, expectedValue, { timeout }),
            `✅ ${name} has attribute ${attribute}="${expectedValue}"`,
            `❌ ${name} missing attribute ${attribute}="${expectedValue}"`
        );
    }

    async getCssValue(element: Locator, name: string, cssProperty: string): Promise<string> {
        return await this.wrap(
            async () => {
                return await element.evaluate((el, prop) => {
                    return window.getComputedStyle(el).getPropertyValue(prop);
                }, cssProperty);
            },
            `🎨 Retrieved CSS property "${cssProperty}" from ${name}`,
            `❌ Failed to get CSS property from ${name}`
        );
    }

    // ==========================================================
    // 🛡️ SAFE METHODS (No Throw)
    // ==========================================================
    async elemVisibleSafe(element: Locator, name: string): Promise<boolean> {
        try {
            await expect(element).toBeVisible({ timeout: 2000 });
            if (this.logger) await this.logger(`ℹ️ ${name} is visible (Safe check)`);
            return true;
        } catch {
            if (this.logger) await this.logger(`⚠️ ${name} is NOT visible (Safe check) - Continuing...`);
            return false;
        }
    }

    async getTextSafe(element: Locator, name: string): Promise<string> {
        try {
            const text = await element.innerText({ timeout: 2000 });
            return text.trim();
        } catch {
            if (this.logger) await this.logger(`⚠️ Could not retrieve text from ${name}`);
            return "N/A";
        }
    }

    // Helper to just log
    async log(message: string) {
        if (this.logger) await this.logger(message);
    }
}