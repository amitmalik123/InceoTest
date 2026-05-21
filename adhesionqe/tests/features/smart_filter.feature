@happypath @smartfilter @e2e
Feature: Smart Filter Functionality

    @smoke @regression
    Scenario: Smart filter filtering
        When I navigate to the APro prospects page
        Then I should see the smart filter options
        And I capture the baseline row count
        When I select the "Proposal Started" filter
        Then the "Proposal Started" filter checkbox should be checked
        And The prospects list should be filtered accordingly
        When I remove the filter
        Then the "Proposal Started" filter checkbox should be unchecked
        And the prospects list row count should be at least the baseline count
