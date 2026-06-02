@e2e @models @critical @test_add_model @regression
Feature: TC5 - Add Additional Strategies in draft model
  As a financial advisor
  I want to manage investment models

  Scenario: TC5 - Add Additional Strategies in draft model
    Given the user is on the draft models list
    And the user opens the most recently updated draft model
    And the user notes the current number of holdings
    When the user adds 2 additional strategies
    And the user allocates all holdings to total 100 percent
    And the user saves the model as draft
    Then the model contains additional strategies with saved allocations
    And the total allocation is 100 percent
    And model analytics are available
    And the changes persist after reload
    And the model can be published
