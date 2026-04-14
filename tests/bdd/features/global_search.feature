@happypath @global_search @e2e
Feature: Global Search

    @smoke @regression
    Scenario: Global Search
        When I search for client "628-454003"
        Then the Actions list loads
        When I select the Create/Edit Proposal action
        Then I should be taken to the Proposal page
