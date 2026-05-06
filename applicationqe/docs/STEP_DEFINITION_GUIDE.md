# Step Definition Implementation Guide: In Person Client Signature Details

**Created**: April 20, 2026  
**Using**: Playwright MCP + Utilities Framework  
**Example**: Step definition + Page Object Method

---

## 📋 Overview

This guide documents the implementation of the step definition:
```gherkin
When User provide "in person" client signature details
```

This step demonstrates **best practices** for implementing Playwright-based steps using the qeautomation framework utilities.

---

## 🏗️ Architecture

### Call Flow

```
Feature File (OAM.feature)
    ↓
Step Definition (client_accounts_steps.py)
    ├─ Fetches test data from CSV
    ├─ Validates required fields
    ├─ Calls Page Object method
    └─ Verifies results with Assertions
    
Page Object (client_accounts_page.py)
    ├─ Locates input fields
    ├─ Uses WaitContext for visibility
    ├─ Fills fields with RetryContext
    ├─ Validates entered values
    └─ Returns verification results
```

---

## 📝 Step Definition Implementation

### Location
**File**: `tests/bdd/steps/client_accounts_steps.py`  
**Function**: `user_provide_in_person_client_signature_details()`

### Code Structure

```python
@when('User provide "in person" client signature details')
def user_provide_in_person_client_signature_details(
    authenticated_page: Page, 
    client_accounts_page, 
    test_context
):
    """
    Step definition that:
    1. Extracts test data from CSV
    2. Validates required columns
    3. Calls page object method
    4. Verifies results
    5. Captures screenshots
    """
```

### Key Features

#### 1. **Test Data Extraction**
```python
test_data = test_context.get("test_data", {})
account_owner = test_data.get("Account_Owner") or test_data.get("account_owner")
email_address = test_data.get("Email_Address") or test_data.get("email_address")
phone = test_data.get("Phone") or test_data.get("phone")
```

**Why this pattern?**
- Lowercase fallback handles case-insensitive CSV headers
- Uses `.get()` to prevent KeyError
- Centralized data extraction before validation

#### 2. **Validation**
```python
if not account_owner:
    raise KeyError("[FAIL] Test Data Validation — Expected: Account_Owner column...")
```

**Why validate before calling page object?**
- Fail-fast approach catches CSV issues early
- Better error messages
- Prevents confusing DOM errors

#### 3. **Page Object Call**
```python
result = client_accounts_page.enter_client_signer_details(
    full_name=account_owner,
    email_address=email_address,
    phone=phone,
    signer_index=1
)
```

**Why use page object?**
- Separation of concerns (test logic vs. DOM interaction)
- Reusable across multiple tests
- Easier to maintain when selectors change

#### 4. **Result Verification**
```python
Assertions.assert_true(
    result['fields_filled'],
    f"[FAIL] ClientAccountsPage: Signer Details Entry — ..."
)
```

**Why verify after page object call?**
- Ensures values were actually entered (not just clicked)
- Catches silent failures (e.g., field readonly)
- Provides clear error messages

#### 5. **Reporting**
```python
screenshot = authenticated_page.screenshot()
allure.attach(screenshot, name="In Person Signer Details Entered", 
              attachment_type=allure.attachment_type.PNG)
```

**Why capture screenshots?**
- Visual proof in Allure reports
- Helps debug failures
- Better test documentation

---

## 🔧 Page Object Method Implementation

### Location
**File**: `pages/client_accounts_page.py`  
**Function**: `enter_client_signer_details()`

### Code Structure

```python
def enter_client_signer_details(
    self, 
    full_name: str, 
    email_address: str, 
    phone: str, 
    signer_index: int = 1
) -> dict:
    """
    Fills client signer details in Account Holders table.
    """
```

### Key Features

#### 1. **Dynamic Locators**
```python
name_field = self.page.locator(f'input[name="txtAccountHolderName{signer_index}"]')
email_field = self.page.locator(f'input[name="txtAccountHolderEmail{signer_index}"]')
phone_field = self.page.locator(f'input[name="txtAccountHolderPhone{signer_index}"]')
```

**Why use f-strings for locators?**
- Supports multiple signer rows (index 1, 2, 3...)
- Self-documenting (knows what it's selecting)
- Easy to extend for future rows

#### 2. **WaitContext for Visibility**
```python
with WaitContext(timeout=5.0, poll_interval=0.2) as wait:
    wait.until_visible(name_field, error_message=f"Name field not visible...")
    wait.until_visible(email_field, error_message=f"Email field not visible...")
    wait.until_visible(phone_field, error_message=f"Phone field not visible...")
```

**Why use WaitContext?**
- Replaces brittle `wait_for_selector()`
- Polls intelligently (every 0.2s)
- Better error messages
- Timeout configurable

#### 3. **RetryContext for Reliability**
```python
with RetryContext(max_retries=2, initial_delay=0.2) as retry:
    while retry.should_retry():
        try:
            name_field.clear()
            email_field.clear()
            phone_field.clear()
            retry.success()
        except Exception as e:
            if retry.should_retry():
                retry.failed(e)
            else:
                raise
```

**Why use RetryContext?**
- Field clearing can fail on slow networks
- Automatic exponential backoff (0.2s, 0.4s, etc.)
- No need for manual retry loops
- Clean exception handling

#### 4. **Value Validation**
```python
actual_name = name_field.input_value() or ""
name_match = actual_name == full_name
```

**Why validate entered values?**
- Catches readonly/disabled fields
- Detects silent filling failures
- Browser might modify values (e.g., phone formatting)
- Better than assuming fill() always works

#### 5. **Comprehensive Return Dictionary**
```python
result = {
    'name_field': name_field,
    'email_field': email_field,
    'phone_field': phone_field,
    'values_entered': {
        'full_name': actual_name,
        'email_address': actual_email,
        'phone': actual_phone
    },
    'fields_filled': all_fields_filled
}
```

**Why return a dictionary?**
- Caller can verify specific fields
- Contains actual vs. expected values
- Supports multiple verification strategies
- Future-proof for additional assertions

---

## 📊 HTML Structure Reference

The implementation targets this HTML table:

```html
<table id="tblAccountHolders" width="100%" border="0">
  <tr>
    <td>Account Owner</td>
    <td><input name="txtAccountHolderName1" type="text" id="txtAccountHolderName1"></td>
    <td><input name="txtAccountHolderEmail1" type="text" id="txtAccountHolderEmail1"></td>
    <td><input name="txtAccountHolderPhone1" type="text" maxlength="50" id="txtAccountHolderPhone1"></td>
    <td>
      <input id="radbtnInPerson1" type="radio" name="mygroup1" value="radbtnInPerson1">
    </td>
    <td>
      <input id="radbtnRemote1" type="radio" name="mygroup1" value="radbtnRemote1" checked="checked">
    </td>
  </tr>
</table>
```

**Key observations:**
- Input fields use `name` attributes (not just `id`)
- Multiple signers use index suffix (1, 2, 3...)
- Radio buttons for "In Person" vs "By Email" signing
- Rows pattern repeats for additional signers

---

## 🧪 Usage Examples

### In Feature File

```gherkin
Scenario: OAM with In Person Client Signature
  When User select OAM Request and Type
  When User select Submission Type
  Then Client Signature Not Required dialog should be displayed
  When User select Client Signature Method
  Then Signer(s) Information dialog should be displayed
  When User provide "in person" client signature details
  And Click on Continue
  Then User should be redirected to the DocuSign page
```

### In Test Data (CSV)

```csv
Account_Owner,Email_Address,Phone,OAM_Request,OAM_Type
"John Smith","john@example.com","925-532-9706","Contributions","Copy for Digital Deposit"
```

---

## 🔄 MCP Server Usage in This Implementation

### **Playwright MCP**
```
Used for:
- Best practice locator strategies (by name attribute)
- Input field interaction patterns
- Multi-row table navigation
- Dynamic selector generation
```

### **Filesystem MCP**
```
Used for:
- CSV test data structure design
- Column naming conventions
- Data validation patterns
```

### **Retry/Wait Utilities** (Framework)
```
Used for:
- WaitContext: Replaces wait_for_selector
- RetryContext: Auto-retry with exponential backoff
- Assertions: Hard assertion framework
```

---

## 🚀 Future Extensions

### Add "In Person" Radio Button Selection

```python
def select_signing_method(self, signer_index: int = 1, method: str = "In Person"):
    """Select In Person or By Email signing method"""
    if method == "In Person":
        radio = self.page.locator(f'input#radbtnInPerson{signer_index}')
    else:
        radio = self.page.locator(f'input#radbtnRemote{signer_index}')
    
    radio.check()
    return radio.is_checked()
```

### Add Multiple Signers Support

```gherkin
Scenario: Multiple Account Owners In Person Signing
  When User provide "in person" client signature details for signer 1
  And User provide "in person" client signature details for signer 2
  Then Verify all signers details are entered
```

### Add API Validation

```python
# Using Fetch MCP in step definition
result = requests.post(
    f"{API_URL}/signers/validate",
    json={
        'name': result['values_entered']['full_name'],
        'email': result['values_entered']['email_address'],
        'phone': result['values_entered']['phone']
    }
)
assert result.status_code == 200, "API validation failed"
```

---

## 📚 Framework Utilities Used

| Utility | Purpose | File |
|---------|---------|------|
| `WaitContext` | Smart element waiting | `utils/wait_utils.py` |
| `RetryContext` | Auto-retry with backoff | `utils/retry_utils.py` |
| `Assertions.assert_true` | Hard assertions | `utils/assertions.py` |
| `get_allure_logger` | Structured logging | `utils/allure_logger.py` |
| `allure.step` | Test reporting | `allure` package |

---

## ✅ Checklist for Similar Steps

When implementing new steps, follow this pattern:

- [ ] Create step definition with clear @when/@then decorator
- [ ] Extract test data from CSV with lowercase fallback
- [ ] Validate required fields before calling page object
- [ ] Create page object method with docstring
- [ ] Use WaitContext for element visibility
- [ ] Use RetryContext for unreliable operations
- [ ] Return comprehensive result dictionary
- [ ] Verify results with Assertions
- [ ] Capture screenshots for reporting
- [ ] Add detailed logging at each step
- [ ] Document HTML structure and selectors
- [ ] Include usage examples

---

## 🎓 Learning Outcomes

This implementation demonstrates:

1. **BDD Best Practices**
   - Clear step definitions
   - Separation of concerns (step ≠ page object)
   - Data-driven testing

2. **Playwright Best Practices**
   - Dynamic locators with f-strings
   - Input value validation
   - Proper wait strategies

3. **Framework Utilities**
   - WaitContext for smart waiting
   - RetryContext for reliability
   - Assertions for validation

4. **Test Reporting**
   - Allure step integration
   - Screenshot capture
   - Detailed logging

5. **Maintainability**
   - Self-documenting code
   - Reusable methods
   - Future-proof design

---

## 📞 Questions?

Refer to:
- `docs/ADVANCED_UTILITIES_GUIDE.md` - WaitContext/RetryContext details
- `docs/COMPLETE_EXECUTION_GUIDE.md` - Framework overview
- `.vscode/mcp.json` - Playwright MCP configuration
- `pyproject.toml` - MCP[cli] integration

