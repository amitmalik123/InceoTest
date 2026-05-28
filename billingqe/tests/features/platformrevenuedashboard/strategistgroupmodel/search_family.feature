Feature: Search Family
  As a Strategist Group user
  I want to search family records with different filters
  So that I can validate full, partial, and no-record search behavior

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @search @family @regression
  Scenario: Search Family matrix with ALL/Pending/Rejected filters
    When the user navigates to Strategist Group Model
    And the user verifies Strategist Group Model page is loaded
    And the user clicks the Family tab
    And the user verifies Family page is loaded for Search Family scenario
    When the user executes all search family validations from test data
    Then the user verifies search family validations completed successfully
    And the user logs out
