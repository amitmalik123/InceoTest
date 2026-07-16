@e2e @models @critical @test_add_model @smoke
Feature: TC1 - Validate user can access advisor model list page
  As a financial advisor
  I want to manage investment models

  Scenario: TC1 - Validate user can access advisor model list page
    Given the user is on the models page
    Then published models are shown by default
    And the drafts tab is available
    And model creation is available
    And the models list includes key business columns
    And the models list displays published model data


