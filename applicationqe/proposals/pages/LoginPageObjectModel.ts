import { type Locator, type Page } from "@playwright/test";

export class LoginPage {
    readonly page: Page;
    readonly usernameInput: Locator;
    readonly passwordInput: Locator;
    readonly signInButton: Locator;
    readonly cookieAcceptButton: Locator;
    readonly privacyPolicyButton: Locator;
    readonly rejectAllButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.usernameInput = page.getByRole("textbox", { name: "Username" });
        this.passwordInput = page.getByRole("textbox", { name: "Password" });
        this.signInButton = page.getByRole("button", { name: "SIGN IN" });
        this.cookieAcceptButton = page.getByRole("button", {
            name: "Confirm My Choices",
        });
        this.privacyPolicyButton = page.getByRole("button", {
            name: "I Agree",
        });
        this.rejectAllButton = page.getByRole("button", { name: "Reject All" });
    }

    // Navigate to login page
    async gotoLoginPage() {
        await this.page.goto(process.env.loginURL);
        // Prefer waiting for a specific element instead of 'networkidle'
        await this.usernameInput.waitFor({ state: "visible" });
    }

    //Sign in with given username and password
    async signIn(username: string, password: string) {
        const env = process.env.ENVIRONMENT || process.env.Environment;
        if (env.toLowerCase() === "test10") {
            await this.cookieAcceptButton.waitFor({
                state: "visible",
                timeout: 5000,
            }); //waiting because it may load slowly
            if (await this.cookieAcceptButton.isVisible()) {
                await this.cookieAcceptButton.click();
            }
        }
        await this.usernameInput.fill(username);
        await this.passwordInput.fill(password);
        await this.signInButton.click();

        await Promise.race([
            this.privacyPolicyButton.waitFor({ state: "visible" }),
            this.page
                .getByText(`Welcome ${process.env.advisorName}`)
                .waitFor({ state: "visible" }),
            this.page
                .getByText("Choose a role to continue")
                .waitFor({ state: "visible" }),
        ]);
        if (await this.privacyPolicyButton.isVisible()) {
            await this.privacyPolicyButton.scrollIntoViewIfNeeded();
            await this.privacyPolicyButton.click();
        }
        // Wait for the sign-in button to disappear (navigation completed)
        await this.signInButton.waitFor({ state: "detached" });
    }

    // Handle privacy/cookie consent banner by clicking Reject All
    async rejectPrivacyBanner() {
        const env = process.env.ENVIRONMENT || process.env.Environment;
        if (env.toLowerCase() != "test10") {
            //change this to !=test10 if OKTA login in prod.
            try {
                await this.rejectAllButton.click({ timeout: 10000 });
            } catch (err) {
                // If the button is not found or not visible, log the error but continue
            }
        }
    }
}
