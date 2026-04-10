# Email Body Fetching Analysis - Outlook Steps

## Error Summary
```
AssertionError: Email body mismatch.
Expected (substring): Juan SamZa,

Your Shared Access User has prepared one or more documents...
Actual: ⚠️ Caution: This message is from an external party...
         [entire email body including headers, warnings, footers]
```

---

## 1. WHERE EMAIL BODY IS FETCHED

**File:** [pages/outlook_page.py](pages/outlook_page.py#L1040-L1090)

**Method:** `fetch_authorized_signer_email_subject_and_body()` (Lines 1040-1090)

**Current Locator:**
```xpath
//div[@data-test-id="mailMessageBodyContainer"]
```

**Extraction Method:**
```python
# Line 1064-1070 in outlook_page.py
body_container = outlook_email_page.locator('//div[@data-test-id="mailMessageBodyContainer"]')
body_container.wait_for(state="visible", timeout=10_000)
body_text = body_container.inner_text()  # Gets ALL text content
```

---

## 2. HOW EMAIL BODY IS USED IN TESTS

**File:** [tests/bdd/steps/outlook_steps.py](tests/bdd/steps/outlook_steps.py#L58-L194)

**Step Function:** `fetch_authorized_signer_email_subject_and_body_step()` (Lines 58-194)

### Data Flow:
1. **Line 73:** Fetch actual email from Outlook:
   ```python
   actual_subject, actual_body = outlook_page.fetch_authorized_signer_email_subject_and_body(outlook_email_page, d_number)
   ```

2. **Line 76-77:** Get expected values from CSV:
   ```python
   expected_subject = test_data.get("Expected_AuthorizedSigner_Email_Subject", "")
   expected_body = test_data.get("Expected_AuthorizedSigner_Email_Body", "")
   ```

3. **Lines 105-111:** Substitute placeholders in expected values:
   ```python
   expected_body_resolved = expected_body.replace("<Document_Creator_Role_Name>", document_creator_role_name or "")
   expected_body_resolved = expected_body_resolved.replace("<Authorized_Signer_Role_Name>", authorized_signer_role_name or "")
   expected_body = expected_body_resolved
   ```

4. **Line 194:** Compare using substring match:
   ```python
   if expected_body_stripped not in actual_body_stripped:
       error_msg = f"Email body mismatch.\nExpected (substring): {expected_body_stripped}\nActual: {actual_body_stripped}"
       raise AssertionError(error_msg)
   ```

---

## 3. WHAT'S INCLUDED IN ACTUAL_BODY

The **entire** text content from `mailMessageBodyContainer`:

✗ **Included (should NOT be there):**
- ⚠️ Caution warning: "This message is from an external party..."
- Unicode special characters: `\xa0`, `\ue113`
- Non-breaking spaces and formatting
- Email footers: "Do Not Share This Email", "Alternate Signing Method", etc.
- Security codes and contact information
- Multiple newlines and whitespace

✓ **Included (should be there):**
- Signer name (e.g., "Juan SamZa," or "Howard Ginsberg CPA,")
- Message content: "Your Shared Access User has prepared..."
- "REVIEW DOCUMENT" button/link text
- Other DocuSign email content

---

## 4. HTML STRUCTURE IN OUTLOOK

```html
<div data-test-id="mailMessageBodyContainer">
  <!-- Full email rendering including -->
  <div>
    ⚠️ Caution: This message is from an external party...
    [warning box]
  </div>
  
  <div>
    [main email content]
    Juan SamZa,
    
    Your Shared Access User has prepared...
  </div>
  
  <div>
    [email footer with security warnings]
    Do Not Share This Email
    Alternate Signing Method
    ...
  </div>
</div>
```

---

## 5. THE PROBLEM

### Root Cause:
The locator `//div[@data-test-id="mailMessageBodyContainer"]` captures the **entire** email container, which includes:
- Outlook's computed warnings and banners for external emails
- DocuSign's complete email template with all sections
- All footers and additional content

### Why Substring Match Fails:
The expected text is relatively clean:
```
Juan SamZa,

Your Shared Access User has prepared one or more documents that are ready for you to sign electronically.
```

The actual text is buried in:
```
⚠️ Caution: This message is from an external party. Report suspicious messages with the report phish button in your Outlook ribbon bar
 [special Unicode chars]
[formatting]

Please review and sign your document.
REVIEW DOCUMENT

Juan SamZa,

Your Shared Access User has prepared one or more documents that are ready for you to sign electronically.
[more content and footers...]
```

Even though "Juan SamZa," IS in the actual body, the comparison might fail due to:
1. **Whitespace issues** - Unicode characters like `\xa0` (non-breaking space) vs regular spaces
2. **Character encoding** - Smart quotes or other special characters in actual vs expected
3. **Line break differences** - Actual has different newlines/formatting

---

## 6. RECOMMENDED SOLUTIONS

### Option A: Extract Only Main Email Content
Modify locator to target only the email message body (skip warnings and footers):

```python
# In pages/outlook_page.py, line 1064
# Instead of:
body_container = outlook_email_page.locator('//div[@data-test-id="mailMessageBodyContainer"]')

# Use more specific selector that excludes warnings:
# Look for the main message container, not the entire wrapper
body_text = outlook_email_page.locator('//div[@aria-label="Message content"]').first.inner_text()
# OR
body_text = outlook_email_page.locator('//div[contains(@class, "message-body")]').first.inner_text()
```

### Option B: Clean Up Extracted Text
After extracting, remove known warnings and footers:

```python
# In pages/outlook_page.py, after line 1068
body_text = body_container.inner_text()

# Remove Outlook's external warning banner
body_text = body_text.replace("⚠️ Caution: This message is from an external party...", "")
body_text = body_text.replace("Report suspicious messages with the report phish button...", "")

# Remove footer sections
body_text = body_text.split("Do Not Share This Email")[0]  # Keep only content before footer

# Clean up special Unicode and extra whitespace
body_text = body_text.replace('\u00A0', ' ')  # Replace non-breaking spaces
body_text = body_text.replace('\ue113', '')   # Remove special Unicode
body_text = ' '.join(body_text.split())  # Normalize whitespace
```

### Option C: Use Normalized String Comparison
Make comparison more robust:

```python
# In tests/bdd/steps/outlook_steps.py, around line 186
import unicodedata
import re

def normalize_for_comparison(text):
    """Normalize text for robust email body comparison"""
    # Unicode normalization
    text = unicodedata.normalize('NFC', text)
    
    # Replace special characters
    text = text.replace('\u00A0', ' ')  # Non-breaking space
    text = text.replace('\u2009', ' ')  # Thin space
    text = text.replace('\ue113', '')   # Special Unicode
    
    # Remove email warnings and footers
    text = text.replace("⚠️ Caution: This message is from an external party. Report suspicious messages...", "")
    text = text.split("Do Not Share This Email")[0]
    
    # Normalize multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Then use:
actual_body_normalized = normalize_for_comparison(actual_body)
expected_body_normalized = normalize_for_comparison(expected_body)

if expected_body_normalized not in actual_body_normalized:
    error_msg = f"Email body mismatch..."
```

---

## 7. RECOMMENDATION PRIORITY

**Priority 1 (Best):** Option A - Use more specific locator  
- Directly targets only the message content  
- No post-processing needed  
- Most maintainable long-term  

**Priority 2 (Better):** Option C - Normalize text for comparison  
- Handles current HTML structure  
- Makes comparison more robust  
- Easier to implement immediately  

**Priority 3 (Quick Fix):** Option B - Clean up extracted text  
- Works with current locators  
- Clears out known junk content  

---

## 8. CURRENT LOCATORS SUMMARY

| Component | Locator | Location | Issue |
|-----------|---------|----------|-------|
| **Subject** | `//div[contains(@id,"SUBJECT")]/descendant::span[1]` | outlook_page.py:1050 | ✓ Works fine |
| **Body** | `//div[@data-test-id="mailMessageBodyContainer"]` | outlook_page.py:1064 | ✗ Gets entire container including warnings |

