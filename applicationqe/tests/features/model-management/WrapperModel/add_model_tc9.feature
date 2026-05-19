@e2e @models @critical @test_add_model @regression
Feature: TC9 - Add Strategy to Published Model
  As a financial advisor
  I want to manage investment models

  Scenario: TC9 - Add Strategy to Published Model
    Given the user is on the published models list
    And the user opens an existing published model in edit mode
    And the user notes the current number of holdings
    When the user adds 2 additional strategies
    And the user allocates all holdings to total 100 percent
    And the user saves the model as draft
    Then the model contains additional strategies with saved allocations
    And the total allocation is 100 percent
    And model analytics are available
