Feature: Search Model
  As a Strategist Group user
  I want to search model records by Model ID
  So that I can validate status-based action buttons and no-record behavior

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @search_model @search @regression
  Scenario: Search Model with status-action validation and no-record handling
    When the user navigates to Strategist Group Model
    And the user clicks the Model tab
    And the user verifies Model page is loaded for Search Model scenario
    When the user executes search model validations from test data
    Then the user verifies search model validations completed successfully
    And the user logs out
