# Recording-Based Test Generation Guide

## Overview

This framework now supports **visual, recording-based test generation** that intelligently reuses existing framework components via RAG (Retrieval-Augmented Generation).

Instead of describing tests in natural language, you can:
1. **Record** your interactions with the application (Playwright codegen or trace)
2. **Analyze** the recording against existing framework components
3. **Generate** only what's new (pages, locators, steps) while reusing what exists
4. **Get** production-ready BDD tests that match your framework's patterns

---

## Key Benefits

| Benefit | Description |
|---------|-------------|
| **Visual Workflow** | Record actions instead of describing them in text |
| **Accurate Selectors** | Real DOM elements captured, not AI-guessed |
| **Intelligent Reuse** | RAG automatically matches existing pages/locators/steps |
| **Framework Consistent** | Generates BasePage-compliant code with allure logging |
| **Faster Creation** | Record once vs. manual coding or long descriptions |
| **Non-Technical Friendly** | QA engineers can record, AI generates the code |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  1. RECORD USER ACTIONS                                     │
│     - Playwright Codegen (simple)                           │
│     - Playwright Trace (detailed)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  2. PARSE RECORDING → Extract Actions                       │
│     RecorderAnalyzer:                                       │
│     - Clicks, fills, selects, navigations                   │
│     - Selectors and values                                  │
│     - Page contexts (URLs)                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  3. RAG MATCHING → Find Existing Components                 │
│     For each action:                                        │
│     ✓ Query ChromaDB for similar pages                     │
│     ✓ Match selectors against existing locators            │
│     ✓ Identify reusable step definitions                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SMART GENERATION → Create Only What's New               │
│     - Reuse: AccountListPage.search_input                   │
│     - Create: WireTransferPage (new)                        │
│     - Reuse: "user fills {field} with {value}" step         │
│     - Create: "user submits wire transfer" step (new)       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  5. GENERATE ARTIFACTS                                      │
│     - .feature file (BDD scenarios)                         │
│     - *_steps.py (only new steps)                           │
│     - *_page.py (only new pages/locators)                   │
│     - test_*.py (runner)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup (One-Time)

### 1. Ensure Playwright is Installed

```bash
pip install playwright
playwright install
```

### 2. Index Your Framework (Enable RAG)

The recording analyzer needs RAG to match existing components:

```bash
python scripts/index_framework.py
```

This indexes:
- All page objects (pages/*.py)
- All step definitions (tests/bdd/steps/*_steps.py)
- All feature files (tests/bdd/features/*.feature)
- Locator mappings

**Important**: Re-run indexing after adding new pages or steps to keep RAG up-to-date.

### 3. Configure AI Provider

Ensure your `.env` file has AI credentials (same as regular AI generation):

```env
AI_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

---

## Usage Workflows

### Workflow 1: Interactive Recording (Recommended for Beginners)

**Step 1: Start Recording Mode**

```bash
python scripts/generate_from_recording.py \
  --start-recording \
  --feature-name "Add Wire Transfer Instructions" \
  --url "https://your-app.com"
```

**What Happens:**
- Playwright Inspector opens
- Browser launches to your URL
- You navigate and interact normally
- Recording is saved to `temp_recording.py`

**Step 2: Navigate and Record**
1. Log in (if needed)
2. Navigate to the feature you're testing
3. Perform all user actions (clicks, fills, selections)
4. Close the browser when done

**Step 3: Generate Tests from Recording**

```bash
python scripts/generate_from_recording.py \
  --codegen temp_recording.py \
  --feature-name "Add Wire Transfer Instructions"
```

**What Happens:**
- Analyzes your recording
- Matches against existing framework components
- Generates only new pages/locators/steps
- Outputs to `ai/generated/`

**Step 4: Review and Install**

Review the generated files:
```bash
ls ai/generated/
# wire_transfer_instructions.feature
# wire_transfer_steps.py
# wire_transfer_page.py
# test_wire_transfer.py
# _recording_metadata.json
```

Install into framework:
```bash
python scripts/generate_from_recording.py --install ai/generated
```

---

### Workflow 2: From Existing Codegen File

If you already have a codegen recording:

```bash
# 1. Generate the recording manually
playwright codegen https://your-app.com --output my_recording.py

# 2. Generate tests from it
python scripts/generate_from_recording.py \
  --codegen my_recording.py \
  --feature-name "Search Account"
```

---

### Workflow 3: From Trace File (Advanced)

Trace files contain more metadata (screenshots, network logs):

```bash
# 1. Create a trace during test execution
# In your test:
#   context = browser.new_context()
#   context.tracing.start(screenshots=True, snapshots=True)
#   # ... run test actions ...
#   context.tracing.stop(path="trace.zip")

# 2. Generate tests from trace
python scripts/generate_from_recording.py \
  --trace trace.zip \
  --feature-name "Complex User Flow"
```

---

## How RAG Matching Works

### Example: Wire Transfer Recording

**Your Recording:**
```python
page.goto("https://app.com/accounts")
page.locator("input[placeholder='Search accounts']").fill("12345")
page.locator("button:has-text('Search')").click()
page.locator("a:has-text('Account Wizard')").click()
page.locator("#wireBank").fill("Chase Bank")
page.locator("#wireRouting").fill("123456789")
page.locator("button:has-text('Submit')").click()
```

**RAG Analysis:**

| Action | Selector | RAG Match | Outcome |
|--------|----------|-----------|---------|
| Navigate | /accounts | ✓ `AccountListPage` exists | **Reuse** existing page |
| Fill | input[placeholder='Search accounts'] | ✓ `AccountListPage.search_input` | **Reuse** existing locator |
| Click | button:has-text('Search') | ✓ `AccountListPage.search_button` | **Reuse** existing locator |
| Click | a:has-text('Account Wizard') | ✓ `AccountListPage.account_wizard_link` | **Reuse** existing locator |
| Fill | #wireBank | ✗ No match | **Create** `WireTransferPage.bank_name_input` |
| Fill | #wireRouting | ✗ No match | **Create** `WireTransferPage.routing_number_input` |
| Click | button Submit | ✗ No match | **Create** `WireTransferPage.submit_button` |

**Generated Artifacts:**

```python
# NEW: pages/wire_transfer_page.py
class WireTransferPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.bank_name_input = page.locator("#wireBank")
        self.routing_number_input = page.locator("#wireRouting")
        self.submit_button = page.locator("button:has-text('Submit')")
```

```python
# NEW: tests/bdd/steps/wire_transfer_steps.py
@when('user fills bank name with "{value}"')
def fill_bank_name(wire_transfer_page, value):
    wire_transfer_page.fill_input(wire_transfer_page.bank_name_input, value)

# REUSES: common_steps.py already has fill_input for search!
```

```gherkin
# NEW: tests/bdd/features/wire_transfer.feature
Feature: Add Wire Transfer Instructions

  @smoke @wire_transfer
  Scenario: Add wire transfer for an account
    Given user navigates to account list
    When user fills search input with "12345"
    And user clicks search button
    And user clicks account wizard link
    And user fills bank name with "Chase Bank"
    And user fills routing number with "123456789"
    And user clicks submit button
    Then wire transfer should be successfully added
```

---

## Command Reference

### Start Interactive Recording
```bash
python scripts/generate_from_recording.py \
  --start-recording \
  --feature-name "Feature Name" \
  [--url "https://app.com"]
```

### Generate from Codegen File
```bash
python scripts/generate_from_recording.py \
  --codegen <file.py> \
  --feature-name "Feature Name" \
  [--output <dir>] \
  [--dry-run]
```

### Generate from Trace File
```bash
python scripts/generate_from_recording.py \
  --trace <trace.zip> \
  --feature-name "Feature Name" \
  [--output <dir>] \
  [--dry-run]
```

### Dry Run (Preview Only)
```bash
python scripts/generate_from_recording.py \
  --codegen temp_recording.py \
  --feature-name "Test Feature" \
  --dry-run
```

### Install Generated Files
```bash
python scripts/generate_from_recording.py \
  --install <ai/generated/directory>
```

---

## Advanced Usage

### Custom Output Directory
```bash
python scripts/generate_from_recording.py \
  --codegen recording.py \
  --feature-name "Complex Flow" \
  --output ./ai/generated/complex_flow
```

### Recording Authentication Flows

For login/auth, record once and commit:

```bash
# 1. Record login
playwright codegen https://app.com --output login_recording.py

# 2. Generate login test
python scripts/generate_from_recording.py \
  --codegen login_recording.py \
  --feature-name "User Login"

# 3. Install and commit to framework
python scripts/generate_from_recording.py --install ai/generated
```

Future recordings can skip login (use authentication state).

### Recording Multi-Page Flows

Complex flows across multiple pages work automatically:

```bash
# Records navigation across multiple pages
python scripts/generate_from_recording.py \
  --start-recording \
  --feature-name "End-to-End Wire Transfer"
```

RAG will:
- Match existing pages for Account List, Tracking Center, etc.
- Create only new pages (e.g., Wire Transfer form)
- Generate steps that work across all pages

---

## Programmatic API

### Python API Usage

```python
from ai.generator import AITestGenerator

# Initialize generator with RAG
gen = AITestGenerator(use_rag=True)

# Generate from codegen file
files = gen.generate_from_recording(
    recording_file="temp_recording.py",
    feature_name="Add Wire Transfer",
    recording_type="codegen",  # or "trace"
    output_dir="./ai/generated",
    dry_run=False
)

# Inspect generated files
for filename, content in files.items():
    print(f"Generated: {filename}")
```

### Recording Analysis API

```python
from ai.recorder_analyzer import RecorderAnalyzer

# Initialize analyzer
analyzer = RecorderAnalyzer(use_rag=True)

# Analyze codegen file
analysis = analyzer.analyze_codegen_file("recording.py")

# Inspect results
print(analysis.summary())
print(f"Actions recorded: {len(analysis.actions)}")
print(f"Matched pages: {len([m for m in analysis.matched_components.values() if m.match_type == 'page'])}")
print(f"Missing pages: {analysis.missing_pages}")
```

---

## Troubleshooting

### RAG Not Finding Existing Components

**Symptom:** All components are generated as new, nothing reused.

**Solution:**
```bash
# Re-index your framework
python scripts/index_framework.py

# Verify ChromaDB has documents
python -c "
import chromadb
client = chromadb.PersistentClient(path='./chromadb')
collection = client.get_collection('framework_docs')
print(f'Documents indexed: {collection.count()}')
"
```

### Playwright Codegen Not Found

**Symptom:** `playwright: command not found`

**Solution:**
```bash
pip install playwright
playwright install
```

### Recording Contains Too Many Irrelevant Actions

**Symptom:** Recording has debug clicks, navigation errors, etc.

**Solution:**
- Edit `temp_recording.py` manually before generation
- Remove unwanted actions
- Clean up selectors if needed

### Generated Selectors Are Too Specific

**Symptom:** Selectors like `div > div:nth-child(3) > button` are brittle.

**Solution:**
- Edit recording to use better selectors
- Or modify generated page objects
- Add data-testid attributes to your app

### AI Provider Not Configured

**Symptom:** `Failed to initialize AI generator`

**Solution:**
Check `.env` file has correct credentials:
```env
AI_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
```

---

## Best Practices

### 1. Record Clean, Focused Flows
- One feature per recording
- Remove debug/retry actions
- Use stable selectors (IDs, data-* attributes)

### 2. Keep RAG Index Updated
```bash
# After adding new pages/steps
python scripts/index_framework.py
```

### 3. Review Generated Code Before Installing
```bash
# Always review first
ls ai/generated/

# Check the code
cat ai/generated/new_page.py

# Then install
python scripts/generate_from_recording.py --install ai/generated
```

### 4. Leverage Existing Components
- RAG works best with a mature framework
- The more existing pages/steps, the better the reuse

### 5. Use Descriptive Feature Names
```bash
# Good
--feature-name "Add Wire Transfer Instructions"

# Less good
--feature-name "Test 1"
```

### 6. Combine with Natural Language Generation
```bash
# 1. Record to get structure
python scripts/generate_from_recording.py --start-recording --feature-name "Wire Transfer"

# 2. Refine with natural language
python scripts/generate_tests_ai.py --requirement "Add wire transfer with validation checks and error handling"
```

---

## Comparison: Recording vs. Natural Language

| Aspect | Recording | Natural Language |
|--------|-----------|------------------|
| **Input Method** | Visual (record actions) | Text (describe behavior) |
| **Selector Accuracy** | 100% (real DOM) | ~80% (AI guessed) |
| **Speed** | Fast (minutes) | Moderate (depends on desc) |
| **Technical Skill** | Low (anyone can record) | Moderate (clear description) |
| **Best For** | UI-heavy flows | Logic/validation tests |
| **Framework Reuse** | Excellent (RAG-powered) | Excellent (RAG-powered) |

**Recommendation**: Use **recording** for UI-driven flows, **natural language** for API/validation/edge cases.

---

## Examples

### Example 1: Simple Search Flow

```bash
# Record
python scripts/generate_from_recording.py \
  --start-recording \
  --feature-name "Search Account"

# In browser:
# 1. Navigate to /accounts
# 2. Fill search box with "12345"
# 3. Click Search
# 4. Verify results

# Generate
python scripts/generate_from_recording.py \
  --codegen temp_recording.py \
  --feature-name "Search Account"
```

**Result:** Reuses `AccountListPage`, generates minimal new code.

---

### Example 2: Complex Multi-Step Flow

```bash
# Record entire flow
python scripts/generate_from_recording.py \
  --start-recording \
  --feature-name "Wire Transfer End-to-End"

# In browser:
# 1. Search account
# 2. Open Account Wizard
# 3. Fill wire transfer form (bank, routing, account)
# 4. Submit
# 5. Verify in Tracking Center

# Generate
python scripts/generate_from_recording.py \
  --codegen temp_recording.py \
  --feature-name "Wire Transfer End-to-End"
```

**Result:**
- Reuses: `AccountListPage`, `TrackingCenterPage`, common steps
- Creates: `WireTransferPage` (new), wire transfer-specific steps

---

## Integration with CI/CD

Recording-based tests integrate seamlessly:

```yaml
# Azure Pipeline - Generate and run tests from recordings
- task: Bash@3
  displayName: "Generate Tests from Recordings"
  inputs:
    script: |
      # Recording artifacts from manual QA team
      for recording in recordings/*.py; do
        python scripts/generate_from_recording.py \
          --codegen "$recording" \
          --feature-name "$(basename $recording .py)"
      done

      # Install all generated tests
      python scripts/generate_from_recording.py --install ai/generated

- task: Bash@3
  displayName: "Run Generated Tests"
  inputs:
    script: pytest tests/bdd/ -m "generated" --alluredir=allure-results
```

---

## FAQ

**Q: Does recording replace manual test creation?**
A: No, it complements it. Use recording for UI flows, manual coding for complex logic/validation.

**Q: Can I edit recordings before generation?**
A: Yes! Edit `temp_recording.py` to clean up selectors or remove actions.

**Q: What if my app has dynamic selectors?**
A: Use data-testid attributes or edit generated page objects after.

**Q: Does this work with the auto-healing feature?**
A: Yes! Generated page objects use `BasePage`, which includes auto-healing.

**Q: Can I record mobile/tablet views?**
A: Yes, use Playwright device emulation:
```bash
playwright codegen --device="iPhone 12" https://app.com
```

**Q: How accurate is the RAG matching?**
A: Very accurate (>90%) for indexed components with clear selectors.

---

## Conclusion

Recording-based test generation combines the best of both worlds:
- **Visual simplicity** of recording
- **Intelligence** of RAG-powered reuse
- **Quality** of framework-consistent code generation

This workflow dramatically reduces test creation time while maintaining high code quality and framework consistency.

**Get Started:**
```bash
python scripts/generate_from_recording.py --start-recording --feature-name "My First Recording"
```
