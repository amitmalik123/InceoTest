@e2e @models @critical @test_add_model @regression
Feature: TC4 - Edit Allocation Percentage in existing draft Model
  As a financial advisor
  I want to manage investment models

  Scenario: TC4 - Edit Allocation Percentage in existing draft Model
    Given the user is on the draft models list
    And the user opens the most recently updated draft model
    When the user updates holdings allocations to total 100 percent
    And the user saves the model as draft
    Then the total allocation is 100 percent
    And model analytics are available
    And the updated allocations persist after reload
    And the model can be published
