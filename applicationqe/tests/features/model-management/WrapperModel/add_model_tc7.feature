@e2e @models @critical @test_add_model @regression
Feature: TC7 - Create Published Model
  As a financial advisor
  I want to manage investment models

  Scenario: TC7 Create Published Model
    Given the user is on the models page
    When the user creates a new model
    And the user adds 2 strategies to the model
    And the user allocates holdings equally to total 100 percent
    And the user saves the model as draft
    And the user submits the draft for publication
    Then model update summary metrics are displayed
    And holdings and asset allocation details are displayed
    And the model passes critical validations
    And the model is published successfully
