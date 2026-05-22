# Shared Settings Singleton Issue

---

## Changes in This PR — Summary for Review

This PR makes four categories of changes: directory renames, file moves,
architectural fixes to the shared settings infrastructure, and pipeline updates.

### 1. Directory renames — PROPOSAL → proposal (lowercase)

All directories named PROPOSAL have been renamed to proposal throughout the
applicationqe project. This makes the codebase consistent with Python convention
(lowercase package names) and matches the naming used by other teams (stp, baw,
naw are already lowercase).

Files affected:

- config/PROPOSAL/ → config/proposal/
- pages/PROPOSAL/ → pages/proposal/
- tests/features/PROPOSAL/ → tests/features/proposal/
- tests/steps/PROPOSAL/ → tests/steps/proposal/
- tests/runners/PROPOSAL/ → tests/runners/proposal/
- data/PROPOSAL/ → data/proposal/
- queries/PROPOSAL/ → queries/proposal/
- utils/PROPOSAL/ → deleted (files moved, see below)

All Python import statements, pipeline YAML path filters, and internal config
string values that referenced PROPOSAL/ have been updated to proposal/.

### 2. File moves — helper_functions.py and proposal_pdf_utils.py

Two utility files that are specific to the proposal UI have been moved from
utils/PROPOSAL/ into pages/proposal/ where they logically belong:

- utils/PROPOSAL/helper_functions.py → pages/proposal/helper_functions.py
- utils/PROPOSAL/proposal_pdf_utils.py → pages/proposal/proposal_pdf_utils.py

These files contain functions for interacting with proposal pages and PDF
output. They belong in pages/ (page-specific helpers) not utils/ (shared
framework utilities). All import references in step files and other pages
have been updated to the new location.

### 3. Architecture fix — shared settings singleton contamination

This is the most significant change. See the full explanation below under
"Issue 1" and "Issue 2". In short:

Before this PR, every team that ran tests would silently load another team's
config at startup because two shared **init**.py files were eagerly
instantiating team-specific singletons and re-exporting them. This caused:

- FileNotFoundError crashes when a team member did not have another team's
  config directory checked out locally
- Silent config contamination (wrong base URLs, wrong credentials) when the
  config file happened to exist but pointed to the wrong environment

The fix has two parts:

Part A — Removed settings singletons from shared **init**.py files:

- config/**init**.py: removed re-export of the settings singleton
- utils/**init**.py: removed re-export of the settings singleton

  Shared **init**.py files now only export classes and functions (Settings,
  get_settings). No pre-instantiated objects. Teams that need the singleton
  call get_settings() explicitly in their own code.

Part B — Made TEST_CONFIG_PATH required in both settings files:

- config/settings.py: removed hardcoded fallback to config/proposal/. Now
  raises RuntimeError if TEST_CONFIG_PATH is not set.
- utils/settings.py: removed hardcoded fallback to config/stp/. Now raises
  RuntimeError if TEST_CONFIG_PATH is not set. Refactored singleton pattern
  to match config/settings.py (get_settings() function + PEP 562 **getattr**).

  This means the settings framework is now config-path-agnostic. No shared
  file has any team's path hardcoded. Each team controls their own config
  path via the TEST_CONFIG_PATH environment variable.

### 4. Pipeline changes — team-stage.yml and proposal.yml

To make TEST_CONFIG_PATH work in CI/CD without manual intervention:

- azure-pipelines/templates/team-stage.yml: added a new configPath parameter
  (default: empty string). The parameter is exported as the TEST_CONFIG_PATH
  environment variable in the test execution step alongside the existing
  TEST_ENV variable.

- azure-pipelines/proposal.yml: added configPath: config/proposal/env.$(TEST_ENV).yaml
  to the template parameters. Updated all path filters to use lowercase
  proposal/ (matching the directory rename above).

Each other team (STP, BAW, NAW) needs to add one line to their own YAML file.
See the "What each team needs to do" section at the bottom of this document.

### 5. Local development — .env file

Created applicationqe/.env with the proposal team's default values:

    TEST_ENV=test11
    TEST_CONFIG_PATH=config/proposal/env.test11.yaml

This file is gitignored and will not be committed. It means proposal team
members can run tests locally with a plain pytest command without setting
any environment variables in the terminal. Other teams create their own
.env file with their own values (see the guide at the bottom of this doc).

### 6. Added config/stp/ directory

The config/stp/ directory was added to this branch (pulled from develop).
It was not present on this branch because it was merged to develop after
this feature branch was created. It is needed because utils/settings.py
references STP config paths. Without it the test suite would crash on
machines that do not have develop merged in.

---

## Summary

There are two places in the applicationqe framework where a team-specific settings
singleton is instantiated at Python import time and re-exported from a shared
**init**.py file. This causes every team's tests to load another team's config
on startup, which either crashes (if the config file is missing) or silently
injects the wrong URLs and credentials into shared fixtures.

---

## Issue 1: utils/**init**.py re-exports the STP settings singleton

**File:** applicationqe/utils/**init**.py
**Line:** from utils.settings import Settings, settings

**What happens:**
Python executes utils/**init**.py whenever any module from the utils package is
imported — for example, "from utils.logger import setup_logger". This triggers
utils/settings.py to run at module level, which instantiates the STP team's
Settings class pointing to:

    config/stp/stp_moneyin_moneyout/env.{TEST_ENV}.yaml

**Impact:**

- Any team that imports a utils utility (logger, assertions, database helpers, etc.)
  triggers the STP config to load.
- If the STP config file is not present on the machine (e.g. a proposal or BAW
  team member who hasn't pulled that directory), the import crashes with
  FileNotFoundError and no tests can run.
- Even if it does not crash, the "settings" name in scope points to STP's
  environment — wrong base URL, wrong credentials, wrong test data paths.

**Recommended fix:**
Remove "settings" from the re-export in utils/**init**.py. Teams that need
utils.settings.settings should import it directly from utils.settings, not
from the shared utils package:

    # Remove from utils/__init__.py:
    from utils.settings import Settings, settings

    # STP team imports it directly where needed:
    from utils.settings import settings

---

## Issue 2: config/**init**.py re-exports the Proposal settings singleton

**File:** applicationqe/config/**init**.py
**Line:** from config.settings import Settings, get_settings, settings

**What happens:**
Python executes config/**init**.py whenever any module from the config package
is imported — for example, tests/conftest.py does "from config.settings import
get_settings", which triggers config/**init**.py, which instantiates the
Proposal team's Settings class pointing to:

    config/proposal/env.{TEST_ENV}.yaml

**Impact:**

- Every team's tests that share tests/conftest.py will load proposal config on
  startup.
- If the proposal config file is not present on the machine, the import crashes
  with FileNotFoundError and no tests can run.
- Even if it does not crash, any shared fixture that uses "settings" from the
  config package will get proposal URLs and credentials, not the running team's.

**Recommended fix:**
Remove "settings" from the re-export in config/**init**.py. The proposal team
imports it directly where needed:

    # Remove from config/__init__.py:
    from config.settings import Settings, get_settings, settings

    # Keep only the non-instantiating exports:
    from config.settings import Settings, get_settings

    # Proposal team imports the singleton directly where needed:
    from config.settings import settings

---

## Root cause

There are two related problems:

Problem A: Python executes **init**.py for a package the first time anything
in that package is imported. Re-exporting a singleton from **init**.py means
every consumer of the package pays the initialization cost of that singleton,
including teams that never use it.

Problem B: The shared settings files (config/settings.py and utils/settings.py)
both live in shared folders (config/ and utils/ respectively) but contain
hardcoded paths to one specific team's config directory. Since these are shared
files used by all teams, the hardcoded paths are wrong for everyone except the
team that wrote them.

---

## Full fix (two parts)

Part 1 — Remove the settings singleton re-exports from **init**.py files.

In config/**init**.py, change:
from config.settings import Settings, get_settings, settings
to:
from config.settings import Settings, get_settings

In utils/**init**.py, remove:
from utils.settings import Settings, settings

This stops the crash and contamination. Teams that need the singleton import
it directly from the source module.

Part 2 — Remove hardcoded team paths from the shared settings files.

config/settings.py hardcodes config/proposal/ and utils/settings.py hardcodes
config/stp/stp_moneyin_moneyout/. Since both files are in shared folders, the
path resolution must be dynamic, not hardcoded to one team.

The correct pattern is already partially implemented: utils/settings.py checks
for a TEST_CONFIG_PATH environment variable before falling back to a hardcoded
path. That fallback should be removed and TEST_CONFIG_PATH made required.

Each team's pipeline YAML sets TEST_CONFIG_PATH for their own config by passing
a configPath parameter to the shared team-stage.yml template:

    # team-stage.yml — new configPath parameter (default: "")
    - name: configPath
      type: string
      default: ""

    # team-stage.yml — exported alongside TEST_ENV in the test step
    export TEST_CONFIG_PATH="${{ parameters.configPath }}"

Each team's YAML passes their own path:

    proposal.yml:   configPath: config/proposal/env.$(TEST_ENV).yaml
    stp.yml:        configPath: config/stp/stp_moneyin_moneyout/env.$(TEST_ENV).yaml
    baw.yml:        configPath: config/baw/env.$(TEST_ENV).yaml
    naw.yml:        configPath: config/naw/env.$(TEST_ENV).yaml

The shared settings file then becomes config-path-agnostic:

    config_path = os.getenv("TEST_CONFIG_PATH")
    if not config_path:
        raise RuntimeError("TEST_CONFIG_PATH must be set. See your team pipeline YAML.")

---

## Why both fixes are needed — not just one

Part 2 (TEST_CONFIG_PATH) fixes WHICH config gets loaded.
Part 1 (remove from **init**.py) fixes WHO triggers loading it.

Even after Part 2 is applied, the **init**.py re-export is still a problem
because a Python singleton is created once per process and shared by everything
running in that process.

If a shared tests/conftest.py triggers config/**init**.py to instantiate
settings, that one settings object gets used by every test running in that
process. When a full regression pipeline runs all teams tests together in one
process, the first team's config wins for everyone else.

Removing settings from **init**.py means the singleton is never created unless
a team's own code explicitly asks for it by calling get_settings(). Each team
controls their own instantiation in their own conftest.py. The shared
tests/conftest.py no longer forces any team's config to load at startup.

Without Part 1, even with TEST_CONFIG_PATH working correctly, shared
infrastructure loading any team's config for everyone is still wrong
architecture. The two fixes solve different halves of the same problem.

---

## Ask for the broader team

1. Remove settings singleton re-exports from config/**init**.py and
   utils/**init**.py. Shared **init**.py files should only re-export classes,
   functions, and constants — never pre-instantiated objects that require
   environment-specific files to be present on disk.

2. Replace hardcoded team config paths in config/settings.py and
   utils/settings.py with TEST_CONFIG_PATH env var resolution. Add a configPath
   parameter to the shared team-stage.yml template and export it as
   TEST_CONFIG_PATH. Each team passes their own value in their pipeline YAML
   (proposal.yml, stp.yml, baw.yml, naw.yml). No team's path should be
   hardcoded in a shared file.

---

## What each team needs to do

### Pipeline (CI/CD)

Add the configPath parameter to your team's pipeline YAML file. This is a
one-line change alongside the existing stageName, teamDisplay, and featurePath
parameters:

    # Before
    - template: templates/team-stage.yml
      parameters:
        stageName: STP
        teamDisplay: STP
        featurePath: tests/runners/stp

    # After
    - template: templates/team-stage.yml
      parameters:
        stageName: STP
        teamDisplay: STP
        featurePath: tests/runners/stp
        configPath: config/stp/stp_moneyin_moneyout/env.$(TEST_ENV).yaml

Replace the configPath value with your team's own config directory:

    Proposal:   configPath: config/proposal/env.$(TEST_ENV).yaml
    STP:        configPath: config/stp/stp_moneyin_moneyout/env.$(TEST_ENV).yaml
    BAW:        configPath: config/baw/env.$(TEST_ENV).yaml
    NAW:        configPath: config/naw/env.$(TEST_ENV).yaml

### Local development — Option A: .env file (recommended)

Create a file named .env in the applicationqe/ directory (it is already
gitignored and will never be committed). Set both variables to match your team
and the environment you are testing against:

    TEST_ENV=test11
    TEST_CONFIG_PATH=config/proposal/env.test11.yaml

The settings module loads this file automatically at startup via load_dotenv().
You do not need to set anything in the terminal. Just create the file once and
forget it.

Example values by team:

    Proposal:   TEST_CONFIG_PATH=config/proposal/env.test11.yaml
    STP:        TEST_CONFIG_PATH=config/stp/stp_moneyin_moneyout/env.test11.yaml
    BAW:        TEST_CONFIG_PATH=config/baw/env.test11.yaml
    NAW:        TEST_CONFIG_PATH=config/naw/env.test11.yaml

Change test11 to test12, silo, or prod as needed.

### Local development — Option B: terminal session

Set both variables in your terminal once per session before running tests.
They persist until you close the terminal window.

PowerShell:

    $env:TEST_ENV="test11"
    $env:TEST_CONFIG_PATH="config/proposal/env.test11.yaml"

Bash/zsh (Mac/Linux):

    export TEST_ENV=test11
    export TEST_CONFIG_PATH=config/proposal/env.test11.yaml

Then run pytest normally without repeating them on every command.

---

## Adopted direction — team-owned settings + removal of config/settings.py

The TEST_CONFIG_PATH approach above was considered but not adopted. The actual
direction is simpler and follows the pattern already used by the STP team:

**Each team owns a settings.py file next to their own config YAMLs.**

    config/proposal/settings.py   ← proposal team owns this
    config/stp/settings.py        ← stp team owns this (already exists)
    config/baw/settings.py        ← baw team needs to create this
    config/naw/settings.py        ← naw team needs to create this

Each settings.py resolves its config path relative to its own location:

    self.config_path = Path(__file__).parent / f"env.{env}.yaml"

No TEST_CONFIG_PATH env var needed. Just TEST_ENV (e.g. test11, silo, prod).

Once all teams have their own settings.py, config/settings.py will be deleted.

---

## What teams need to do to enable deletion of config/settings.py

### Step 1 — Create config/{team}/settings.py

Copy config/proposal/settings.py as a starting point and update:

- All config path references to point to your team's directories
- Any team-specific properties (database_config, vault_databases, etc.)
- The \_load_queries() path to point to queries/{team}/sql_queries.yaml

### Step 2 — Update shared fixtures to use pytest fixture injection

The shared fixtures (fixtures/) currently import from config.settings directly.
This couples shared infrastructure to a specific team's config. The fix is
to inject settings via a pytest fixture instead of importing at module level.

Files that need to be updated (shared — coordinate across all teams):

    fixtures/auth_fixtures.py     lines 24, 124, 202
    fixtures/hooks_fixtures.py    line 13
    fixtures/data_fixtures.py     line 11
    tests/conftest.py             line 26

For each fixture function that calls get_settings() directly, add a `settings`
parameter and remove the direct import. Before/after example:

    # Before — direct import couples to one team's config
    from config.settings import get_settings

    @pytest.fixture(scope="session")
    def app_config():
        return get_settings().get_app_config()

    # After — injected; each team provides the `settings` fixture in their conftest
    @pytest.fixture(scope="session")
    def app_config(settings):
        return settings.get_app_config()

### Step 3 — Add a `settings` fixture to your team's conftest.py

Each team's conftest.py must define a session-scoped `settings` fixture that
returns an instance from their own settings module. This is what the shared
fixtures will receive via injection.

    # tests/runners/{team}/conftest.py
    import pytest
    from config.{team}.settings import get_settings

    @pytest.fixture(scope="session")
    def settings():
        return get_settings()

Proposal already does this in tests/runners/proposal/conftest.py.

### Step 4 — Update team-specific pages that import config.settings

Each team is responsible for their own page files. Pages in pages/{team}/
that import from config.settings should be updated to import from
config.{team}.settings instead.

Files by team:

    BAW team — pages/baw/:
        baw_login_page.py       line 5
        dashboard_page.py       line 3
        journal_utility_page.py line 3
        create_oa_page.py       line 4

    EWM team — pages/ewm/:
        account_wizard_page.py  line 5

    Shared (no clear owner — coordinate):
        pages/tracking_center_page.py   line 3

### Step 5 — Update shared utilities (coordinate across teams)

    utils/database.py       line 18
    utils/excel_utils.py    line 1077

These utilities use settings for optional config lookups. They should accept
settings as a parameter or use lazy optional imports with a fallback of None
so they remain usable without any settings object.

### Step 6 — Delete config/**init**.py re-export and config/settings.py

Once all steps above are complete across all teams:

    1. Remove the re-export from config/__init__.py:
           from config.settings import Settings, get_settings, settings
       Replace with an empty __init__.py or remove the line.

    2. Delete config/settings.py.

---

## Tracking checklist

- [x] config/proposal/settings.py created (proposal team — this PR)
- [ ] config/baw/settings.py created (BAW team)
- [ ] config/naw/settings.py created (NAW team)
- [ ] config/stp/settings.py verified/created (STP team)
- [ ] fixtures/auth_fixtures.py converted to fixture injection
- [ ] fixtures/hooks_fixtures.py converted to fixture injection
- [ ] fixtures/data_fixtures.py converted to fixture injection
- [ ] tests/conftest.py import removed
- [ ] pages/baw/ imports updated (BAW team)
- [ ] pages/ewm/ imports updated (EWM team)
- [ ] pages/tracking_center_page.py import updated
- [ ] utils/database.py updated
- [ ] utils/excel_utils.py updated
- [ ] config/**init**.py re-export removed
- [ ] config/settings.py deleted
