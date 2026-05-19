# AI-Powered Test Generation Guide

## Overview

This framework includes an **AI test generator** that converts natural language requirements
directly into executable test automation artifacts:

| Input | Output |
|-------|--------|
| Requirement text (or .md/.txt file) | `.feature` file (BDD/Gherkin) |
| | Step definitions (`*_steps.py`) |
| | Page objects (`*_page.py`) |
| | Test runner (`test_*.py`) |
| | Pytest fixtures |

The AI understands your framework's exact patterns (pytest-bdd, BasePage, auto-healing,
allure logging, assertions) and generates code that matches 1:1.

---

## Architecture

```
┌──────────────────────────────┐
│  Requirement (text or file)  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  1. AnalysisAgent            │  ← Decides what to generate
│     (analyses existing code) │    (feature? steps? pages?)
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  2. FeatureGenerator         │  ← Generates .feature file
│     (reuses existing steps)  │    with proper tags & scenarios
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  3. StepGenerator            │  ← Only generates NEW steps
│     (skips existing ones)    │    (won't duplicate)
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  4. PageObjectGenerator      │  ← Generates page classes
│     (extends BasePage)       │    with Playwright locators
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  5. RunnerGenerator          │  ← Generates test_*.py
│     (imports & scenarios())  │    with correct imports
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  ai/generated/               │  ← Review → Install
└──────────────────────────────┘
```

---

## Setup (One-Time)

### Step 1: Install the OpenAI SDK

```bash
pip install openai>=1.0.0
```

### Step 2: Configure AI Provider

Add these to your `.env` file (project root):

**Option A: Azure OpenAI (Recommended – Enterprise)**
```env
AI_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-10-21
```

**Option B: OpenAI Direct**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
```

> **Azure OpenAI** is recommended since your team already uses Azure
> (Key Vault, Azure SQL). Ask your Azure admin to provision an
> Azure OpenAI resource and deploy a GPT-4o model.

### Step 3: Verify Setup

```bash
python scripts/generate_tests_ai.py --requirement "test" --dry-run --only analysis
```

---

## Usage

### 1. Full Pipeline (Recommended)

Generate all artifacts from a requirement:

```bash
# From requirement text
python scripts/generate_tests_ai.py \
  --requirement "User should be able to add wire transfer instructions for a client account. The flow includes navigating to Account List, searching for account, opening Account Wizard, filling wire details (bank name, routing number, account number), submitting, and verifying in Tracking Center."

# From a requirement file (more detailed = better results)
python scripts/generate_tests_ai.py \
  --file ai/sample_requirements/add_wire_transfer.md

# Dry run (preview without writing files)
python scripts/generate_tests_ai.py \
  --file ai/sample_requirements/add_wire_transfer.md \
  --dry-run
```

### 2. Generate Individual Artifacts

```bash
# Only the .feature file
python scripts/generate_tests_ai.py \
  --requirement "Add wire transfer instructions flow" \
  --only feature

# Only step definitions
python scripts/generate_tests_ai.py \
  --requirement "Add wire transfer instructions flow" \
  --only steps

# Only a page object (with UI element hints)
python scripts/generate_tests_ai.py \
  --requirement "Wire transfer instructions page" \
  --only page \
  --elements "bank name input, routing number input, account number input, account type dropdown, submit button, cancel link"

# Only analyse (see what would be generated)
python scripts/generate_tests_ai.py \
  --requirement "Add wire transfer instructions" \
  --only analysis
```

### 3. Install Generated Files

After reviewing the generated files:

```bash
python scripts/generate_tests_ai.py --install ai/generated/
```

This copies files to the correct framework directories:
| Generated File | Installed To |
|---------------|-------------|
| `*.feature` | `tests/bdd/features/` |
| `*_steps.py` | `tests/bdd/steps/` |
| `*_page.py` | `pages/` |
| `test_*.py` | `tests/bdd/test_runners/` |
| `_new_fixtures.py` | Appended to `tests/bdd/conftest.py` |

---

## How It Works

### Smart Analysis
The AI first scans your existing framework to understand:
- **Existing feature files** → avoids duplicates
- **Existing step definitions** → reuses them (won't recreate "When I navigate to Clients menu")
- **Existing page objects** → knows what's already built

### Pattern Matching
The prompts include real examples from YOUR codebase:
- Your exact `@when(parsers.parse(...))` pattern
- Your `BasePage` class structure
- Your `get_allure_logger()` logging pattern
- Your `Assertions` class usage
- Your `test_context` dict for data sharing
- Your fixture injection pattern

### What Gets Generated

**Feature File** (`.feature`):
```gherkin
@e2e @add_wire @critical
Feature: Add Wire Transfer Instructions E2E flow
  As a financial advisor
  I want to add wire transfer instructions

  @regression @wire
  Scenario: Successfully add wire transfer instructions
    When I load test data from excel sheet "WireTransfer"
    When I navigate to Clients menu
    And I click on Account List
    Then User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    When User clicks on Add Wire Instructions button
    And User selects "Wire" radio button and clicks Next
    Then User enters wire transfer details for bank "Chase Bank"
    ...
```

**Step Definitions** (`wire_transfer_steps.py`):
```python
@when("User clicks on Add Wire Instructions button")
def click_add_wire(authenticated_page: Page, account_wizard_page: AccountWizardPage):
    """Click Add Wire Instructions on Account Wizard."""
    logger.info("Clicking Add Wire Instructions button")
    account_wizard_page.click_add_wire_instructions()
```

**Page Object** (`wire_transfer_page.py`):
```python
class WireTransferPage(BasePage):
    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.bank_name_input: Locator = page.locator("#bankName")
        self.routing_number_input: Locator = page.locator("#routingNumber")
        ...
```

---

## Best Practices

### Writing Good Requirements

**Bad** (too vague):
> "Test the wire transfer feature"

**Good** (specific flow with details):
> "User should be able to add wire transfer instructions. Flow: Navigate to
> Clients > Account List, search account by number, open Account Wizard,
> click Add Wire Instructions, fill in bank name, routing number, account
> number, select account type (Checking/Savings), choose No SLOA option,
> submit, verify confirmation page, check Tracking Center for completion."

**Best** (use a structured requirement file):
See `ai/sample_requirements/add_wire_transfer.md` for an example template.

### Review Before Installing
Always review generated code before installing:
1. Check locator selectors match your actual UI
2. Verify step text matches your team's conventions
3. Ensure page object methods cover the actual interactions
4. Update locators with real selectors from browser DevTools

### Iterative Refinement
1. Generate with `--dry-run` first
2. Review the output
3. Adjust your requirement text and regenerate
4. Install when satisfied
5. Update locators manually after inspecting the real UI

---

## Using AI in Python Code (Programmatic)

```python
from ai.generator import AITestGenerator

gen = AITestGenerator()

# Analyse what needs to be generated
analysis = gen.analyse_requirement("Add wire transfer instructions...")
print(analysis)

# Generate individual pieces
feature = gen.generate_feature_file("Add wire transfer requirement...")
steps = gen.generate_step_definitions(feature)
page = gen.generate_page_object("Wire transfer page", "bank name input, routing number input")

# Full pipeline
results = gen.generate_from_requirement(
    requirement="ai/sample_requirements/add_wire_transfer.md",
    output_dir="ai/generated/wire_transfer",
    dry_run=False,
)
```

---

## File Structure

```
ai/
├── __init__.py              # Module init
├── prompts.py               # All AI prompt templates
├── generator.py             # Core AI engine
├── generated/               # Default output directory (gitignored)
│   ├── _analysis.json       # What was decided to generate
│   ├── add_wire.feature     # Generated feature file
│   ├── wire_steps.py        # Generated step definitions
│   ├── wire_page.py         # Generated page object
│   ├── test_wire.py         # Generated test runner
│   └── _new_fixtures.py     # Generated fixtures
└── sample_requirements/     # Example requirement templates
    └── add_wire_transfer.md # Sample requirement file
```

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `EnvironmentError: Set AZURE_OPENAI_ENDPOINT` | Add AI config to `.env` file |
| `ImportError: openai` | Run `pip install openai>=1.0.0` |
| Generated locators are wrong | Expected — update with real selectors from DevTools |
| Steps duplicate existing ones | The AI scans existing steps but may miss some; remove duplicates manually |
| `openai.RateLimitError` | Wait and retry, or use a higher-tier Azure OpenAI deployment |

---

## Security Notes

- API keys are read from environment variables (`.env` file, never committed)
- Azure OpenAI stays within your Azure tenant (enterprise-compliant)
- Generated code goes to `ai/generated/` for review before installation
- No test data or credentials are sent to the AI — only requirement text
