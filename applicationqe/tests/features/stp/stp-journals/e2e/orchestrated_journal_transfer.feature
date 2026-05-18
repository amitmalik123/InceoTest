Feature: Complete Journal Transfer Flow - Orchestrated 11-Phase Workflow
  As a financial advisor
  I want to execute journal transfer requests using the complete orchestrated workflow
  So that I can efficiently transfer client assets between accounts

  Background:
    Given the eWealth Manager application is available
    And I have valid test credentials
    And test data is loaded for journal transfer scenarios

  @complete_e2e @high_priority @smoke
  Scenario: Execute complete journal transfer E2E flow using orchestrated workflow
    Given I navigate to the login page
    When I execute the complete end-to-end flow
    Then the complete flow results should be successful
    And I should have a valid request number
    And the journal transfer flow should complete successfully
    And I should be able to track the request

  @phase_by_phase @detailed
  Scenario: Execute journal transfer flow phase by phase with orchestrated workflow
    Given I navigate to the login page
    When I execute the complete login flow
    Then I should be successfully authenticated
    
    When I execute the landing page flow
    And I execute the transfer configuration flow
    And I execute the transaction details flow
    And I execute the request summary flow
    And I execute the review and submission flow
    Then I should have a valid request number
    And the journal transfer flow should complete successfully
    And I should be able to track the request

  @portion_transfer @standard
  Scenario: Execute portion transfer using orchestrated workflow
    Given I navigate to the login page
    When I execute the complete login flow
    Then I should be successfully authenticated
    
    When I execute the landing page flow
    And I execute the transfer configuration flow
    And I execute the transaction details flow
    And I execute the request summary flow
    And I execute the review and submission flow
    Then I should have a valid request number
    And the journal transfer flow should complete successfully

  @no_signature @quick_test
  Scenario: Execute journal transfer without signature requirement
    Given I navigate to the login page
    When I execute the complete login flow
    Then I should be successfully authenticated
    
    When I execute the landing page flow
    And I execute the transfer configuration flow 
    And I execute the transaction details flow
    And I execute the request summary flow
    And I execute the review and submission flow
    Then I should have a valid request number
    And the journal transfer flow should complete successfully