"""
Test runner for STP-ICT BDD scenarios.

Modelled on the stp-journals runner pattern:
  - Resolves repo root from this file's location
  - Adds the step directory to sys.path so step modules can be imported by bare name
  - Wildcard-imports all 13 ICT step modules so pytest-bdd can resolve step definitions
  - Loads all scenarios from ICT_E2E.feature in the same directory
"""
from pathlib import Path
import sys

from pytest_bdd import scenarios

# ── Path setup ────────────────────────────────────────────────────────────────
# File is at: tests/features/stp/stp-ict/test_ict_e2e_runner.py
# Repo root is 4 parents up:  stp-ict → stp → features → tests → applicationqe
REPO_ROOT = Path(__file__).resolve().parents[4]
STEP_DIR = REPO_ROOT / "tests" / "steps" / "stp" / "stp-ict"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(STEP_DIR))

# ── Step definitions (all 13 needed modules) ─────────────────────────────────
from account_number_steps import *       # noqa: F401, F403, E402
from account_steps import *              # noqa: F401, F403, E402
from account_wizard_steps import *       # noqa: F401, F403, E402
from client_suitability_steps import *   # noqa: F401, F403, E402
from common_steps import *               # noqa: F401, F403, E402
from create_fees_steps import *          # noqa: F401, F403, E402
from create_forms_steps import *         # noqa: F401, F403, E402
from docusign_steps import *             # noqa: F401, F403, E402
from ict_summary_steps import *          # noqa: F401, F403, E402
from login_steps import *                # noqa: F401, F403, E402
from navigation_steps import *           # noqa: F401, F403, E402
from select_destination_steps import *   # noqa: F401, F403, E402
from tracking_center_steps import *      # noqa: F401, F403, E402

# ── Scenarios ─────────────────────────────────────────────────────────────────
scenarios(Path(__file__).parent / "ICT_E2E.feature")
