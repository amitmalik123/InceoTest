
import pytest

from tests.api.STP.services.beneficiaryHouseholdService import BeneficiaryHouseholdService


@pytest.fixture
def beneficiary_household_service():
    """Beneficiary Household service object fixture"""
    return BeneficiaryHouseholdService()


