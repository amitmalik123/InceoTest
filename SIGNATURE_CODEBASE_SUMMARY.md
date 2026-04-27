# Signature-Related Functionality - Comprehensive Codebase Summary

## Overview
This document provides a complete inventory of all signature-related functionality in the QE Automation project, including eSignature workflows, DocuSign integration, authorized signer management, and OTP verification.

---

## 1. PAGE OBJECTS FOR SIGNATURE OPERATIONS

### 1.1 DocuSign Page Object
**File:** [pages/docusign_page.py](pages/docusign_page.py)  
**Purpose:** Handles all DocuSign signing interface interactions

#### Key Methods:
- `verify_docusign_page_loaded(timeout=60000)` - Wait and verify DocuSign page loads
- `submit_otp(otp_code)` - Submit OTP code to verification field
- `check_ersd_consent_checkbox()` - Check Electronic Record and Signature Disclosure consent
- `click_ersd_continue_button(timeout=10000)` - Click ERSD Continue button
- `click_finish_button(timeout=10000)` - Click Finish button to complete signing
- `click_sign_button()` - Click on Sign button/div in document
- `get_stamping_element(stamping_text)` - Get locator for stamping element (e.g., "As authorized by")
- `fetch_docusign_review_and_continue_dialog_text(timeout=10000)` - Fetch Review and Continue dialog text
- `otp_verification(outlook_page=None)` - Complete OTP verification workflow
- `complete_docusign_signing_with_otp(d_number, parent_page, outlook_page)` - Full signing workflow with OTP

#### OTP/Verification Workflow Methods:
- `_click_send_now_button()` - Trigger OTP email send
- `_init_locators()` - Initialize all button locators
- `_init_locators(page)` - Reinitialize locators for context switching

#### Dialog and Verification Methods:
- `verify_docusign_page_loaded()` - Verify page fully loaded with URL checks
- `click_review_document_link()` (in Outlook integration)
- `complete_ersd_and_finish()` - Complete ERSD consent and finish
- `complete_ersd_and_continue()` - Complete ERSD consent and continue

---

### 1.2 Outlook Page Object (Signature Integration)
**File:** [pages/outlook_page.py](pages/outlook_page.py)  
**Purpose:** Integrates signature workflows with email verification

#### Signature-Related Methods:
- `search_authorized_signer_email(outlook_email_page, search_text)` - Search for authorized signer email using D-number
  - Filters by subject: "Electronic Signature"
  - Filters by body: "ready for you to sign"
  - Used to find active (non-voided) signing requests

- `fetch_authorized_signer_email_subject_and_body(outlook_email_page, d_number)` - Fetch email subject and body for verification

- `click_review_document_link(outlook_email_page)` - Click "REVIEW DOCUMENT" link in authorized signer email
  - Opens DocuSign in new tab/popup
  - Returns Page object for new DocuSign tab

- `login_and_complete_the_signing(search_text)` - Complete full authorized signer signing workflow
  - Logs into Outlook
  - Searches for authorized signer email
  - Clicks Review Document link
  - Performs OTP verification
  - Completes DocuSign signing

- `login_and_complete_the_signing_without_otp(search_text)` - Complete signing without OTP (ERSD only)

- `login_and_complete_the_authorized_signer_ersd_and_finish(search_text)` - Complete ERSD and finish

#### Supporting Methods:
- `_handle_sign_in_if_needed(page)` - Handle Outlook sign-in if required
- `login_outlook(context_message)` - Login to Outlook email
- `get_otp_with_retry()` - Retrieve OTP from Outlook with retry logic
- `get_otp()` - Get OTP from email content
- `_read_latest_mail_time()` - Parse email timestamp for OTP validation

---

### 1.3 Client Accounts Page Object (Signer Management)
**File:** [pages/client_accounts_page.py](pages/client_accounts_page.py)  
**Purpose:** Manages authorized signer approval options and eSignature methods

#### Signer Approval Methods:
- `select_authorized_signer_approval_option(option)` - Select "Yes" or "No" for authorized signer approval
  - Radio button selection in Signer Information dialog
  - Validates against valid options ["Yes", "No"]

- `select_authorized_signer_esign_method(method)` - Select eSign method
  - Methods: "SMS", "Tracking Center"
  - Selects corresponding radio button

- `verify_fields_for_esign_method(method)` - Verify fields displayed for selected eSign method
  - For SMS: Authorized Signers dropdown, Email, Phone
  - For Tracking Center: Similar fields

- `provide_authorized_signers_information(authorized_signer, email_address, phone)` - Fill signer info
  - Authorized Signer (dropdown or text)
  - Email Address
  - Phone

- `click_continue_on_signer_dialog()` - Click Continue on Signer Information dialog

#### Dialog Management:
- `get_signer_information_dialog_text()` - Get text from Signer Information dialog
- `handle_signature_dialog(signature_option, button_text)` - Handle signature dialog interactions
- `get_signature_dialog_title()` - Get signature dialog title

#### Client Signature Methods:
- `select_client_signature_method()` - Select client signature method
- `verify_client_signature_not_required()` - Verify "Client Signature Not Required" dialog

---

## 2. BDD STEP DEFINITIONS FOR SIGNATURES

### 2.1 DocuSign Steps
**File:** [tests/bdd/steps/docusign_steps.py](tests/bdd/steps/docusign_steps.py)

#### Workflow Steps:
- `user_confirm_and_continue()` - Check ERSD consent and click Continue
  - BDD Step: "When User confirm and Continue the docusign Review and continue dialog"

- `user_finish_the_docusign_process()` - Click Finish to complete signing
  - BDD Step: "When User Finish the DocuSign process"

- `user_should_be_redirected_to_docusign_page()` - Verify DocuSign page redirect
  - BDD Step: "Then User should be redirected to the DocuSign page"

- `verify_as_authorized_by_stamp_presence()` - Verify stamping presence
  - BDD Step: "Then Verify As_authorized_by stamp presence"
  - Checks if "As authorized by" text exists based on test data

- `verify_docusign_review_and_continue_dialog_text(expected_text)` - Verify dialog text
  - BDD Step: 'Then Verify docusign Review and continue dialog text "{expected_text}"'
  - Uses SoftAssertions for non-blocking validation

- `user_add_signature()` - Complete signature addition workflow
  - BDD Step: "When User add Signature"
  - Clicks Finish → Sign → Finish sequence

- `user_click_review_document_and_submit_opt()` - Click Review Document and perform OTP
  - BDD Step: "When User click Review Document link in authorized signer email"
  - Opens DocuSign from email link
  - Performs OTP verification workflow

---

### 2.2 Outlook Steps
**File:** [tests/bdd/steps/outlook_steps.py](tests/bdd/steps/outlook_steps.py)

#### Email and Signing Steps:
- `user_login_to_the_email_and_search_the_authorized_signer_email()` - Search for authorized signer email
  - BDD Step: "When User login to the email and search the authorized signer email"
  - Filters by D-number, subject, and body

- `fetch_authorized_signer_email_subject_and_body_step()` - Fetch email content
  - BDD Step: "Then Verify authorized signer email content"
  - Fetches and stores subject and body

- `user_login_to_the_email_and_complete_the_workflow_approver_signature()` - Complete full signing workflow
  - BDD Step: "When User login to the email and complete the workflow approver signature"
  - Full end-to-end authorized signer signing

- `user_click_on_review_document_link_in_authorized_signer_email()` - Click Review Document link
  - BDD Step: "When User click on Review Document link in authorized signer email"
  - Handles new tab/popup for DocuSign

---

### 2.3 Client Accounts Steps
**File:** [tests/bdd/steps/client_accounts_steps.py](tests/bdd/steps/client_accounts_steps.py)

#### Signer Setup Steps:
- `select_authorized_signer_approval_option()` - Select signer approval
  - BDD Step: "When User select Authorized Signer Approval option"

- `verify_signer_information_dialog_exists_with_correct_information()` - Verify signer dialog
  - BDD Step: "Then Signer(s) Information dialog should be displayed"

- `verify_authorized_signer_approval_section()` - Verify approval section
  - BDD Step: "And Verify Authorized Signer Approval section should be displayed"

- `verify_authorized_signer_esign_method_section()` - Verify eSign method section
  - BDD Step: "Then Authorized Signer eSign Method section should be displayed"

- `user_select_authorized_signer_esign_method()` - Select eSign method
  - BDD Step: "When User select Authorized Signer eSign Method"

- `verify_fields_for_esign_method()` - Verify method-specific fields
  - BDD Step: "Then Verify appropriate fields are displayed based on eSign Method selected"

- `verify_authorized_signer_dropdown()` - Verify signer dropdown
  - BDD Step: "Then Verify Authorized Signer dropdown"

- `provide_authorized_signers_information()` - Fill signer information
  - BDD Step: "When User provide Authorized Signers information"

- `user_select_client_signature_method()` - Select client signature method
  - BDD Step: "When User select Client Signature Method"

- `verify_client_signature_not_required_dialog()` - Verify signature not required dialog
  - BDD Step: "Then Client Signature Not Required dialog should be displayed"

---

## 3. LOCATORS FOR SIGNATURE COMPONENTS

**File:** [locators/docusign_locators.py](locators/docusign_locators.py)

### DocuSign URL and Patterns:
```python
DOCUSIGN_URL_PATTERN = "https://apps-d.docusign.com/"
```

### ERSD (Electronic Record and Signature Disclosure):
```python
ERSD_CONSENT_TEXT = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."
```

### Button Locators:
```python
FINISH_BUTTON = '#action-bar-btn-finish'
SEND_NOW_BUTTON_PATTERN = "Send Now"
CONFIRM_CODE_BUTTON_PATTERN = "Confirm Code"
RESEND_CODE_BUTTON_PATTERN = "Resend Code"
SIGN_HERE_BUTTON_PATTERN = r"Required\s*-\s*Sign Here"
SIGNATURE_APPLIED_BUTTON_PATTERN = r"Required\s*-\s*Signature Applied"
```

### Dialog Locators:
```python
REVIEW_CONTINUE_DIALOG = '[aria-label="Review and continue"]'
DIALOG_CONTENT_P_TAG = 'p[data-qa="email-message-content"]'
```

### Signature Elements:
```python
SIGN_BUTTON = '//div[@data-type="SignHere"]/button'
SIGNATURE_TAB_BUTTON = "//button[contains(@data-qa,'signature-tab-required')]"
DATE_SIGNED_INPUT = "//div[@data-type='DateSigned']/descendant::input"
```

### Session and Stamping:
```python
SESSION_TIMEOUT_BANNER = "#ds_hldrBdy_lblHeaderText"
STAMPING_ELEMENT_TEXT_KEY = "As authorized by"
OTP_FIELD_NAME_PATTERN = "verification code"
```

---

## 4. TEST FEATURE FILES

**File:** [tests/bdd/features/OAM.feature](tests/bdd/features/OAM.feature)

### Signature Workflow Scenarios:
1. **OAM_Initiated by SAU_Online Submit_Authorized Signer_Not_Required**
   - Client signs without authorized signer
   - Workflow: Navigate → Client Signature → DocuSign → ERSD → Finish

2. **OAM_Initiated by SAU_Online Submit_Authorized Signer_Not_Required** (with authorized signer)
   - Authorized signer approves and signs
   - Workflow: Signer setup → SMS/TC Method → Email notification → Review Document → OTP → Sign → Finish

3. **OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_FA**
   - Financial Advisor authorized signer signing
   - Full workflow with eSign method selection

4. **OAM_Initiated by SAU_Online Submit_Authorized Signer_Required_SAU**
   - Shared Access User authorized signer signing
   - Similar to FA workflow with SAU role

### Key Test Steps:
```gherkin
Then Client Signature Not Required dialog should be displayed
When User select Client Signature Method
Then User should be redirected to the DocuSign page
And Verify docusign Review and continue dialog text "..."
When User confirm and Continue the docusign Review and continue dialog
And User Finish the DocuSign process
When User add Signature
Then Signature and today's date should be added on the document
```

---

## 5. DATABASE QUERIES FOR SIGNATURE/SIGNER DATA

**File:** [queries/sql_queries.yaml](queries/sql_queries.yaml)

### E-Signature Related Queries:
```yaml
# DocuSign ID lookup
docusign_id_by_item_id: "SELECT DocuSignID FROM trackingcenter..envelope WHERE itemid = ?"

# E-Signature data database
esignature_data:
  database: "esignaturedata"
  queries:
    recipient_by_envelope_provider_id: "SELECT Role, RoutingOrder FROM esignaturedata.dbo.recipient WHERE envelopeproviderid = CAST(? AS UNIQUEIDENTIFIER)"

# Authorized Signer queries
authorized_signer_SAU_name_ManageLogin_by_UserID: "..."
```

---

## 6. SIGNATURE WORKFLOW PATTERNS

### Complete Signature Workflow (Client Direct):
1. User navigates to initiate request
2. Client Signature Not Required dialog appears
3. User clicks "Continue" or "Sign"
4. User redirected to DocuSign
5. Review and Continue dialog shown with message
6. User checks ERSD consent checkbox
7. User clicks Continue button
8. Document shown with signature fields
9. User clicks Sign button to add signature
10. "As authorized by" stamping appears with date
11. User clicks Finish button to complete

### Authorized Signer Workflow (With OTP):
1. Initial request submitted with authorized signer info
2. Email sent to authorized signer with D-number
3. Authorized signer receives "Electronic Signature" email
4. Email contains "REVIEW DOCUMENT" link
5. Authorized signer clicks link → Opens DocuSign in new tab
6. "Send Now" button clicked to trigger OTP
7. OTP email sent and retrieved from Outlook
8. OTP code submitted to DocuSign
9. ERSD consent checked
10. Continue → Signature fields shown
11. Signature added
12. Finish to complete

### eSign Method Selection:
- **SMS**: Phone number required, signer info fields
- **Tracking Center**: Signer info fields displayed
- **Mail**: Traditional physical mail method

---

## 7. SIGNATURE DIALOG TYPES

1. **Client Signature Not Required Dialog**
   - Options: "Proceed without signature" or "Continue with signature"
   - Appears at workflow start

2. **Signer Information Dialog**
   - Authorized Signer Approval section (Yes/No)
   - eSign Method section (SMS/TC/Mail)
   - Authorized Signers dropdown
   - Email and Phone fields

3. **Review and Continue Dialog (DocuSign)**
   - Message: "Please review and sign the document electronically."
   - ERSD consent checkbox
   - Continue button

4. **Signature Fields (DocuSign)**
   - Sign Here button/div
   - Date Signed input
   - Stamping area

---

## 8. OTP AND VERIFICATION MECHANISMS

### OTP Retrieval Process:
1. "Send Now" button clicked → Triggers OTP email
2. OTP email arrives in Outlook
3. `get_otp_with_retry()` navigates to OTP folder
4. Reads email timestamp
5. Validates timestamp is within acceptable window (≥ Send Now time - 2 min)
6. Extracts 6-digit OTP code from email
7. Returns OTP to caller

### OTP Submission:
1. Locate OTP input field by role (textbox) and name pattern
2. Fill field with OTP code
3. Locate and click "Confirm Code" button
4. Wait for confirmation

### Email Filters for Authorized Signer Email:
- **Subject Filter**: "Electronic Signature" (identifies DocuSign emails)
- **Body Filter**: "ready for you to sign" (identifies active, non-voided requests)
- Both filters ensure we get the correct active signing request

---

## 9. CONFIGURATION AND SETTINGS

### DocuSign Configuration:
- **Base URL**: https://apps-d.docusign.com/
- **Environment**: Demo/Test environment (site=demo.docusign.net)
- **Timeout**: 60 seconds for page load, 10 seconds for elements

### Outlook Integration:
- Email credentials stored in settings
- Encryption for credentials
- OTP folder navigation
- Email timestamp parsing (format: %I:%M %p)

---

## 10. ERROR HANDLING AND ASSERTIONS

### Common Assertions:
- Dialog presence (aria-label="Review and continue")
- Element visibility and state
- Text content matching
- Stamping presence/absence
- Button state (visible, enabled, clickable)

### Soft Assertions Used:
- Non-blocking assertions via SoftAssertions utility
- Allows collecting multiple failures before throwing
- Better for test diagnostics

---

## 11. KEY UTILITIES AND HELPERS

### Allure Logging:
- Screenshot capture for evidence
- Named attachments for reporting
- Step-level annotations

### Wait Utilities:
- Element visibility waits
- Page load waits
- Timeout configurations

### Dialog Utilities:
- Dialog detection
- Dialog content extraction
- Dialog dismissal

---

## 12. SUMMARY BY OPERATION TYPE

| Operation | Page Object | Method | Step Definition |
|-----------|-------------|--------|-----------------|
| Add Signature | DocuSignPage | click_sign_button() + click_finish_button() | user_add_signature() |
| Complete Signing | DocuSignPage | complete_docusign_signing_with_otp() | user_click_review_document_and_submit_opt() |
| Select Signer | ClientAccountsPage | select_authorized_signer_approval_option() | select_authorized_signer_approval_option() |
| Select eSign Method | ClientAccountsPage | select_authorized_signer_esign_method() | user_select_authorized_signer_esign_method() |
| Provide Signer Info | ClientAccountsPage | provide_authorized_signers_information() | provide_authorized_signers_information() |
| Search Email | OutlookPage | search_authorized_signer_email() | user_login_to_the_email_and_search_the_authorized_signer_email() |
| Fetch Email | OutlookPage | fetch_authorized_signer_email_subject_and_body() | verify_authorized_signer_email_content() |
| Verify Dialog Text | DocuSignPage | fetch_docusign_review_and_continue_dialog_text() | verify_docusign_review_and_continue_dialog_text() |
| Verify Stamping | DocuSignPage | get_stamping_element() | verify_as_authorized_by_stamp_presence() |
| Submit OTP | DocuSignPage | submit_otp() | Used in otp_verification() |
| Check ERSD | DocuSignPage | check_ersd_consent_checkbox() | user_confirm_and_continue() |
| Finish Process | DocuSignPage | click_finish_button() | user_finish_the_docusign_process() |

---

## 13. FILES CONTAINING SIGNATURE CODE

### Python Pages:
- [pages/docusign_page.py](pages/docusign_page.py) - Main DocuSign interactions
- [pages/outlook_page.py](pages/outlook_page.py) - Email/signer integration
- [pages/client_accounts_page.py](pages/client_accounts_page.py) - Signer setup

### BDD Steps:
- [tests/bdd/steps/docusign_steps.py](tests/bdd/steps/docusign_steps.py) - DocuSign workflows
- [tests/bdd/steps/outlook_steps.py](tests/bdd/steps/outlook_steps.py) - Email workflows
- [tests/bdd/steps/client_accounts_steps.py](tests/bdd/steps/client_accounts_steps.py) - Signer management

### Locators:
- [locators/docusign_locators.py](locators/docusign_locators.py) - All signature-related locators

### Features:
- [tests/bdd/features/OAM.feature](tests/bdd/features/OAM.feature) - Signature test scenarios

### Utilities:
- [utils/database.py](utils/database.py) - Database queries for signer data
- [queries/sql_queries.yaml](queries/sql_queries.yaml) - SQL queries for DocuSign/signer data

---

## 14. ADDITIONAL DOCUMENTATION

- [ANALYSIS_MULTIPLE_DOCUSIGN_PAGES.md](ANALYSIS_MULTIPLE_DOCUSIGN_PAGES.md) - Analysis of multiple DocuSign page object handling
- [EMAIL_BODY_FETCHING_ANALYSIS.md](EMAIL_BODY_FETCHING_ANALYSIS.md) - Email content extraction logic
- [docs/DOCUSIGN_OTP_FIX_SUMMARY.md](docs/DOCUSIGN_OTP_FIX_SUMMARY.md) - OTP verification improvements

---

## 15. EXECUTION CONTEXT AND TEST CONTEXT

### Test Context Variables (test_context):
- `test_data` - CSV row data for current test
- `new_docusign_page` - New DocuSign page opened from email link
- `outlook_email_page` - Outlook email page instance
- `multiple_signers` - Authorized signers from database
- `d_number` - Document number from request

### Fixture Dependencies:
- `authenticated_page` - Main application page (Playwright Page)
- `docusign_page` - DocuSignPage fixture wrapping authenticated_page
- `client_accounts_page` - ClientAccountsPage fixture
- `outlook_page` - OutlookPage fixture
- `test_context` - Context dictionary for test data sharing

---

**Last Updated:** 2026-04-07  
**Project:** QE Automation Framework  
**Scope:** Comprehensive signature-related functionality inventory
