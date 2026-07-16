"""
Test module for BAW features using the shared BDD runner.
"""

from pytest_bdd import scenarios

# Import step definitions
from tests.steps.baw.construct_portfolio_step import *  # noqa
from tests.steps.baw.view_documents_step import *  # noqa
from tests.steps.baw.baw_login_steps import *  # noqa
from tests.steps.baw.baw_dashboard_steps import *  # noqa
from tests.steps.baw.shell_process_steps import *  # noqa
from tests.steps.baw.search_work_item_steps import *  # noqa
from tests.steps.baw.naa_coach_steps import *  # noqa
from tests.steps.baw.transfer_attributes_step import *  # noqa
from tests.steps.baw.create_oa_step import *  # noqa
from tests.steps.baw.journal_utility_step import *  # noqa
from tests.steps.baw.withdrawal_step import *  # noqa
from tests.steps.baw.check_contributions_steps import *  # noqa

# Load remaining BAW feature files.
scenarios("../../features/baw/baw_account_activation.feature")
scenarios("../../features/baw/baw_shell_journal.feature")
scenarios("../../features/baw/baw_transfer_records.feature")
scenarios("../../features/baw/baw_Check_Association_To_Transfer.feature")
scenarios("../../features/baw/baw_withdrawal.feature")
scenarios("../../features/baw/baw_Agent_notification.feature")
scenarios("../../features/baw/baw_check_extraction.feature")
