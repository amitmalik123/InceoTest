Feature: Comprehensive Journal Transfer Scenarios - Orchestrated
  As a financial advisor
  I want to execute various journal transfer scenarios using the orchestrated workflow
  So that I can efficiently transfer client assets with different configurations

  Background:
    Given the eWealth Manager application is available
    And I have valid test credentials  
    And test data is loaded for comprehensive journal transfer scenarios

  @orchestrated @smoke @high_priority
  Scenario: Standard journal portion transfer using orchestrated flow
    Given I have test data for "journal_portion_transfer_standard1"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And all required phases should be completed
    And the request should be trackable in the system

  @orchestrated @rollover @medium_priority
  Scenario: Rollover to beneficiary transfer using orchestrated flow
    Given I have test data for "journal_portion_transfer_rollover_to_beneficiary1"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And the rollover configuration should be properly processed
    And the beneficiary information should be accurately captured

  @orchestrated @shared_access @medium_priority
  Scenario: Shared access transfer using orchestrated flow
    Given I have test data for "journal_portion_transfer_shared_access2"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And the shared access permissions should be properly handled
    And all stakeholders should have appropriate visibility

  @orchestrated @manual_transfer @medium_priority
  Scenario: Manual journal transfer using orchestrated flow
    Given I have test data for "journal_manual_transfer4"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And the manual transfer configuration should be processed
    And manual review requirements should be properly flagged

  @orchestrated @phase_validation @detailed
  Scenario: Phase-by-phase validation of orchestrated workflow
    Given I have test data for "journal_portion_transfer_standard1"
    When I execute the login flow phase
    Then I should be successfully authenticated
    When I execute the landing page flow phase
    Then I should be on the correct landing page
    When I execute the transfer configuration flow phase
    Then the transfer configuration should be properly set
    When I execute the transaction details flow phase
    Then the transaction details should be accurately captured
    When I execute the request summary flow phase
    Then the request summary should reflect all configurations
    When I execute the review and submission flow phase
    Then the request should be successfully submitted
    And I should have a valid request number with all phases completed

  @orchestrated @data_driven @comprehensive
  Scenario Outline: Data-driven journal transfer scenarios
    Given I have test data for "<scenario_name>"
    When I execute the complete journal transfer orchestrated flow
    Then the orchestrated flow should complete successfully
    And I should have a valid request number
    And at least <min_phases> phases should be completed
    And the scenario-specific validations should pass

    Examples:
      | scenario_name                                      | min_phases |
      | journal_portion_transfer_standard1                 | 8          |
      | journal_portion_transfer_rollover_to_beneficiary1  | 8          |
      | journal_portion_transfer_shared_access2            | 8          |
      | journal_manual_transfer4                           | 8          |

  @orchestrated @error_handling @negative
  Scenario: Orchestrated flow error handling validation
    Given I have invalid test data
    When I attempt to execute the complete journal transfer orchestrated flow
    Then the flow should handle errors gracefully
    And appropriate error messages should be logged
    And the system should remain in a consistent state
    And recovery mechanisms should be available

  @orchestrated @performance @load_test
  Scenario: Performance validation of orchestrated workflow
    Given I have test data for "journal_portion_transfer_standard1"
    When I execute the complete journal transfer orchestrated flow
    Then the flow should complete within acceptable time limits
    And each phase should meet performance benchmarks
    And resource utilization should remain within acceptable bounds
    And the system should handle the load efficiently

  @orchestrated @regression @critical
  Scenario: Regression testing with orchestrated flows
    Given I have multiple test scenarios available
    When I execute each scenario using the orchestrated flow
    Then all scenarios should complete successfully
    And no regressions should be detected
    And all business rules should be properly enforced
    And data integrity should be maintained throughout

  @orchestrated @comparison @validation
  Scenario: Orchestrated vs individual step comparison
    Given I have test data for "journal_portion_transfer_standard1"
    When I execute the same scenario using both approaches
    Then both approaches should produce identical results
    And the orchestrated approach should be more efficient
    And the orchestrated approach should provide better maintainability
    And error handling should be more robust in the orchestrated approach