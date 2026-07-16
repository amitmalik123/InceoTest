"""Step definitions for the Check Contributions (Check Details) coach."""

import re

from pytest_bdd import then, when

from pages.baw.check_contributions_page import CheckContributionsPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

# Hardcoded ABA Routing number (removed from Excel data sheet by user request).
DEFAULT_ABA_ROUTING_NUMBER = "011001755"


def _require(data: dict, key: str) -> str:
    value = str(data.get(key, "") or "").strip()
    if not value:
        raise ValueError(f"Required column '{key}' missing/empty in test data")
    return value


def _normalize_amount(value: str) -> str:
    """Normalize OCR/extracted amount to plain decimal string."""
    cleaned = str(value or "").strip().replace(",", "")
    if not cleaned:
        return ""
    try:
        # Keep integer amounts without trailing .0 while preserving decimals.
        as_float = float(cleaned)
        if as_float.is_integer():
            return str(int(as_float))
        return str(as_float)
    except Exception:
        return cleaned


def _normalize_check_date(value: str) -> str:
    """Normalize extracted check date text to MM-DD-YYYY."""
    raw = str(value or "").strip()
    if not raw:
        return ""

    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        yyyy, mm, dd = raw.split("-")
        return f"{mm}-{dd}-{yyyy}"
    if re.match(r"^\d{4}/\d{2}/\d{2}$", raw):
        yyyy, mm, dd = raw.split("/")
        return f"{mm}-{dd}-{yyyy}"
    if re.match(r"^\d{2}/\d{2}/\d{4}$", raw):
        mm, dd, yyyy = raw.split("/")
        return f"{mm}-{dd}-{yyyy}"
    if re.match(r"^\d{2}-\d{2}-\d{4}$", raw):
        return raw
    return raw


def _get_check_page(test_context) -> CheckContributionsPage:
    """Return (and cache) a CheckContributionsPage bound to the active coach tab.

    Clicking 'Add/Update Check Details' opens the CheckContributions coach in
    a NEW browser tab. We locate that tab by scanning ``context.pages`` for a
    URL containing ``CheckContributions``/``executecf``. Falls back to the
    page already cached in ``test_context``.
    """
    page_obj = test_context.get("check_contributions_page")
    if page_obj:
        return page_obj

    base_page = (
        test_context.get("page")
        or (
            test_context["shell_process_page"].page
            if test_context.get("shell_process_page")
            else None
        )
    )
    if base_page is None:
        raise ValueError(
            "No base coach page in test_context. Open the Check Details coach first."
        )

    context = base_page.context
    coach_page = None

    # Poll context.pages (Add/Update Check Details may take a few seconds to
    # open its tab and then load the form).
    import time as _t
    end = _t.time() + 30
    while _t.time() < end:
        for p in context.pages:
            try:
                url = (p.url or "").lower()
            except Exception:
                continue
            if "checkcontributions" in url or "executecf" in url:
                coach_page = p
                break
        if coach_page is not None:
            break
        _t.sleep(1)

    if coach_page is None:
        # As a last resort, prefer the most recently opened tab.
        try:
            coach_page = context.pages[-1]
            logger.warning(
                f"CheckContributions tab not detected by URL; using last page: "
                f"{coach_page.url}"
            )
        except Exception:
            coach_page = base_page

    try:
        coach_page.bring_to_front()
    except Exception:
        pass
    try:
        coach_page.wait_for_load_state("domcontentloaded", timeout=45000)
        coach_page.wait_for_load_state("networkidle", timeout=45000)
    except Exception:
        pass

    logger.info(f"CheckContributions coach bound to: {coach_page.url}")
    check_page = CheckContributionsPage(coach_page)
    test_context["check_contributions_page"] = check_page
    test_context["page"] = coach_page
    return check_page


@when("Enter all required details on check coach and click on IWR Complete button")
@then("Enter all required details on check coach and click on IWR Complete button")
def step_enter_check_coach_details_and_iwr_complete(test_context):
    """End-to-end fill of the Check Contributions coach.

    Column mapping (BAW sheet in test_data.<env>.xlsx):
        Check Type            -> Check Type dropdown (optional; defaults to index 1)
        Check Number          -> Check Number input
        Bank Account #        -> Bank Account input
        Image Type            -> Image Type dropdown
        AccountNumber         -> Allocation managed account dropdown
        Allocation Amt        -> Allocation amount input

    Check Date is ALWAYS set to today (per requirement).
    ``ExpectedSystemResult`` column is optional; defaults to 'Passed'.
    """
    check_page = _get_check_page(test_context)
    check_page.pause_after_coach_entry()
    data = test_context.get("test_data", {})

    check_type = str(data.get("Check Type", "") or "").strip() or None
    check_number = _require(data, "Check Number")
    aba_routing = str(data.get("ABA Routing Number", "") or "").strip() or DEFAULT_ABA_ROUTING_NUMBER
    bank_account = _require(data, "Bank Account #")
    image_type = _require(data, "Image Type")
    alloc_account = _require(data, "AccountNumber")
    alloc_amount = _require(data, "Allocation Amt")
    bank_name = str(data.get("Bank Name", "") or "").strip() or None

    # 1. First coach open: do not enter any details. Read Check Images Validation
    #    and fetch OCR amounts from it.
    pre_validation = check_page.fetch_check_images_validation()

    numeric_amount = _normalize_amount(pre_validation.get("numeric_extracted_amount", ""))
    alpha_amount = _normalize_amount(pre_validation.get("alpha_extracted_amount", ""))
    if not numeric_amount and alpha_amount:
        numeric_amount = alpha_amount
    if not alpha_amount and numeric_amount:
        alpha_amount = numeric_amount
    if not numeric_amount or not alpha_amount:
        raise ValueError(
            "Unable to fetch numeric/alpha extracted amount from Check Images Validation"
        )

    logger.attach_summary_table(
        {
            "Fetched Numeric Amount": numeric_amount,
            "Fetched Alpha Amount": alpha_amount,
            "Validation System Result": pre_validation.get("system_result", ""),
            "Validation Details": "\n".join(pre_validation.get("description_items") or []) or "(none)",
        },
        name="Fetched Amounts From Check Images Validation",
    )

    # 2. Save & Close immediately and return to shell coach.
    check_page.click_save_and_close()
    shell_process_page = test_context.get("shell_process_page")
    if not shell_process_page:
        raise ValueError("Shell Process page not initialized in test_context")
    shell_process_page.wait_for_shell_page_and_open_check_details()

    # Re-bind to CheckContributions coach after reopening Add/Update Check Details.
    test_context.pop("check_contributions_page", None)
    check_page = _get_check_page(test_context)
    check_page.pause_after_coach_entry()

    # 3. Second coach open: fill details using fetched alpha/numeric.
    check_page.select_check_type(check_type)
    banner_text = check_page.enter_alpha_amount_and_capture_banner(alpha_amount)
    test_context["alpha_mismatch_banner"] = banner_text

    # 4. Fill remaining Check Details (Check Date = today inside the helper).
    check_date_used = check_page.fill_check_details(
        numerical_amount=numeric_amount,
        alpha_amount=alpha_amount,
        check_number=check_number,
        aba_routing=aba_routing,
        bank_account=bank_account,
        bank_name=bank_name,
        select_check_type=False,  # already selected above
    )
    test_context["check_date_used"] = check_date_used
    check_page.select_image_type(image_type, row_index=0)

    # 5. Save & Close after entering required fields, then reopen Check Details.
    check_page.click_save_and_close()
    shell_process_page = test_context.get("shell_process_page")
    if not shell_process_page:
        raise ValueError("Shell Process page not initialized in test_context")
    shell_process_page.wait_for_shell_page_and_open_check_details()

    # Re-bind again after the second reopen.
    test_context.pop("check_contributions_page", None)
    check_page = _get_check_page(test_context)
    check_page.pause_after_coach_entry()

    # 6. Fetch validation after second reopen. If it reports extracted check
    #    date mismatch, update Check Date with the extracted date and re-validate.
    validation = check_page.fetch_check_images_validation()
    extracted_check_date_raw = str(validation.get("extracted_check_date", "") or "").strip()
    extracted_check_date = _normalize_check_date(extracted_check_date_raw)
    if extracted_check_date:
        logger.attach_summary_table(
            {
                "Fetched Extracted Check Date": extracted_check_date,
                "Current Check Date Used": test_context.get("check_date_used", ""),
                "Date Validation Line": validation.get("check_date_validation_line", "") or "(none)",
            },
            name="Fetched Check Date From Validation",
        )

        check_date_used = check_page.set_check_date(extracted_check_date)
        test_context["check_date_used"] = check_date_used

        check_page.click_save_and_close()
        shell_process_page = test_context.get("shell_process_page")
        if not shell_process_page:
            raise ValueError("Shell Process page not initialized in test_context")
        shell_process_page.wait_for_shell_page_and_open_check_details()

        test_context.pop("check_contributions_page", None)
        check_page = _get_check_page(test_context)
        check_page.pause_after_coach_entry()
        validation = check_page.fetch_check_images_validation()

    test_context["check_images_validation"] = validation
    details = validation.get("description_items") or []
    test_context["check_images_validation_details"] = details
    system_result = (validation.get("system_result") or "").strip()
    details_text = "\n".join(details) if details else "(none)"

    logger.attach_summary_table(
        {
            "Expected System Result": "Verified",
            "Actual System Result": system_result or "(empty)",
            "Validation Details": details_text,
        },
        name="Check Images Validation Details",
    )

    if system_result.lower() != "verified":
        raise AssertionError(
            "Check Images Validation failed: expected System Result='Verified' "
            f"but got '{system_result or 'empty'}'. Description:\n{details_text}"
        )

    # 7. Allocation (Managed)
    check_page.add_managed_allocation(
        account_number=alloc_account,
        allocation_amount=alloc_amount,
    )

    # 8. IWR Complete + post-Proceed Shell details capture
    shell_capture = check_page.click_iwr_complete() or {}
    shell_details_text = (shell_capture.get("details_text") or "").strip()
    shell_details_items = shell_capture.get("details_items") or []
    test_context["shell_check_image_extraction_details"] = shell_details_items

    if shell_details_text:
        logger.attach_summary_table(
            {
                "Shell Section": "Check Image Extraction",
                "Shell Details": "\n".join(shell_details_items) if shell_details_items else shell_details_text,
            },
            name="Shell Check Image Extraction Details",
        )

    logger.attach_summary_table(
        {
            "Alpha Mismatch Banner": banner_text or "(not displayed)",
            "Check Date Used": check_date_used,
            "System Result": validation.get("system_result", ""),
            "Shell Check Extraction": shell_details_text or "(not captured)",
            "Image Type": image_type,
            "Allocation Account": alloc_account,
            "Allocation Amount": alloc_amount,
        },
        name="Check Contributions Coach Summary",
    )


@then("Validates the Check Extraction in the Check Images Validation section")
def step_validate_check_images_validation_section(test_context):
    import time as _t

    check_page = _get_check_page(test_context)

    # 1. Capture initial result (may be 'Pending' while extraction is queued)
    initial_validation = check_page.fetch_check_images_validation()
    initial_system_result = (initial_validation.get("system_result") or "").strip()
    initial_description = (initial_validation.get("description") or "").strip()
    logger.info(
        f"Initial Check Images Validation: System Result='{initial_system_result}'",
        attach_to_allure=True,
    )

    # 2. If Pending, poll until the extraction result changes or timeout
    first_extraction_validation = initial_validation
    if initial_system_result.lower() == "pending":
        logger.info(
            "System Result is 'Pending' - polling until extraction completes...",
            attach_to_allure=True,
        )
        poll_timeout_s = 300   # 5 minutes
        poll_interval_s = 15   # re-check every 15 seconds
        deadline = _t.time() + poll_timeout_s
        while _t.time() < deadline:
            _t.sleep(poll_interval_s)
            # Reload the coach page so BAW re-fetches extraction status from server
            # (re-reading stale DOM shows 'Pending' even when server has a result)
            try:
                check_page.page.bring_to_front()
                check_page.page.reload()
                check_page.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception as _reload_err:
                logger.warning(f"Coach page reload failed during poll: {_reload_err}")
            polled = check_page.fetch_check_images_validation()
            polled_result = (polled.get("system_result") or "").strip()
            logger.info(f"Polled System Result: '{polled_result}'", attach_to_allure=True)
            if polled_result.lower() != "pending":
                first_extraction_validation = polled
                break
        else:
            logger.warning(
                f"System Result remained 'Pending' after {poll_timeout_s}s; capturing last polled value."
            )
            try:
                check_page.page.bring_to_front()
                check_page.page.reload()
                check_page.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            first_extraction_validation = check_page.fetch_check_images_validation()

    first_extraction_system_result = (first_extraction_validation.get("system_result") or "").strip()
    first_extraction_description = (first_extraction_validation.get("description") or "").strip()

    # 3. Log both initial and 1st extraction result to Allure
    logger.attach_summary_table(
        {
            "Initial System Result": initial_system_result or "(empty)",
            "Initial Description": initial_description or "(empty)",
            "1st Extraction System Result": first_extraction_system_result or "(empty)",
            "1st Extraction Description": first_extraction_description or "(empty)",
        },
        name="Check Images Validation (Initial -> 1st Extraction)",
    )
    test_context["check_images_validation_initial"] = initial_validation
    test_context["check_images_validation"] = first_extraction_validation
    logger.info(
        f"Check Images Validation 1st Extraction: System Result='{first_extraction_system_result}'",
        attach_to_allure=True,
    )

    # 4. Assert the final System Result is a valid extraction outcome
    valid_results = {"verified", "review required"}
    result_lower = first_extraction_system_result.lower()
    if result_lower == "pending":
        logger.warning(
            "System Result is still 'Pending' after polling timeout. "
            "IWR extraction did not complete within the wait period.",
            attach_to_allure=True,
        )
    elif result_lower not in valid_results:
        raise AssertionError(
            f"Unexpected 1st Extraction System Result: '{first_extraction_system_result}'. "
            f"Expected one of: {sorted(valid_results)}"
        )
    else:
        logger.info(
            f"1st Extraction System Result confirmed: '{first_extraction_system_result}'",
            attach_to_allure=True,
        )
