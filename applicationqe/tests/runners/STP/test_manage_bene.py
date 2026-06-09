from pathlib import Path
from pytest_bdd import scenarios

APP_ROOT = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------------
# Step definitions — full dotted imports (no sys.path manipulation needed).
# ---------------------------------------------------------------------------
from tests.steps.stp.stp_shared.account_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.account_wizard_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_manageBene.add_bene_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.api_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.common_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.database_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.item_details_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.login_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_manageBene.manage_bene_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_addACHIntrcutions.manage_instruction_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_mimotransaction.mimo_summary_confirmation_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_mimotransaction.mimo_transaction_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.navigation_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_oaTradingTool.oa_tool_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.print_preview_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_ict.test_roth_conversion_steps import *  # noqa: F401,F403
from tests.steps.stp.stp_shared.tracking_center_steps import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Feature files
# ---------------------------------------------------------------------------
_FEATURES = APP_ROOT / 'tests/features/stp'
scenarios(str(_FEATURES / 'stp_manageBene/Manage_bene.feature'))
