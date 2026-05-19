"""Re-export shim — steps have been split into per-wizard-step modules.

Import from the individual modules directly, or use this file for backwards
compatibility with any wildcard import (`from ... import *`).
"""

from tests.bdd.steps.Adhesion.apro_step_allocation_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_details_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_fees_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_generate_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_history_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_holdings_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_prospects_list_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_risk_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_tax_management_steps import *  # noqa: F401, F403
