import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class LoginPage {
  readonly page: Page;
  private fBrowser: BrowserActions;
  private fElement: ElementHelper;

  readonly logoAssetMark: Locator;
  readonly fUserName: Locator;
  readonly fPassword: Locator;
  readonly btnLogin: Locator;
  readonly btnOktaLogin: Locator;
  readonly errLoginBlank: Locator;
  readonly errLogin2: Locator;

  constructor(page: Page, logger: Logger) {
    this.page = page;
    this.fBrowser = new BrowserActions(page, logger);
    this.fElement = new ElementHelper(logger);

    this.logoAssetMark = page.getByAltText('logo');
    this.fUserName = page.locator('#okta-signin-username');
    this.fPassword = page.locator('#okta-signin-password');
    this.btnLogin = page.locator('#okta-signin-submit');
    this.btnOktaLogin = page.locator('#social-keycloak-oidc');

    this.errLoginBlank = page.locator('.icon.error-16', {
      hasText: 'We found some errors. Please review the form and make corrections.',
    });

    this.errLogin2 = page.locator('.icon.error-16', {
      hasText: 'The Username and/or password entered do not match our records. Please try again.',
    });
  }

  // ==========================================================
  // 🔐 Actions
  // ==========================================================
  async Login(user: string, pass: string) {
    await this.fElement.waitForElemVisible(this.fUserName, 'Username Field');

    await this.fElement.typeInField(this.fUserName, 'field Username', user);
    await this.fElement.typeInField(this.fPassword, 'field Password', pass);

    await this.fElement.log('⏳ Clicking Login and waiting for navigation...');

    await Promise.all([
      this.page.waitForNavigation({ waitUntil: 'networkidle' }),
      this.btnLogin.click(),
    ]);

    await this.fElement.log('✅ Login Submitted');
  }

  async ReLogin(user: string, pass: string) {
    const isLoginFieldVisible = await this.fUserName.isVisible({ timeout: 5000 });

    if (isLoginFieldVisible) {
      await this.fElement.log('ℹ️ Login page detected again. Proceeding with ReLogin.');

      await this.fElement.typeInField(this.fUserName, 'field Username', user);
      await this.fElement.typeInField(this.fPassword, 'field Password', pass);

      await Promise.all([
        this.page.waitForNavigation({ waitUntil: 'networkidle' }),
        this.btnLogin.click(),
      ]);
      await this.fElement.log('✅ ReLogin Submitted');

    } else {
      await this.fElement.log('ℹ️ User name field NOT visible. Skipping ReLogin.');
    }
  }

  async oktaLogin(user: string, pass: string) {
    const isVisible = await this.btnOktaLogin.isVisible({ timeout: 2000 });

    if (isVisible) {
      await this.fElement.log("ℹ️ Social login button found. Clicking...");
      await this.fElement.clickElem(this.btnOktaLogin, 'button Okta Login');
    } else {
      await this.fElement.log("ℹ️ Social login button not found. Proceeding with standard login.");
    }
  }

  // ==========================================================
  // 🔍 Validation Checks
  // ==========================================================
  async wrongUser(expectedError: string) {
    await this.fElement.waitForElemVisible(this.errLogin2, 'Login Error Message');

    const actual = await this.errLogin2.textContent();
    const cleanActual = actual?.trim();

    expect(cleanActual).toBe(expectedError);

    await this.fElement.log(`✅ Error Verified. Actual: "${cleanActual}" | Expected: "${expectedError}"`);
  }
}