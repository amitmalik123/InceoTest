# DocuSign OTP Functions - Missing Components Fix Summary

## Overview
Fixed all missing dependencies in [pages/docusign_page.py](../pages/docusign_page.py) OTP-related functions to align with existing project components.

---

## 📋 Issues Fixed

### 1. **Missing Imports** ✅
**Files Modified**: [pages/docusign_page.py](../pages/docusign_page.py#L1-L20)

**Before:**
```python
import re
from datetime import datetime
from typing import Callable, Optional
```

**After:**
```python
import os                          # ✅ ADDED - Used for file operations in click_send_now()
import re
import time                        # ✅ ADDED - Used for epoch time tracking
from datetime import datetime
from typing import Callable, Optional

from config.settings import get_settings          # ✅ ADDED - For credential retrieval
from pages.outlook_page import OutlookPage        # ✅ ADDED - Correct class import
```

**Impact**: Enables all time/OS operations and settings access used throughout OTP functions

---

### 2. **Fixed Wrong Class Reference** ✅
**Issue**: Code referenced `OutlookOTPPage` which doesn't exist

**Locations Fixed**:
- Line 406: `OutlookOTPPage.get_email()` → Now using static method `DocuSignPage.get_email()`
- Line 407: `OutlookOTPPage.get_password()` → Now using static method `DocuSignPage.get_password()`
- Line 413: `OutlookOTPPage(outlook_page)` → Now `OutlookPage.from_config(outlook_page)`
- Line 441: Type hint `outlook_otp: OutlookOTPPage` → Now `outlook_otp: OutlookPage`

**Solution**: 
- Import correct `OutlookPage` class from [pages/outlook_page.py](../pages/outlook_page.py)
- Use `OutlookPage.from_config()` factory method to instantiate with encrypted credentials
- Implement static methods in `DocuSignPage` to retrieve credentials from settings

---

### 3. **Added Locator Property Initialization** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L32-L42)

**New Method**: `_initialize_locators()`
```python
def _initialize_locators(self) -> None:
    """Initialize all locator properties for Send Now and Resend Code buttons."""
    # Send Now button with multiple locator strategies
    self.send_now_button = self.page.locator('button[data-qa*="send-now"]')
    self.send_now_button_by_role = self.page.get_by_role("button", name=SEND_NOW_BUTTON_PATTERN)
    self.send_now_button_text = self.page.get_by_text(SEND_NOW_BUTTON_PATTERN)
    
    # Resend Code button with multiple locator strategies
    self.resend_code_button = self.page.locator('button[data-qa*="resend-code"]')
    self.resend_code_primary_button = self.page.get_by_role("button", name=RESEND_CODE_BUTTON_PATTERN)
    
    # Fallback locator for Send Now button variants
    self.send_now_fallback_buttons = self.page.get_by_role("button").filter(has_text=re.compile(...))
```

**Called From**:
- `__init__()` - Initializes all locators on page creation
- `_init_locators(page)` - Reinitializes when switching pages

**Properties Initialized**:
- ✅ `self.send_now_button` (data-qa locator)
- ✅ `self.send_now_button_by_role` (role-based locator)
- ✅ `self.send_now_button_text` (text-based locator)
- ✅ `self.resend_code_button` (data-qa locator)
- ✅ `self.resend_code_primary_button` (role-based locator)
- ✅ `self.send_now_fallback_buttons` (fallback matching)

---

### 4. **Added Instance Variable Initialization** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L27-L29)

**In `__init__()` method:**
```python
def __init__(self, page: Page, base_url: str = ""):
    super().__init__(page, base_url=base_url)
    self._initialize_locators()
    self._last_send_now_epoch = None  # ✅ ADDED - Initialized to None
```

**Impact**: `_last_send_now_epoch` is now properly initialized and can be set in:
- Line 518: `_click_resend_code_button()` 
- Line 536: `click_send_now()`

---

### 5. **Added Static Credential Methods** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L44-L63)

**New Static Methods**:
```python
@staticmethod
def get_email() -> str:
    """Get Outlook email from settings configuration."""
    settings = get_settings()
    return settings.outlook_email or ""

@staticmethod
def get_password() -> str:
    """Get Outlook password from settings configuration."""
    settings = get_settings()
    return settings.outlook_password or ""
```

**Usage**:
- Replaces `OutlookOTPPage.get_email()` calls
- Replaces `OutlookOTPPage.get_password()` calls
- Retrieves encrypted credentials from [config/settings.py](../config/settings.py)
- Returns encrypted values (will be decrypted by OutlookPage.from_config())

---

### 6. **Added `_init_locators()` Method** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L65-L71)

**Purpose**: Reinitialize locators when switching to a new page context
```python
def _init_locators(self, page: Page) -> None:
    """Reinitialize locators for a new page (for context switching)."""
    self.page = page
    self._initialize_locators()
```

**Called By**: Line 481 in `fetch_and_submit_otp()` when switching back to DocuSign page from OTP submission

---

### 7. **Added `submit_otp()` Method** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L73-111)

**Implementation**:
```python
def submit_otp(self, otp_code: str, timeout: int = 10000) -> None:
    """Submit OTP code to the verification code field in DocuSign."""
    logger.info(f"Submitting OTP code to DocuSign")
    
    try:
        # Locate the OTP input field by role and name pattern
        otp_field = self.page.get_by_role("textbox", name=re.compile(
            docusign_locators.OTP_FIELD_NAME_PATTERN, re.IGNORECASE))
        
        # Wait for field to be visible
        otp_field.wait_for(state="visible", timeout=timeout)
        logger.debug("OTP field is visible")
        
        # Fill the OTP code
        otp_field.fill(otp_code)
        logger.info(f"OTP code entered")
        
        # Wait a moment for the field to process
        self.page.wait_for_timeout(1000)
        
        # Click the Confirm Code button to submit
        confirm_button = self.page.get_by_role("button", 
            name=docusign_locators.CONFIRM_CODE_BUTTON_PATTERN)
        confirm_button.wait_for(state="visible", timeout=timeout)
        logger.debug("Confirm Code button is visible")
        
        confirm_button.click()
        logger.info("Confirm Code button clicked")
        
        # Wait for submission to complete
        self.page.wait_for_timeout(2000)
        
    except Exception as e:
        logger.error(f"Failed to submit OTP: {str(e).splitlines()[0]}")
        raise RuntimeError(f"Code is incorrect or submission failed: {e}")
```

**Uses Existing Components**:
- `docusign_locators.OTP_FIELD_NAME_PATTERN` = "verification code"
- `docusign_locators.CONFIRM_CODE_BUTTON_PATTERN` = "Confirm Code"
- Playwright role-based locators
- Existing error handling patterns

**Called By**: Line 482 in `fetch_and_submit_otp()` after OTP code is fetched

---

### 8. **Fixed `otp_verification()` Method** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L455-481)

**Before (BROKEN)**:
```python
def otp_verification(self) -> None:
    self.click_send_now()
    
    otp_submitted = self.fetch_and_submit_otp(
        outlook_otp,              # ❌ Undefined variable
        email=outlook_email,      # ❌ Undefined variable
        password=outlook_password,# ❌ Undefined variable
```

**After (FIXED)**:
```python
def otp_verification(self) -> None:
    """Run common Outlook pre-login + Send Now + OTP submission flow."""
    logger.info("[common_otp] Start")
    outlook_page = None
    try:
        # Click Send Now to trigger OTP email
        self.click_send_now()
        logger.info("Send Now clicked to trigger OTP email")
        
        # Get Outlook credentials from settings
        outlook_email = self.get_email()
        outlook_password = self.get_password()
        logger.info("Retrieved Outlook credentials from settings")
        
        # Create new page for Outlook in same context
        outlook_page = self.page.context.new_page()
        logger.info("Created new Outlook page")
        
        # Initialize Outlook page object
        outlook_otp = OutlookPage.from_config(outlook_page)
        logger.info("Initialized OutlookPage object")
        
        # Fetch and submit OTP
        otp_submitted = self.fetch_and_submit_otp(
            outlook_otp,
            email=outlook_email,
            password=outlook_password,
            timeout=180.0,
            refresh_interval=5.0,
            preferred_sender=getattr(self, "_preferred_otp_sender", None),
            max_attempts=2,
        )

        if not otp_submitted:
            raise RuntimeError("OTP retrieval failed during e-signature flow")

        logger.info("[common_otp] Completed")
    finally:
        if outlook_page:
            logger.info("[common_otp] Closing Outlook OTP tab")
            try:
                outlook_page.close()
            except Exception as e:
                logger.warning(f"Error closing Outlook page: {e}")
        # Bring DocuSign page back to front
        try:
            self.page.bring_to_front()
        except Exception as e:
            logger.warning(f"Error bringing DocuSign page to front: {e}")
```

**Changes**:
- ✅ All undefined variables now defined
- ✅ Added proper initialization of `outlook_otp` with `OutlookPage.from_config()`
- ✅ Credentials retrieved from `self.get_email()` and `self.get_password()`
- ✅ Enhanced error handling and cleanup
- ✅ Brings DocuSign page back to front after Outlook tab closes

---

### 9. **Fixed `_fetch_and_submit_otp_from_outlook()` Method** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L483-520)

**Before (BROKEN)**:
```python
outlook_email = OutlookOTPPage.get_email()       # ❌ Wrong class
outlook_password = OutlookOTPPage.get_password() # ❌ Wrong class
outlook_otp = OutlookOTPPage(outlook_page)       # ❌ Wrong class
```

**After (FIXED)**:
```python
outlook_email = self.get_email()
outlook_password = self.get_password()
outlook_otp = OutlookPage.from_config(outlook_page)
```

**All Changes**:
- ✅ Use correct `OutlookPage` class
- ✅ Retrieve credentials via `self.get_email()` and `self.get_password()`
- ✅ Proper error handling with exception cleanup
- ✅ Log all major steps

---

### 10. **Fixed `fetch_and_submit_otp()` Type Hint** ✅
**File**: [pages/docusign_page.py](../pages/docusign_page.py#L521-530)

**Before**:
```python
def fetch_and_submit_otp(
    self,
    outlook_otp: OutlookOTPPage,  # ❌ Non-existent class
```

**After**:
```python
def fetch_and_submit_otp(
    self,
    outlook_otp: OutlookPage,     # ✅ Correct class
```

---

## 📊 Summary of Changes

| Component | Issue | Fix | Link |
|-----------|-------|-----|------|
| **Imports** | Missing `os`, `time`, `OutlookPage` | Added all required imports | [L1-20](../pages/docusign_page.py#L1-L20) |
| **Class Reference** | `OutlookOTPPage` doesn't exist | Use `OutlookPage` + add static methods | [L44-63](../pages/docusign_page.py#L44-L63) |
| **Locators** | Never initialized | Added `_initialize_locators()` in `__init__` | [L32-42](../pages/docusign_page.py#L32-L42) |
| **_last_send_now_epoch** | Uninitialized | Added `self._last_send_now_epoch = None` | [L29](../pages/docusign_page.py#L29) |
| **get_email()** | Missing | Added static method | [L44-51](../pages/docusign_page.py#L44-L51) |
| **get_password()** | Missing | Added static method | [L53-60](../pages/docusign_page.py#L53-L60) |
| **_init_locators(page)** | Missing | Added method | [L65-71](../pages/docusign_page.py#L65-L71) |
| **submit_otp()** | Missing | Added complete implementation | [L73-111](../pages/docusign_page.py#L73-L111) |
| **otp_verification()** | Undefined variables | Fixed with proper definitions | [L455-481](../pages/docusign_page.py#L455-L481) |
| **_fetch_and_submit_otp_from_outlook()** | Wrong class refs | Fixed class references | [L483-520](../pages/docusign_page.py#L483-L520) |
| **fetch_and_submit_otp()** | Wrong type hint | Updated type hint to `OutlookPage` | [L521-530](../pages/docusign_page.py#L521-L530) |

---

## ✅ Validation

### All Missing Components Now Present:
- ✅ `import os` - For file/directory operations
- ✅ `import time` - For epoch time tracking
- ✅ `OutlookPage` class - Correct import
- ✅ `DocuSignPage.get_email()` - Static method
- ✅ `DocuSignPage.get_password()` - Static method
- ✅ `self.send_now_button` - Locator property
- ✅ `self.send_now_button_by_role` - Locator property
- ✅ `self.send_now_button_text` - Locator property
- ✅ `self.resend_code_button` - Locator property
- ✅ `self.resend_code_primary_button` - Locator property
- ✅ `self.send_now_fallback_buttons` - Locator property
- ✅ `self._last_send_now_epoch` - Instance variable
- ✅ `_init_locators(page)` - Method
- ✅ `submit_otp(otp_code)` - Method
- ✅ All undefined variables in `otp_verification()` - Defined
- ✅ All undefined variables in `_fetch_and_submit_otp_from_outlook()` - Defined

### Integration:
- ✅ Uses existing `OutlookPage.from_config()` factory method
- ✅ Uses existing `OutlookPage.get_otp_with_retry()` method
- ✅ Uses existing credential system (`get_settings()`)
- ✅ Uses existing locator patterns from `docusign_locators`
- ✅ Uses existing error handling patterns
- ✅ Uses existing logging patterns

---

## Usage Example

```python
from pages.docusign_page import DocuSignPage

# Initialize page
docusign_page = DocuSignPage(page)

# Call OTP verification workflow
docusign_page.otp_verification()
# OR
docusign_page._fetch_and_submit_otp_from_outlook()
```

**Expected Flow**:
1. Click "Send Now" → OTP email triggered
2. Open Outlook in new tab
3. Login to Outlook
4. Fetch latest OTP from email
5. Return to DocuSign
6. Submit OTP code
7. Complete verification

---

## Notes
- All changes use **existing project components** (no external dependencies added)
- **Backward compatible** - existing code patterns preserved
- **Error handling** enhanced throughout
- **Logging** improved for debugging
- **Type hints** corrected and consistent

