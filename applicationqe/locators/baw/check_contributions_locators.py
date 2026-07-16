"""Locators for Check Contributions (CheckAttributesCV1) coach page."""


class CheckContributionsLocators:
    COACH_FRAME_SELECTOR = 'iframe[title="Coach"]'

    # XPath template for a Check Type <option>.
    # {idx} is the data-sheet-driven row number (1 = "A_PersonalCheck", etc.)
    XP_CHECK_TYPE_OPTION_TPL = (
        '//option[@id="singleselect-option-CheckAttributesCV1:CheckType[{idx}]"]'
    )

    # Default Check Type option index when no value is supplied.
    DEFAULT_CHECK_TYPE_INDEX = "1"

    # Calendar today cell (select_today_check_date)
    CALENDAR_TODAY_CELL = "xpath=//td[contains(@class,'today') or contains(@class,'Today')]"

    # Check Images Validation — System Result XPath candidates (use as list)
    SYSTEM_RESULT_XPATH_1 = (
        "xpath=//*[normalize-space(text())='System Result']"
        "/ancestor::tr[1]//td[normalize-space(.)"
        " and not(normalize-space(.)='System Result')][1]"
    )
    SYSTEM_RESULT_XPATH_2 = (
        "xpath=//*[normalize-space(text())='System Result']"
        "/following::*[self::span or self::div or self::td]"
        "[string-length(normalize-space(.))>0"
        " and normalize-space(.)!='System Result'][1]"
    )
    SYSTEM_RESULT_XPATH_3 = (
        "xpath=//*[contains(@id,'SystemResult')"
        " and not(contains(@id,'Label'))]"
        "[string-length(normalize-space(.))>0][1]"
    )

    # Description following locator
    DESCRIPTION_FOLLOWING = (
        "xpath=//*[normalize-space(.)='Description']"
        "/following::*[self::span or self::div or self::td or self::li or self::p]"
        "[string-length(normalize-space(.)) > 5][1]"
    )

    # Image Type select template (dynamic — use .format(row_index=...))
    IMAGE_TYPE_SELECT_XPATH_TPL = (
        'xpath=//select[@id="singleselect-CheckAttributesCV1'
        ':CheckImages_Table:ImageType[{row_index}]"]'
    )

    # Allocation Account select
    ALLOCATION_ACCOUNT_SELECT = (
        'xpath=//select[@id="singleselect-CheckAttributesCV1'
        ':Allocation_AccountNumber"]'
    )

    # Save & Close button candidates
    SAVE_CLOSE_BTN_HAS_TEXT_1 = "button:has-text('Save & Close')"
    SAVE_CLOSE_BTN_HAS_TEXT_2 = "button:has-text('Save and Close')"
