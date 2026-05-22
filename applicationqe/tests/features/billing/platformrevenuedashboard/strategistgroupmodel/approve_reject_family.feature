Feature: Approve / Reject Family
  As a Strategist Group user
  I want to approve or reject a family record
  So that I can manage the lifecycle of model families

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @approve_reject @family @regression
  Scenario: Approve/Reject Family with valid data
    When the user navigates to Strategist Group Model
    And the user verifies Strategist Group Model page is loaded
    And the user clicks the Family tab
    And the user verifies Family page is loaded with Approve/Reject button
    And the user searches for family to approve or reject from test data
    And the user clicks Search for family
    And the user verifies search results are displayed
    And the user clicks Approve/Reject button for the family
    And the user verifies Approve/Reject dialog is displayed
    When the user performs the approve or reject action based on test data
    Then the user verifies the action was successful
    And the user verifies the family status is updated correctly
    And the user logs out
