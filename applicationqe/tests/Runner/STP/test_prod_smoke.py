from pathlib import Path
import sys
import pytest
from pytest_bdd import scenarios

APP_ROOT = Path(__file__).resolve().parents[3]

_STEP_DIRS = [
    'tests/steps/stp/stp-shared',
    'tests/steps/stp/stp-aip',
    'tests/steps/stp/stp-swp',
    'tests/steps/stp/stp-addACHIntrcutions',
    'tests/steps/stp/stp-updateAddress',
    'tests/steps/stp/stp-mimotransaction',
    'tests/steps/stp/stp-manageBene',
    'tests/steps/stp/stp-oaTradingTool',
    'tests/steps/stp/stp-ict',
]
for _d in _STEP_DIRS:
    sys.path.insert(0, str(APP_ROOT / _d))

from account_steps import *  # noqa: F401,F403,E402
from account_wizard_steps import *  # noqa: F401,F403,E402
from add_bene_steps import *  # noqa: F401,F403,E402
from api_steps import *  # noqa: F401,F403,E402
from cancel_aip_steps import *  # noqa: F401,F403,E402
from common_steps import *  # noqa: F401,F403,E402
from database_steps import *  # noqa: F401,F403,E402
from dmtaddresschangeconfirmationstep import *  # noqa: F401,F403,E402
from dmtool_steps import *  # noqa: F401,F403,E402
from establish_aip_steps import *  # noqa: F401,F403,E402
from item_details_steps import *  # noqa: F401,F403,E402
from login_steps import *  # noqa: F401,F403,E402
from manage_bene_steps import *  # noqa: F401,F403,E402
from manage_instruction_steps import *  # noqa: F401,F403,E402
from mimo_summary_confirmation_steps import *  # noqa: F401,F403,E402
from mimo_transaction_steps import *  # noqa: F401,F403,E402
from navigation_steps import *  # noqa: F401,F403,E402
from oa_tool_steps import *  # noqa: F401,F403,E402
from print_preview_steps import *  # noqa: F401,F403,E402
from swp_confirmation_steps import *  # noqa: F401,F403,E402
from swp_transaction_steps import *  # noqa: F401,F403,E402
from test_roth_conversion_steps import *  # noqa: F401,F403,E402
from tracking_center_steps import *  # noqa: F401,F403,E402

# TODO: uncomment when prod features are migrated to STP
# _FEATURES = APP_ROOT / 'tests/features/stp'
# scenarios(str(_FEATURES / 'stp-addACHIntrcutions/prod/prod_add_ach.feature'))
# scenarios(str(_FEATURES / 'stp-contributions/prod/prod_contribution.feature'))
# scenarios(str(_FEATURES / 'stp-swp/stp-establishSwp/prod/prod_SWP.feature'))
# scenarios(str(_FEATURES / 'stp-aip/stp-establishAip/prod/prod_EstablishAIP.feature'))
# scenarios(str(_FEATURES / 'stp-withdrawals/prod/prod_Withdrawal.feature'))
# scenarios(str(_FEATURES / 'stp-aip/stp-cancelAip/prod/prod_AIP.feature'))
# scenarios(str(_FEATURES / 'stp-updateAddress/prod/prod_address_change.feature'))
# scenarios(str(_FEATURES / 'stp-oaTradingTool/prod/prod_OA_tool.feature'))
