Feature: Edit Model
  As a Strategist Group user
  I want to edit model entries on the Model page
  So that I can update Family Name for models with or without existing family mapping

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @edit_model @edit @regression
  Scenario: Edit Model entry to update Family Name
    When the user navigates to Strategist Group Model
    And the user clicks the Model tab
    And the user verifies Model page is loaded for Edit Model scenario
    And the user verifies model grid action buttons are visible
    When the user edits model entry from test data
    Then the user verifies based on model type that only expected family edit controls are enabled and other attributes are grayed out
    And the user verifies updated model row is displayed with pending status and Edit and/or Approve Reject action buttons
    Then the user verifies edit model validations completed successfully
    And the user logs out
