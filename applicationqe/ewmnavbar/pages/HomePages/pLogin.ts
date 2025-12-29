
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible, typeinField, waitForElem } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;


export class LoginPage {
  readonly page: Page;
  private logger: Logger;
  readonly logoAssetMark: Locator;
  readonly fUserName: Locator;
  readonly fPassword: Locator;
  readonly btnLogin: Locator;
  readonly btnOktaLogin: Locator;
  readonly errLoginBlank: Locator;
  readonly errLogin2: Locator;
  // readonly smOne: Locator;

  constructor(page: Page, logger: Logger) {
    this.page = page;
    this.logger = logger;
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

  async Login(user: string, pass: string) {
    await waitForElem(this.fUserName, 'field Username', this.logger);
    await typeinField(this.fUserName, 'field Username', user, this.logger);
    await typeinField(this.fPassword, 'field Password', pass, this.logger);
    await Promise.all([
      this.page.waitForNavigation({ waitUntil: 'networkidle' }),
      this.btnLogin.click(),
    ]);
  }

  async ReLogin(user: string, pass: string) {
    const isLoginFieldVisible = await this.fUserName.isVisible({ timeout: 50000 });

    if (isLoginFieldVisible) {
      console.log('Page came up for Login again. Proceeding with ReLogin.');

      await this.fUserName.fill(user);
      await this.fPassword.fill(pass);

      await Promise.all([
        this.page.waitForNavigation({ waitUntil: 'networkidle' }),
        this.btnLogin.click(),
      ]);

    } else {
      console.log('User name field is NOT visible. Skipping ReLogin steps.');

    }
  }

  async oktaLogin(user: string, pass: string) {

    const isVisible = await this.btnOktaLogin.isVisible({ timeout: 500 });

    if (isVisible) {
      await this.logger("Social login button found, clicking it.");
      await this.btnOktaLogin.click();
    } else {
      await this.logger("Social login button not found, proceeding with the standard login flow.");
    }
  }

  async wrongUser(expectedError: string) {
    await elemVisible(this.errLogin2, 'Login Error Message', this.logger);
    const actual = await this.errLogin2.textContent();
    expect(actual?.trim()).toBe(expectedError);
    await this.logger('Message Actual = ' + actual);
    await this.logger('Message Expected = ' + expectedError);
  }
}
