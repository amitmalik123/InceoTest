"""Locators for BAW login page."""


class BawLoginLocators:
    USERNAME_FIELD = "#username"
    PASSWORD_FIELD = "#password"
    SIGNIN_BUTTON = "//form[@id='signInForm']/a[@href='javascript:submitForm();']"
