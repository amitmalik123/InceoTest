from pathlib import Path
import sys

from pytest_bdd import scenarios


# # Resolve repo root from tests/features/stp/stp-journals/e2e
# REPO_ROOT = Path(__file__).resolve().parents[5]
# STP_JOURNALS_ROOT = REPO_ROOT / "tests" / "steps" / "stp" / "stp-journals"
# STEP_DIR = REPO_ROOT / "tests" / "steps" / "stp" / "stp-journals" / "e2e"

# sys.path.insert(0, str(REPO_ROOT))
# sys.path.insert(0, str(STP_JOURNALS_ROOT))
# sys.path.insert(0, str(STEP_DIR))

# # Import all ES3 stp-journals step functions into this module namespace so
# # pytest-bdd can resolve step definitions for generated scenarios.
# from account_steps import *  # noqa: F401,F403
# from account_wizard_steps import *  # noqa: F401,F403
# from common_steps import *  # noqa: F401,F403
# from complete_journal_transfer_steps import *  # noqa: F401,F403
# from comprehensive_orchestrated_steps import *  # noqa: F401,F403
# from direct_page_access_steps import *  # noqa: F401,F403
# from e2e_portion_no_signature_steps import *  # noqa: F401,F403
# from ira_journal_steps import *  # noqa: F401,F403
# from journal_portion_transfer_standard1_e2e_steps import *  # noqa: F401,F403
# from journal_transfer_request_steps import *  # noqa: F401,F403
# from like2like_esign_flow_steps import *  # noqa: F401,F403
# from login_steps import *  # noqa: F401,F403
# from navigation_steps import *  # noqa: F401,F403
# from orchestrated_flow_steps import *  # noqa: F401,F403
# from roth_conversion_steps import *  # noqa: F401,F403
# from tracking_center_steps import *  # noqa: F401,F403


# FEATURE_DIR = Path(__file__).parent
# for feature_file in sorted(FEATURE_DIR.glob("*.feature")):
#     scenarios(feature_file)
