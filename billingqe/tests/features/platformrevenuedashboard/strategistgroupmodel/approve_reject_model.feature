Feature: Approve / Reject Model
  As a Strategist Group user
  I want to approve or reject a model record
  So that I can manage the lifecycle of models

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @approve_reject @model @regression
  Scenario: Approve/Reject Model with valid data
    When the user navigates to Strategist Group Model
    And the user verifies Strategist Group Model page is loaded
    And the user clicks the Model tab
    And the user verifies Model page is loaded with action buttons
    And the user searches for model to approve or reject from test data
    And the user clicks Approve/Reject button for the model
    And the user verifies model Approve/Reject dialog is displayed
    When the user performs the approve or reject action for model based on test data
    Then the user verifies the model action was successful
    And the user verifies the model status is updated correctly
    And the user logs out
