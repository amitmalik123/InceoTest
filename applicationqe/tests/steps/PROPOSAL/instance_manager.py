"""
Instance manager for storing page objects per worker for parallel test execution.
"""

import logging
import os
from typing import Dict

from pages.PROPOSAL import (
    EwmPage,
    NewAccountWizardPage,
    PortfolioEnginePage,
    TaxManagementServicesPage,
)

logger = logging.getLogger(__name__)

# Store instances per worker to support parallel test execution
_ewm_page_instances: Dict[str, EwmPage] = {}
_new_account_wizard_instances: Dict[str, NewAccountWizardPage] = {}
_portfolio_engine_instances: Dict[str, PortfolioEnginePage] = {}
_tax_mgmt_services_instances: Dict[str, TaxManagementServicesPage] = {}


def _get_worker_id() -> str:
    """Get the current worker ID for parallel test execution."""
    return os.getenv("PYTEST_XDIST_WORKER", "master")


def set_ewm_page_instance(instance: EwmPage) -> None:
    """Store EWM page instance for current worker."""
    worker_id = _get_worker_id()
    logger.debug(f"[{worker_id}] Setting EwmPage instance")
    _ewm_page_instances[worker_id] = instance


def get_ewm_page_instance() -> EwmPage:
    """Retrieve EWM page instance for current worker."""
    worker_id = _get_worker_id()
    instance = _ewm_page_instances.get(worker_id)
    if not instance:
        raise ValueError(f"EwmPage not initialized for worker {worker_id}")
    return instance


def set_new_account_wizard_instance(instance: NewAccountWizardPage) -> None:
    """Store NewAccountWizard page instance for current worker."""
    worker_id = _get_worker_id()
    logger.debug(f"[{worker_id}] Setting NewAccountWizardPage instance")
    _new_account_wizard_instances[worker_id] = instance


def get_new_account_wizard_instance() -> NewAccountWizardPage:
    """Retrieve NewAccountWizard page instance for current worker."""
    worker_id = _get_worker_id()
    instance = _new_account_wizard_instances.get(worker_id)
    if not instance:
        raise ValueError(f"NewAccountWizardPage not initialized for worker {worker_id}")
    return instance


def set_portfolio_engine_instance(instance: PortfolioEnginePage) -> None:
    """Store PortfolioEngine page instance for current worker."""
    worker_id = _get_worker_id()
    logger.debug(f"[{worker_id}] Setting PortfolioEnginePage instance")
    _portfolio_engine_instances[worker_id] = instance


def get_portfolio_engine_instance() -> PortfolioEnginePage:
    """Retrieve PortfolioEngine page instance for current worker."""
    worker_id = _get_worker_id()
    instance = _portfolio_engine_instances.get(worker_id)
    if not instance:
        raise ValueError(f"PortfolioEnginePage not initialized for worker {worker_id}")
    return instance


def set_tax_mgmt_services_instance(instance: TaxManagementServicesPage) -> None:
    """Store TaxManagementServices page instance for current worker."""
    worker_id = _get_worker_id()
    logger.debug(f"[{worker_id}] Setting TaxManagementServicesPage instance")
    _tax_mgmt_services_instances[worker_id] = instance


def get_tax_mgmt_services_instance() -> TaxManagementServicesPage:
    """Retrieve TaxManagementServices page instance for current worker."""
    worker_id = _get_worker_id()
    instance = _tax_mgmt_services_instances.get(worker_id)
    if not instance:
        raise ValueError(f"TaxManagementServicesPage not initialized for worker {worker_id}")
    return instance


def clear_all_instances(worker_id: str | None = None) -> None:
    """Clear all stored instances for a worker (for cleanup between tests)."""
    target_worker = worker_id or _get_worker_id()
    _ewm_page_instances.pop(target_worker, None)
    _new_account_wizard_instances.pop(target_worker, None)
    _portfolio_engine_instances.pop(target_worker, None)
    _tax_mgmt_services_instances.pop(target_worker, None)
    logger.debug(f"[{target_worker}] Cleared all page instances")
