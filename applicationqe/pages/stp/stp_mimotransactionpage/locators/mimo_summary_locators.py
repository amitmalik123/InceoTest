"""Locators for MIMO Summary Page elements."""


class MIMOSummaryLocators:
    """Raw selector strings for the MIMO Summary page."""

    TRANSACTION_SUMMARY_TITLE = "//h3[@class='section-title' and text()='Transaction summary']"
    SUBMIT_BUTTON = "//button[@data-testid='submit-button']"
    SUBMIT_REVIEW_BUTTON = "//button[@data-testid='submit-to-review-button']"
    BACK_BUTTON = "//button[@data-testid='back-button']"
    QUALIFIED_INFO_VALUES = "//h3[text()='QUALIFIED INFORMATION']//parent::div//div[@aria-label='category-group-item']//h4[@aria-label='category-group-item-value']"
