"""
Test runner for STP Add ACH and related E2E flows.

Loads scenarios from all main STP feature files (excluding Manage Bene
and prod validation which have their own runners).
"""
from pathlib import Path
from pytest_bdd import scenarios


APP_ROOT = Path(__file__).resolve().parents[3]  # …/applicationqe/

# ---------------------------------------------------------------------------
# Step definitions — full dotted imports (no sys.path manipulation needed
# now that all stp_* directories are valid Python packages).
# ---------------------------------------------------------------------------
from tests.steps.stp.stp_shared.account_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.account_wizard_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.api_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_aip.stp_cancelAip.cancel_aip_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.common_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.database_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_updateAddress.dmtaddresschangeconfirmationstep import *  # noqa: F401,F403
from tests.steps.stp.stp_updateAddress.dmtool_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_aip.stp_establishAip.establish_aip_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.item_details_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.login_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_addACHIntrcutions.manage_instruction_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_mimotransaction.mimo_summary_confirmation_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_mimotransaction.mimo_transaction_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.navigation_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_oaTradingTool.oa_tool_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.outlook_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.print_preview_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_swp.stp_establishSwp.swp_confirmation_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_swp.stp_establishSwp.swp_transaction_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_ict.test_roth_conversion_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.tracking_center_steps import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Feature files
# ---------------------------------------------------------------------------
_FEATURES = APP_ROOT / "tests/features/stp"

scenarios(str(_FEATURES / "stp_addACHIntrcutions/add_ACH.feature"))
# scenarios(str(_FEATURES / "stp_contributions/Contribution.feature"))
# scenarios(str(_FEATURES / "stp_withdrawals/Withdrawal.feature"))
# scenarios(str(_FEATURES / "stp_swp/stp_establishSwp/SWP.feature"))
# scenarios(str(_FEATURES / "stp_aip/stp_cancelAip/AIP.feature"))
# scenarios(str(_FEATURES / "stp_updateAddress/Address_change.feature"))
# scenarios(str(_FEATURES / "stp_aip/stp_establishAip/EstablishAIP.feature"))
# scenarios(str(_FEATURES / "stp_oaTradingTool/OA_tool.feature"))
