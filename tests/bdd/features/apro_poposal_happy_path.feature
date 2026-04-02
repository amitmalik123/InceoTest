@regression @proposal @e2e
Feature: APro poposal happy path

    Scenario: APro poposal happy path
        When I navigate to the APro prospects page
        Then I should see the APro prospects page
        And I start a new proposal
        And I complete the client details section for Guy Apro with investment amount 1000000
        And I complete the add holdings section with [["GOOG", 5, 250], ["NVDA", 2, 150], ["AAPL", 3, 170]]
        Then the holdings [["GOOG", 5, 250], ["NVDA", 2, 150], ["AAPL", 3, 170]] should be added to the proposal
        And I complete the Assess Risk section
        And I complete the select allocation section
        Then The proposal details should contain the expected information
        And I preview the proposal
        And I complete the generate report section with all reports
        Then the proposal should be generated with all reports
        Then the History/Actions section should contain the expected information
        Then I delete the proposal
