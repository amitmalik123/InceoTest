"""
PROPOSAL team Page Object Models.
"""

from .ewm_page import EwmPage
from .new_account_wizard_page import NewAccountWizardPage
from .portfolio_engine_page import PortfolioEnginePage
from .switch_id_page import SwitchIDPage
from .tax_management_services_page import TaxManagementServicesPage

__all__ = [
    "EwmPage",
    "NewAccountWizardPage",
    "PortfolioEnginePage",
    "SwitchIDPage",
    "TaxManagementServicesPage",
]
