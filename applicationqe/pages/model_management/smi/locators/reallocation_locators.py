DIALOG_SELECTORS = [
    'div[role="dialog"]',
    'div.ui-dialog',
    '.modal',
    '.popup',
    'div.dialog',
]

# Select Company/Strategist popup
POPUP_DROPDOWN = 'div[role="dialog"] select, div.ui-dialog select'

# New Reallocation form: Model search
MODEL_SEARCH_BUTTON = (
    'input[type="image"][alt*="earch" i], '
    'input[type="button"][value*="earch" i], '
    'button[title*="earch" i], '
    'a[title*="earch" i], '
    'input[name*="earch" i][type="button"], '
    'input[id*="earch" i][type="image"]'
)
MODEL_ID_INPUT = (
    'input[name*="odel" i][type="text"], '
    'input[id*="odel" i][type="text"]'
)

POPUP_SUBMIT_BUTTON = (
    'div[role="dialog"] input[type="submit"], '
    'div.ui-dialog input[type="submit"], '
    'div[role="dialog"] button[type="submit"], '
    'div.ui-dialog button[type="submit"], '
    'div[role="dialog"] input[type="button"][value="OK"], '
    'div.ui-dialog input[type="button"][value="OK"], '
    '.ui-dialog-buttonset button, '
    'div[role="dialog"] button'
)
