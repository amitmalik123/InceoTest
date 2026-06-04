"""
Test module for retain account feature using BDD approach
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

# Load all scenarios from the feature file
scenarios("../../features/naw/naw_document_options.feature")
