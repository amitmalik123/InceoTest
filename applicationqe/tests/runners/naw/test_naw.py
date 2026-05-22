"""
Test module for NAW feature using BDD approach
"""

from pytest_bdd import scenarios

# Import step definitions
from tests.steps.common_steps import *  # noqa
from tests.steps.naw.navbar_common_steps import *  # noqa
from tests.steps.naw.dashboard_steps import *  # noqa
from tests.steps.naw.clients_steps import *  # noqa
from tests.steps.naw.account_wizard_steps import *  # noqa
from tests.steps.naw.client_profile_step import *  # noqa
from tests.steps.naw.construct_portfolio_step import *  # noqa
from tests.steps.naw.fees_step import *  # noqa
from tests.steps.naw.portfolio_details_step import *  # noqa
from tests.steps.naw.account_setup_step import *  # noqa
from tests.steps.naw.review_all_accounts_step import *  # noqa
from tests.steps.naw.create_documents_step import *  # noqa
from tests.steps.naw.view_documents_step import *  # noqa
from tests.steps.naw.docusign_step import *  # noqa
from tests.steps.naw.tracking_center_steps import *  # noqa
from tests.steps.baw.baw_login_steps import *  # noqa
from tests.steps.baw.baw_dashboard_steps import *  # noqa
from tests.steps.baw.shell_process_steps import *  # noqa
from tests.steps.baw.search_work_item_steps import *  # noqa
from tests.steps.baw.naa_coach_steps import *  # noqa
from tests.steps.naw.account_approval_step import *  # noqa
# Add other step files as needed

# Load all scenarios from the feature files
scenarios("../../features/naw/NAW.feature")
