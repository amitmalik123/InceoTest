@bdd @l2l_esign @end_to_end @esignature_flow
Feature: Like2Like eSign flow
  Validate the Like2Like eSign path using orchestrated flow execution and scenario_name mapping.

  Scenario: Execute Like2Like eSign orchestrated flow
    Given the eWealth Manager application is available
    And I have valid test credentials
    And test data is loaded for comprehensive journal transfer scenarios
    And I use Like2Like eSign scenario context
    And I have test data for "journal_portion_amount_with_esign5"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And all required phases should be completed
    And the request should be trackable in the system
