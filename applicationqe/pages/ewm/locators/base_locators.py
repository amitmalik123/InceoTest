"""Locators and constants shared across all EWM page objects."""


class BaseLocators:
    """Shared DOM selectors used by BasePage."""

    # Stable iframe ID used by the new EWM shell to embed the old application
    EWM_IFRAME_SELECTOR = "iframe#iframeWrapper"

    # OneTrust / Ketch cookie consent banner
    COOKIE_ACCEPT_BUTTON = "button.save-preference-btn-handler"
    COOKIE_OVERLAY = ".onetrust-pc-dark-filter"
