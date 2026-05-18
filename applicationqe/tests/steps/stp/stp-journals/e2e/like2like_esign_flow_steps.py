"""BDD steps dedicated to the Like2Like eSign flow."""

from pytest_bdd import given


@given("I use Like2Like eSign scenario context")
def given_use_like2like_context(test_context: dict, comprehensive_flow_context: dict):
    """Set flow context. Scenario data resolved by scenario_name journal_portion_amount_with_esign5."""
    test_context["flow_name"] = "like2like_esign"
    comprehensive_flow_context["flow_name"] = "like2like_esign"
    # Ensure the scenario_name is pre-set so given_specific_test_data uses it correctly.
    test_context["scenario_name"] = "journal_portion_amount_with_esign5"

