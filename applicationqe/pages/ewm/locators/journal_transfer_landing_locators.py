# locators/journal_transfer_landing_locators.py

"""
Locators for Journal Transfer page
"""

import json
from pathlib import Path


def _load_test_data(scenario_name: str = "journal_portion_transfer_standard1") -> dict:
    data_file = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "stp"
        / "stp_journals"
        / "journal_transfer_test_data.json"
    )
    with open(data_file, "r") as handle:
        data = json.load(handle)

    for scenario in data.get("testScenarios", []):
        if scenario.get("name") == scenario_name:
            return scenario

    raise ValueError(f"Scenario '{scenario_name}' not found in test data")


_TEST_DATA = _load_test_data()


class JournalTransferLocators:
    """Selectors for journal transfer page elements"""

    # Page title
    PAGE_TITLE = _TEST_DATA["expectedResults"]["pageTitle"]

    # Destination account selection
    DESTINATION_ACCOUNT_LISTITEM = {
        "text": _TEST_DATA["accounts"]["destinationAccountName"]
    }

    DESTINATION_ACCOUNT_BUTTON = {
        "role": "button"
    }

    # Investment account details confirmation
    INVESTMENT_ACCOUNT_DETAILS = {
        "text": _TEST_DATA["uiText"]["investmentAccountDetails"]
    }

    # Navigation buttons
    NEXT_BUTTON = {
        "role": "button",
        "name": _TEST_DATA["uiText"]["nextButton"]
    }

    NEXT_BUTTON_LAST = {
        "role": "button",
        "name": _TEST_DATA["uiText"]["nextButton"]  # Last occurrence
    }

    # Distribution options
    JOURNAL_PORTION_RADIO = {
        "role": "radio",
        "name": _TEST_DATA["transactionDetails"]["distributionType"]
    }

    # Amount input field
    AMOUNT_INPUT = {
        "role": "textbox"
    }

    # Approximate percentage indicator
    APPROX_PERCENTAGE = {
        "text": _TEST_DATA["uiText"]["approxText"]
    }

    # Signature selection
    NO_SIGNATURE_RADIO = {
        "role": "radio",
        "name": _TEST_DATA["transactionDetails"]["signatureOption"]
    }

    # Request summary page
    REQUEST_SUMMARY = {
        "text": _TEST_DATA["uiText"]["requestSummary"]
    }

    REQUEST_TYPE_LABEL = {
        "text": _TEST_DATA["uiText"]["requestTypeLabel"]
    }

    JOURNAL_TEXT = {
        "text": _TEST_DATA["uiText"]["journalText"],
        "exact": True
    }

    PORTION_AMOUNT = {
        "text": _TEST_DATA["expectedResults"]["amountDisplay"]
    }

    # Submit buttons
    SUBMIT_TO_REVIEW_BUTTON = {
        "role": "button",
        "name": _TEST_DATA["uiText"]["submitToReview"]
    }

    SUBMIT_BUTTON = {
        "role": "button",
        "name": _TEST_DATA["uiText"]["submit"]
    }

    # Confirmation messages
    REQUEST_SUBMITTED_SUCCESS = {
        "text": _TEST_DATA["expectedResults"]["confirmationText"]
    }

    IN_PROCESS_STATUS = {
        "text": _TEST_DATA["expectedResults"]["status"]
    }

    ITEM_NUMBER_LABEL = {
        "text": _TEST_DATA["uiText"]["itemNumberLabel"]
    }

    # Item number pattern
    ITEM_NUMBER_PATTERN = _TEST_DATA["patterns"]["itemNumberRegex"]

    # Tracking center indicators
    TRACKING_CENTER_PAGE = _TEST_DATA["patterns"]["trackingCenterItemRegex"]
    TRACKING_STATUS_PATTERN = _TEST_DATA["patterns"]["trackingStatusRegex"]
    TRACKING_REQUEST_TYPE_TEXT = _TEST_DATA["uiText"]["trackingCenterRequestType"]

    # Alert/warning locators
    ALERT_WARNING = {
        "css": "[role='alert'], .alert, .warning"
    }
    NETWORK_IDLE_TIMEOUT = 30000
    ELEMENT_TIMEOUT = 3000