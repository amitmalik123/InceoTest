"""
Test runner for STP Add ACH and related E2E flows.

Loads scenarios from all main STP feature files (excluding Manage Bene
and prod validation which have their own runners).
"""
from pathlib import Path
import sys

import pytest
from pytest_bdd import scenarios

# ---------------------------------------------------------------------------
# Path setup — hyphenated STP folder names cannot be used as Python modules,
# so we add each step directory to sys.path and import by filename.
# ---------------------------------------------------------------------------
APP_ROOT = Path(__file__).resolve().parents[3]  # …/applicationqe/

_STEP_DIRS = [
    "tests/steps/stp/stp-shared",
    "tests/steps/stp/stp-aip",
    "tests/steps/stp/stp-swp",
    "tests/steps/stp/stp-addACHIntrcutions",
    "tests/steps/stp/stp-updateAddress",
    "tests/steps/stp/stp-mimotransaction",
    "tests/steps/stp/stp-oaTradingTool",
    "tests/steps/stp/stp-ict",
]
for _d in _STEP_DIRS:
    sys.path.insert(0, str(APP_ROOT / _d))

# ---------------------------------------------------------------------------
# Step definitions
# ---------------------------------------------------------------------------
from account_steps import *  # noqa: F401,F403,E402
from account_wizard_steps import *  # noqa: F401,F403,E402
from api_steps import *  # noqa: F401,F403,E402
from cancel_aip_steps import *  # noqa: F401,F403,E402
from common_steps import *  # noqa: F401,F403,E402
from database_steps import *  # noqa: F401,F403,E402
from dmtaddresschangeconfirmationstep import *  # noqa: F401,F403,E402
from dmtool_steps import *  # noqa: F401,F403,E402
from establish_aip_steps import *  # noqa: F401,F403,E402
from item_details_steps import *  # noqa: F401,F403,E402
from login_steps import *  # noqa: F401,F403,E402
from manage_instruction_steps import *  # noqa: F401,F403,E402
from mimo_summary_confirmation_steps import *  # noqa: F401,F403,E402
from mimo_transaction_steps import *  # noqa: F401,F403,E402
from navigation_steps import *  # noqa: F401,F403,E402
from oa_tool_steps import *  # noqa: F401,F403,E402
from outlook_steps import *  # noqa: F401,F403,E402
from print_preview_steps import *  # noqa: F401,F403,E402
from swp_confirmation_steps import *  # noqa: F401,F403,E402
from swp_transaction_steps import *  # noqa: F401,F403,E402
from test_roth_conversion_steps import *  # noqa: F401,F403,E402
from tracking_center_steps import *  # noqa: F401,F403,E402

# ---------------------------------------------------------------------------
# Feature files
# ---------------------------------------------------------------------------
_FEATURES = APP_ROOT / "tests/features/stp"

scenarios(str(_FEATURES / "stp-addACHIntrcutions/add_ACH.feature"))
scenarios(str(_FEATURES / "stp-contributions/Contribution.feature"))
scenarios(str(_FEATURES / "stp-withdrawals/Withdrawal.feature"))
scenarios(str(_FEATURES / "stp-swp/stp-establishSwp/SWP.feature"))
scenarios(str(_FEATURES / "stp-aip/stp-cancelAip/AIP.feature"))
scenarios(str(_FEATURES / "stp-updateAddress/Address_change.feature"))
scenarios(str(_FEATURES / "stp-aip/stp-establishAip/EstablishAIP.feature"))
scenarios(str(_FEATURES / "stp-oaTradingTool/OA_tool.feature"))
