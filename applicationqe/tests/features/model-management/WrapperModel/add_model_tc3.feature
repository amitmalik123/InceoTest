@e2e @models @critical @test_add_model @regression
Feature: TC3 - Edit Existing draft Model Name
  As a financial advisor
  I want to manage investment models

  Scenario: TC3 - Edit Existing draft Model Name
    Given the user is on the draft models list
    And the user opens the most recently updated draft model
    When the user updates the model name
    And the user saves the model as draft
    Then the updated model name is shown
    And the updated model name persists after reload
