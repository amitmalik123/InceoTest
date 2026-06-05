"""
Test Data Loader Utility
Handles loading and processing of test data for journal transfer tests.
"""
import csv
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

import pytest

from utils.settings import Settings


def _set_nested_value(target: dict, key_path: str, value):
    """Set nested dictionary value using dot notation key path"""
    current = target
    parts = key_path.split(".")
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


def _normalize_csv_value(key_path: str, value):
    """Normalize CSV string values into nested scenario-friendly types."""
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped == "":
        return ""

    if stripped.lower() == "null":
        return None

    if stripped.lower() == "true":
        return True

    if stripped.lower() == "false":
        return False

    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    if key_path.startswith("timeouts.") and stripped.isdigit():
        return int(stripped)

    return stripped


def _get_active_settings() -> Settings:
    """Resolve settings using the active test environment."""
    return Settings(env=os.getenv("TEST_ENV", "test11"))


def _read_csv_scenario(csv_path: Path, scenario_name: str) -> Dict[str, Any]:
    """Read test scenario from the configured CSV file."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV test data file does not exist: {csv_path}")

    with open(csv_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in CSV test data file: {csv_path}")

    for row in rows:
        if row.get("name") != scenario_name:
            continue

        scenario = {}
        for header, cell_value in row.items():
            if not header:
                continue
            _set_nested_value(scenario, header, _normalize_csv_value(header, cell_value))

        return scenario

    raise ValueError(f"Scenario '{scenario_name}' not found in CSV test data: {csv_path}")


def load_test_data(scenario_name: str = "journal_portion_transfer_standard1",
                   excel_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load test data from the environment-resolved CSV file.
    
    Args:
        scenario_name: Name of the test scenario to load
        excel_path: Deprecated and ignored. Retained for call compatibility.
        
    Returns:
        Dictionary containing test scenario data
        
    Raises:
        ValueError: If scenario not found in test data
        FileNotFoundError: If the CSV file does not exist
    """
    del excel_path

    active_settings = _get_active_settings()
    return normalize_account_data(_read_csv_scenario(active_settings.test_data_csv, scenario_name))


def get_all_test_scenarios() -> list:
    """Get list of all available test scenarios"""
    try:
        active_settings = _get_active_settings()
        with open(active_settings.test_data_csv, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            return [row.get("name") for row in reader if row.get("name")]
    except Exception:
        return []


def normalize_account_data(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize destination account fields for scenarios with destinationAccounts array
    
    Args:
        test_data: Test data dictionary to normalize
        
    Returns:
        Normalized test data with flat destination account fields
    """
    accts = test_data.get('accounts', {})
    
    if 'destinationAccounts' in accts and isinstance(accts['destinationAccounts'], list):
        if accts['destinationAccounts']:  # Check if array is not empty
            first_dest = accts['destinationAccounts'][0]
            accts.setdefault('destinationAccountName', first_dest.get('accountName', ''))
            accts.setdefault('destinationAccountNumber', first_dest.get('accountNumber', ''))
    
    return test_data


def extract_advisor_id_from_url(test_data: Dict[str, Any]) -> Optional[str]:
    """Extract advisor ID from journal transfer URL"""
    try:
        url = test_data["urls"]["journalTransferUrl"]
        # Expecting format: ...&Advisor=AGARLP&...
        advisor_param = [param for param in url.split("&") if param.startswith("Advisor=")]
        if advisor_param:
            return advisor_param[0].split("=")[1]
    except:
        pass
    return None


def prepare_test_data_for_scenario(scenario_name: str, **overrides) -> Dict[str, Any]:
    """
    Prepare test data for a scenario with optional field overrides
    
    Args:
        scenario_name: Name of test scenario to load
        **overrides: Field overrides to apply to test data
        
    Returns:
        Prepared test data with normalizations and overrides applied
    """
    # Load base test data
    test_data = load_test_data(scenario_name)
    
    # Apply normalizations
    test_data = normalize_account_data(test_data)
    
    # Apply overrides
    for key, value in overrides.items():
        if "." in key:
            # Handle nested keys like "transactionDetails.signatureOption"
            _set_nested_value(test_data, key, value)
        else:
            test_data[key] = value
    
    return test_data


# Predefined test data configurations for common scenarios
class TestDataPresets:
    """Predefined test data configurations for common test scenarios"""
    
    @staticmethod
    def standard_journal_transfer() -> Dict[str, Any]:
        """Standard journal portion transfer configuration"""
        return prepare_test_data_for_scenario("journal_portion_transfer_standard1")
    
    @staticmethod
    def journal_transfer_with_esignature() -> Dict[str, Any]:
        """Journal transfer with electronic signature configuration"""
        return prepare_test_data_for_scenario(
            "journal_portion_transfer_standard1",
            **{"transactionDetails.signatureOption": "Obtain Electronic Client Signature"}
        )
    
    @staticmethod
    def journal_transfer_with_print_signature() -> Dict[str, Any]:
        """Journal transfer with print signature configuration"""
        return prepare_test_data_for_scenario(
            "journal_portion_transfer_standard1",
            **{"transactionDetails.signatureOption": "Print to Obtain physical Client Signature"}
        )
    
    @staticmethod
    def journal_securities_transfer() -> Dict[str, Any]:
        """Journal securities transfer configuration"""
        return prepare_test_data_for_scenario(
            "journal_portion_transfer_standard1",
            **{"transactionDetails.distributionType": "Journal Securities"}
        )
    
    @staticmethod
    def rollover_to_beneficiary_transfer() -> Dict[str, Any]:
        """Rollover to beneficiary transfer configuration"""
        return prepare_test_data_for_scenario("journal_portion_transfer_rollover_to_beneficiary1")
    
    @staticmethod
    def shared_access_transfer() -> Dict[str, Any]:
        """Shared access transfer configuration"""
        return prepare_test_data_for_scenario("journal_portion_transfer_shared_access2")


# Constants for commonly used test scenarios
STANDARD_SCENARIOS = [
    "journal_portion_transfer_standard1",
    "journal_portion_transfer_rollover_to_beneficiary1", 
    "journal_portion_transfer_shared_access2",
    "journal_manual_transfer4"
]

PARAMETRIZED_SCENARIOS = [
    pytest.param("journal_portion_transfer_standard1", id="standard_transfer"),
    pytest.param("journal_portion_transfer_rollover_to_beneficiary1", id="rollover_beneficiary"),
    pytest.param("journal_portion_transfer_shared_access2", id="shared_access"),
    pytest.param("journal_manual_transfer4", id="manual_transfer")
]