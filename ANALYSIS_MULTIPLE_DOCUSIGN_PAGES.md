# Analysis: Multiple DocuSign Page Objects Issue

## Problem Summary
The error "Review and Continue dialog not found - [aria-label="Review and continue"]" occurs because the verification step is checking on the **wrong DocuSignPage object**. Two different DocuSign page wrapper objects are created during the workflow, pointing to different underlying Playwright pages.

---

## 1. EXACT CODE: verify_docusign_review_and_continue_dialog_text Function

**File:** [tests/bdd/steps/docusign_steps.py](tests/bdd/steps/docusign_steps.py#L129-L195)

```python
@then(parsers.parse('Verify docusign Review and continue dialog text "{expected_text}"'))
def verify_docusign_review_and_continue_dialog_text(authenticated_page: Page, docusign_page, expected_text: str):
    """Verify the Review and Continue dialog text matches expected value from feature file.
    
    Takes expected text as a parameter from the feature file step
    and verifies it matches the text fetched from the dialog using soft assertions.
    
    Args:
        authenticated_page: Playwright Page object for screenshots
        docusign_page: DocuSignPage fixture for DocuSign interactions
        expected_text: Expected dialog text passed from feature file step
    
    Uses framework utilities:
    - docusign_page.fetch_docusign_review_and_continue_dialog_text(): Fetches dialog text
    - SoftAssertions: Non-blocking assertions that collect failures
    - Framework logging via setup_logger
    """
    logger.info(">>> ENTERED STEP: verify_docusign_review_and_continue_dialog_text")
    logger.info(f"Expected text from feature file: '{expected_text}'")
    
    if not expected_text:
        raise ValueError("Expected text parameter is required for this step")
    
    with allure.step("Verify Review and Continue dialog text"):
        logger.info(f"Expected text from test data: '{expected_text}'")
        
        # STEP 1: Fetch the dialog text using page object method
        logger.info("Step 1: Fetching dialog text...")
        try:
            actual_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
            logger.info(f"Step 1: Dialog text fetched successfully: '{actual_text}'")
        except Exception as e:
            logger.error(f"✗ Failed to fetch dialog text: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Fetch Failed", attachment_type=allure.attachment_type.PNG)
            except:
                pass
            raise
        
        # STEP 2: Use SoftAssertions to verify text matches expected value
        logger.info("Step 2: Verifying dialog text using soft assertions...")
        soft_assert = SoftAssertions()
        soft_assert.assert_equal(
            actual_text,
            expected_text,
            message=f"[FAIL] DocuSignPage: Review and Continue Dialog Text — Expected: '{expected_text}', Actual: '{actual_text}'. Details: Review and Continue dialog text must match expected value from test data. Locator: p[data-qa='email-message-content']."
        )
        
        # STEP 3: Verify soft assertions
        logger.info("Step 3: Verifying soft assertions...")
        try:
            soft_assert.assert_all()
            logger.info(f"[PASS] DocuSignPage: Dialog Text Verification Completed.")
        except Exception as soft_assert_error:
            logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
            allure.attach(
                str(soft_assert_error),
                name="Review and Continue Dialog - Text Verification Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        # STEP 4: Take screenshot for Allure reporting
        logger.info("Step 4: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="DocuSign Review and Continue Dialog - Text Verified", attachment_type=allure.attachment_type.PNG)
        
        logger.info("✓ Review and Continue dialog text verification passed")
```

---

## 2. EXACT CODE: user_click_review_document_and_submit_opt() Step

**File:** [tests/bdd/steps/docusign_steps.py](tests/bdd/steps/docusign_steps.py#L331-L410)

```python
@when("User click on Review Document and submit the otp")
def user_click_review_document_and_submit_opt(authenticated_page: Page, docusign_page, test_context):
    """Click on Review Document link and submit OTP for document signing.
    
    This step performs the complete end-to-end OTP verification and DocuSign signing workflow:
    1. Click the Review Document link in the authorized signer email (opens DocuSign in new tab)
    2. Perform OTP verification from Outlook and submit to DocuSign
    3. Complete the document signing process
    
    The Outlook page is expected to already be open from the prior step
    'User login to the email and search the authorized signer email' which
    searches for and opens the authorized signer email.
    
    Args:
        authenticated_page: Playwright Page object for the main DocuSign page (not used in this flow)
        docusign_page: DocuSignPage fixture for DocuSign interactions
        test_context: Test context dictionary containing the stored outlook_email_page
        
    Workflow:
        1. Retrieve stored outlook_email_page from test_context (created in previous step)
        2. Click 'Review Document' link in email, opens DocuSign in new tab
        3. Retrieve OTP from Outlook and submit to DocuSign
        4. Complete OTP verification and signing process
    """
    logger.info(">>> ENTERED STEP: user_click_review_document_and_submit_opt")
    
    with allure.step("User perform advisor signature 'by mail' method"):
        try:
            # Retrieve the stored outlook email page from test_context
            # This was created and stored by the previous step:
            # "User login to the email and search the authorized signer email"
            outlook_email_page = test_context.get("outlook_email_page")
            if not outlook_email_page:
                raise ValueError(
                    "outlook_email_page not found in test_context. "
                    "Ensure the step 'User login to the email and search the authorized signer email' "
                    "runs before this step to create and store the email page."
                )
            
            # Verify the page is still open before proceeding
            if outlook_email_page.is_closed():
                raise RuntimeError(
                    "outlook_email_page has been closed. "
                    "The page must remain open between steps for this workflow."
                )
            
            logger.info("Retrieved stored outlook_email_page from test_context")
            
            # STEP 1: Click Review Document link in the email to open DocuSign in new tab
            logger.info("STEP 1: Clicking 'Review Document' link in authorized signer email...")
            
            # Bring the Outlook email page to the foreground
            outlook_email_page.bring_to_front()
            logger.info("Brought outlook email page to foreground")
            
            # Click the REVIEW DOCUMENT link which opens DocuSign in a new page context
            review_link = outlook_email_page.get_by_role("link", name="REVIEW DOCUMENT")
            review_link.wait_for(timeout=15000)
            
            # Get the new page that opens when we click the link
            with outlook_email_page.context.expect_page() as new_page_info:
                review_link.click()
                new_docusign_page = new_page_info.value
            
            logger.info("[PASS] DocuSign page opened from email 'Review Document' link")
            
            # STEP 2: Create DocuSignPage wrapper around the new page for OTP workflow
            logger.info("STEP 2: Initializing DocuSignPage object for new DocuSign tab...")
            new_docusign_page_obj = DocuSignPage(new_docusign_page)
            logger.info("[PASS] DocuSignPage object initialized")
            
            # STEP 3: Perform OTP verification and signing workflow
            # This retrieves OTP from Outlook and submits it to DocuSign
            logger.info("STEP 3: Initiating OTP verification and signing workflow...")
            new_docusign_page_obj.otp_verification(outlook_page=outlook_email_page)
            logger.info("[PASS] OTP verification and signing workflow completed")
            
            logger.info("[PASS] DocuSignPage: Advisor Signature 'By Mail' Method Completed Successfully.")
            
        except Exception as e:
            logger.error(f"[FAIL] Advisor signature 'by mail' workflow failed: {str(e).splitlines()[0]}")
            allure.attach(
                str(e),
                name="Advisor Signature 'By Mail' - Error Details",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
```

---

## 3. Where DocuSignPage Objects Are Instantiated

### **Instance 1: Fixture (Original Page)**
**File:** [tests/fixtures/page_fixtures.py](tests/fixtures/page_fixtures.py#L61-L63)

```python
@pytest.fixture
def docusign_page(authenticated_page: Page) -> DocuSignPage:
    """DocuSign page object fixture"""
    return DocuSignPage(authenticated_page, base_url=_base_url)
```

- **Created:** Once per test, at fixture initialization
- **Wrapped Page:** `authenticated_page` (the original application page)
- **Scope:** Function-scoped (available for all steps in the test)
- **Used In:** Steps like `user_should_be_redirected_to_docusign_page`, `verify_docusign_review_and_continue_dialog_text`

### **Instance 2: NEW Page in Step**
**File:** [tests/bdd/steps/docusign_steps.py](tests/bdd/steps/docusign_steps.py#L385-L390)

```python
# In user_click_review_document_and_submit_opt():

# Click the REVIEW DOCUMENT link which opens DocuSign in a new page context
review_link = outlook_email_page.get_by_role("link", name="REVIEW DOCUMENT")
review_link.wait_for(timeout=15000)

# Get the new page that opens when we click the link
with outlook_email_page.context.expect_page() as new_page_info:
    review_link.click()
    new_docusign_page = new_page_info.value

# STEP 2: Create DocuSignPage wrapper around the new page for OTP workflow
new_docusign_page_obj = DocuSignPage(new_docusign_page)
```

- **Created:** During `user_click_review_document_and_submit_opt` step execution
- **Wrapped Page:** `new_docusign_page` (a NEW page that opens in a new browser tab/context)
- **Scope:** Local to the step (not persisted to test_context or fixture)
- **Used In:** OTP verification workflow via `new_docusign_page_obj.otp_verification()`

### **Instance 3: Alternative Creation in OutlookPage**
**File:** [pages/outlook_page.py](pages/outlook_page.py#L1095-L1148)

```python
def click_review_document_link(self, outlook_email_page: Page) -> Page:
    """Click the 'REVIEW DOCUMENT' link in the authorized signer email..."""
    with outlook_email_page.expect_popup() as popup_info:
        review_link = outlook_email_page.get_by_role("link", name="REVIEW DOCUMENT")
        review_link.wait_for(state="visible", timeout=10_000)
        review_link.click()
    
    docusign_page = popup_info.value
    
    # Lazy import to avoid circular import
    from pages.docusign_page import DocuSignPage
    
    docusign_page = DocuSignPage(docusign_page)
```

- Could create another DocuSignPage if used
- Currently NOT used in the OAM workflow

---

## 4. DocuSignPage __init__ Code

**File:** [pages/docusign_page.py](pages/docusign_page.py#L30-L45)

```python
class DocuSignPage(BasePage):
    """Page object for DocuSign signing page"""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self._initialize_locators()
        self._last_send_now_epoch = None
    
    def _initialize_locators(self) -> None:
        """Initialize all locator properties for Send Now and Resend Code buttons."""
        # Send Now button with multiple locator strategies
        self.send_now_button = self.page.locator('button[data-qa*="send-now"]')
        self.send_now_button_by_role = self.page.get_by_role("button", name=docusign_locators.SEND_NOW_BUTTON_PATTERN)
        self.send_now_button_text = self.page.get_by_text(docusign_locators.SEND_NOW_BUTTON_PATTERN)
        
        # Resend Code button with multiple locator strategies
        self.resend_code_button = self.page.locator('button[data-qa*="resend-code"]')
        self.resend_code_primary_button = self.page.get_by_role("button", name=docusign_locators.RESEND_CODE_BUTTON_PATTERN)
```

Each DocuSignPage instance is bound to a single Playwright `page` object passed in the constructor.

---

## 5. The fetch_docusign_review_and_continue_dialog_text Method

**File:** [pages/docusign_page.py](pages/docusign_page.py#L263-L310)

```python
def fetch_docusign_review_and_continue_dialog_text(self, timeout: int = 10000) -> str:
    """
    Fetch the text from the 'Review and continue' dialog.
    
    Locates the dialog by aria-label, then extracts text from p tag with data-qa attribute.
    Returns the text content for assertion/verification in calling code.
    
    Args:
        timeout: Maximum time to wait in milliseconds
        
    Returns:
        The text content from the dialog's content element (stripped)
        
    Raises:
        AssertionError: If dialog or content element not found
        
    Example:
        dialog_text = docusign_page.fetch_docusign_review_and_continue_dialog_text()
        # Use assertions on the returned text in calling code
    """
    logger.info("Fetching DocuSign Review and Continue dialog text...")
    
    # Locate the dialog by aria-label
    dialog_locator = self.page.locator(docusign_locators.REVIEW_CONTINUE_DIALOG)
    
    # Verify dialog is present
    try:
        dialog_locator.wait_for(state="visible", timeout=timeout)
        logger.info("✓ Review and Continue dialog is present")
    except:
        logger.error("✗ Review and Continue dialog not found")
        raise AssertionError('[FAIL] DocuSignPage: Review and Continue Dialog Presence — Expected: dialog with aria-label="Review and continue" found, Actual: dialog not found. Details: Review and Continue dialog must be visible. Locator: [aria-label="Review and continue"].')
    
    # Get the text from the p tag with data-qa="email-message-content"
    content_locator = dialog_locator.locator(docusign_locators.DIALOG_CONTENT_P_TAG)
    
    # Wait for content to be visible
    try:
        content_locator.wait_for(state="visible", timeout=timeout)
        logger.debug("Content p tag is visible")
    except:
        logger.error("✗ Content p tag not found within the dialog")
        raise AssertionError('[FAIL] DocuSignPage: Dialog Content Element — Expected: p[data-qa="email-message-content"] found, Actual: element not found. Details: Content element must exist in the Review and Continue dialog. Locator: p[data-qa="email-message-content"].')
    
    # Get the actual text
    dialog_text = (content_locator.text_content() or "").strip()
    logger.info(f"✓ Dialog text fetched: '{dialog_text}'")
    
    return dialog_text
```

**Key:** It searches for the dialog on `self.page` - the page this DocuSignPage instance is bound to.

---

## 6. Timeline: When Each Object Is Created

### **OAM Scenario (Authorized Signer eSign Method)**

| Time | Object | Event | Page Binding |
|------|--------|-------|--------------|
| 1 | `docusign_page` (fixture) | Fixture initialized at test start | `authenticated_page` (original app) |
| 2 | `authenticated_page` | User redirects to DocuSign | Original DocuSign URL |
| 3 | `docusign_page` method called | ✅ `verify_docusign_review_and_continue_dialog_text` | ✅ Searches on `authenticated_page` |
| 4 | SUCCESS | Dialog found and verified | Dialog exists on original page |

**Note:** In this flow, the dialog verification happens on the original `authenticated_page` which works correctly.

### **Authorized Signer "By Mail" Scenario (OTP Flow)**

| Time | Object | Event | Page Binding |
|------|--------|-------|--------------|
| 1 | `docusign_page` (fixture) | Fixture initialized at test start | `authenticated_page` (original app) |
| 2 | `outlook_email_page` | Email opened in new page | Outlook URL |
| 3 | Click "Review Document" | NEW page opens for DocuSign | NEW DocuSign page in new tab |
| 4 | `new_docusign_page_obj` | Step creates wrapper | NEW DocuSign page |
| 5 | `new_docusign_page_obj.otp_verification()` | OTP flow runs on NEW page | ✅ Correct page |
| **6** | **`verify_docusign_review_and_continue_dialog_text`** | **Step calls with fixture `docusign_page`** | **❌ WRONG: Original `authenticated_page`** |
| **FAIL** | Dialog not found | Searching on original page, not new page | Dialog is on NEW page, not original |

---

## 7. The Root Cause

### **Problem:**
- `verify_docusign_review_and_continue_dialog_text` always uses the `docusign_page` fixture
- This fixture is bound to the ORIGINAL `authenticated_page` from the start of the test
- In the "By Mail" scenario, a NEW page opens when "Review Document" is clicked
- The dialog appears on the NEW page, not the original
- The verification step tries to find the dialog on the WRONG page

### **Why It Works in Scenario 1:**
- No new page is opened
- The user goes directly through the app to DocuSign
- The dialog appears on the original page
- The fixture is bound to the correct page

### **Why It Fails in Scenario 2:**
- A new page (tab) opens for DocuSign
- The dialog appears on this NEW page
- The fixture still points to the ORIGINAL page
- The verification step can't find the dialog

---

## 8. Comparison: dialogPage vs docusign_page

**They are NOT different objects - they are the same concept:**
- `dialogPage` - generic term for any page object handling dialogs
- `docusign_page` - specific fixture wrapping `DocuSignPage` class around a page

**In the codebase:**
- Only `docusign_page` fixture exists (not `dialogPage`)
- Both refer to a DocuSignPage wrapper around a Playwright Page

---

## 9. Key Insights

1. **DocuSignPage is a wrapper class**, not the page itself
   - It wraps a Playwright `Page` object
   - Multiple instances can exist, each bound to a different page
   - Each instance searches for elements on its bound page

2. **The fixture is created once per test**, bound to the original page
   - Reusing it after a new page opens causes context mismatch
   - The new page is in `new_docusign_page` variable, lost after step completes

3. **No persistence of new_docusign_page_obj**
   - It's a local variable in the step function
   - Not stored in `test_context` or accessible to subsequent steps
   - When the next step runs, only the fixture is available

4. **test_context could solve this**
   - The "By Mail" step is NOT storing `new_docusign_page_obj` in `test_context`
   - Comparison steps that run later have no way to access the correct page object

