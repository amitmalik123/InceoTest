"""Locators for Edit Beneficiary Page elements."""


class EditBeneficiaryLocators:
    """Raw selector strings for the Edit Beneficiary page."""

    PAGE_TITLE = "span.MuiTypography-root.MuiCardHeader-title:has-text('Edit Beneficiary')"
    DONT_SAVE_BUTTON = "Don't Save"
    SAVE_BUTTON = "button.MuiButton-containedPrimary:has-text('Save')"
    BENEFICIARY_COMBOBOX = "xpath=//p[normalize-space(text())='Beneficiary']/following-sibling::div//div[@role='combobox']"
    FIRST_NAME_INPUT = "xpath=//p[normalize-space(text())='First Name']/following-sibling::div//input"
    MIDDLE_NAME_INPUT = "xpath=//p[contains(text(),'Middle Name')]/following-sibling::div//input"
    LAST_NAME_INPUT = "xpath=//p[normalize-space(text())='Last Name']/following-sibling::div//input"
    SSN_INPUT = "xpath=//p[contains(text(),'Social Security Number')]/following-sibling::div//input"
    DOB_INPUT = "input[placeholder='MM/DD/YYYY']"
    RELATIONSHIP_RADIO_GROUP = "xpath=//p[contains(text(),'Relationship to Account Holder')]/following-sibling::div//div[@role='radiogroup']"
    CUSTOM_REQUEST_LABEL = "xpath=//div[normalize-space(text())='Custom Request']"
    CUSTOM_REQUEST_CHECKBOX = "xpath=//div[normalize-space(text())='Custom Request']/parent::div/parent::div/span[contains(@class,'MuiCheckbox-root')]//input[@type='checkbox']"
    SUPPORTING_DOCS_FILE_INPUT = "xpath=(//h6[contains(text(),'Supporting Documentation')]/ancestor::div[1]//input[@type='file']) | (//p[contains(text(),'Supporting Documentation')]/ancestor::div[1]//input[@type='file'])"
