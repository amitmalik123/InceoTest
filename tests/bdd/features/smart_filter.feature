@happypath @smartfilter @e2e
Feature: Smart Filter Functionality

    @smoke @regression
    Scenario: Smart filter filtering
        When I navigate to the APro prospects page
        Then I should see the smart filter options
        When I select the "Proposal Started" filter
        Then The prospects list should be filtered accordingly
        When I remove the filter
        Then The prospects list should be unfiltered
