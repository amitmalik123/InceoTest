Feature: Journal Portion Transfer Shared Access2 E2E
    As a financial advisor
    I want to execute the shared-access journal portion transfer scenario
    So that I can submit and track the request using the existing orchestrated flow

    Background:
        Given the eWealth Manager application is available
        And test data is loaded for comprehensive journal transfer scenarios
        And I have test data for "journal_portion_transfer_shared_access2"
        And the test data is loaded from CSV

    @journal_transfer @e2e @orchestrated @shared_access @portion_transfer @journal_transfer_smoke
    Scenario: Execute journal_portion_transfer_shared_access2 using existing orchestrated flow
        When I execute the complete journal transfer orchestrated flow
        Then the orchestrated flow should complete successfully
        And I should have a valid request number
        And all required phases should be completed
        And the request should be trackable in the system
        And the shared access permissions should be properly handled
        And all stakeholders should have appropriate visibility
