@e2e @models @critical @test_add_model @regression @smoke
Feature: TC6 - Remove Strategy and Adjust Allocation
  As a financial advisor
  I want to manage investment models

  Scenario: TC6 - Remove Strategy and Adjust Allocation
    Given the user is on the draft models list
    And the user opens a draft model with at least 3 strategies
    When the user removes one strategy from the model
    Then the save draft button is disabled
    When the user adjusts all holdings to total 100 percent
    And the user saves the model as draft
    Then the total allocation is 100 percent
    And no validation errors are displayed
    And model analytics are available
    And the model can be published
