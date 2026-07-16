@e2e @models @critical @test_add_model @smoke @regression
Feature: TC2 - Validate user can create a model and allocate holdings
  As a financial advisor
  I want to manage investment models

  Scenario: TC2 - Validate user can create a model and allocate holdings
    Given the user is on the models page
    When the user starts a new model
    And the user adds 2 strategies to the model
    And the user allocates holdings equally to total 100 percent
    And the user saves the model as draft
    Then the model is saved as a draft with a valid model identifier
    And model analytics are available
    And the model can be published
