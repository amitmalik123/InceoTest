from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "username_input": page.locator(
            "input#okta-signin-username[name='username'][type='text'][aria-required='true']"
        ),
        "password_input": page.locator(
            "input#okta-signin-password[name='password'][type='password'][aria-required='true']"
        ),
        "sign_in_button": page.locator(
            "input#okta-signin-submit[type='submit'][value='Sign In']"
        ),
    }
