@happypath @exportbutton @e2e
Feature: Export Prospects

    @smoke @regression
    Scenario: Export prospects list unfiltered
        When I navigate to the APro prospects page
        Then I should see the export button
        When I click the export button
        Then The prospects list should be exported successfully

    @smoke @regression
    Scenario: Export prospects list filtered
        When I navigate to the APro prospects page
        Then I should see the smart filter options
        When I select the "Questionnaire Completed" filter
        Then The prospects list should be filtered accordingly
        When I click the export button
        Then The filtered prospects list should be exported successfully
