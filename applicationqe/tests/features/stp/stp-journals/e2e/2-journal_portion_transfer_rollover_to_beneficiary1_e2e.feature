Feature: Journal Portion Transfer Rollover To Beneficiary1 E2E
    As a financial advisor
    I want to execute rollover-to-beneficiary journal portion transfer
    So that I can submit and track a valid request using the existing orchestrated flow

    Background:
        Given the eWealth Manager application is available
        And test data is loaded for comprehensive journal transfer scenarios
        And I have test data for "journal_portion_transfer_rollover_to_beneficiary1"
        And the test data is loaded from CSV

    @journal_transfer @e2e @orchestrated @rollover @portion_transfer @journal_transfer_smoke
    Scenario: Execute journal_portion_transfer_rollover_to_beneficiary1 using existing orchestrated flow
        When I execute the complete journal transfer orchestrated flow
        Then the orchestrated flow should complete successfully
        And I should have a valid request number
        And all required phases should be completed
        And the request should be trackable in the system
        And the rollover configuration should be properly processed
        And the beneficiary information should be accurately captured
