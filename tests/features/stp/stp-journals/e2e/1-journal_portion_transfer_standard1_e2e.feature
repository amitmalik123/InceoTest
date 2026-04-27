Feature: Journal Portion Transfer Standard1 E2E with Screenshots
    As a financial advisor
    I want to execute a complete end-to-end journal portion transfer for standard1 scenario
    So that I can successfully transfer $45.00 with full visual documentation of each screen

    Background:
        Given the eWealth Manager application is available
        And I have test data for "journal_portion_transfer_standard1"
        And the test data is loaded from CSV

    @journal_transfer_smoke @e2e @screenshots @standard1 @portion_transfer @high_priority
    Scenario: Complete E2E journal portion transfer standard1 with screenshots
        # Login Phase with Screenshots
        Given I am on the login page
        And I take a screenshot of "Login Page Initial Load"
        When I handle cookie consent banner using multiple strategies  
        And I take a screenshot of "After Cookie Consent Handling"
        And I login with valid credentials
        And I take a screenshot of "After Login Submission"
        Then I should be redirected to the home page
        And I take a screenshot of "Authentication Successful - Home Page"

        # Navigation to Journal Transfer
        When I execute the landing page flow phase
        And I take a screenshot of "Landing Page Navigation"
        Given I navigate to the journal transfer page
        And I take a screenshot of "Journal Transfer Page Loaded"
        When I select a destination account from the available list
        And I take a screenshot of "Destination Account Selected"
        And I click the Next button to proceed to transaction details
        And I take a screenshot of "Transaction Details Page Loaded"

        # Transaction Configuration
        When I select "Journal Portion of Account" as the distribution type
        And I take a screenshot of "Distribution Type Selected"
        And I configure the journal portion with amount "45.00" and portion type "$ Amount"
        And I take a screenshot of "Transfer Amount Configured"
        #When I execute the transfer configuration flow phase
        And I take a screenshot of "Transfer Configuration Completed"

        # Transaction Details
        When I execute the transaction details flow phase
        And I take a screenshot of "Transaction Details Configured"

        # Review and Submit  
        When I execute the review and submission flow phase
        And I take a screenshot of "Request Summary Loaded"
        # Note: Review, submission, confirmation, completion, and tracking are handled within this phase
        And I take a screenshot of "After Submission"

        # Verification
        Then the orchestrated flow should complete successfully
        And I should have a valid request number
        And the request should be trackable in the system
        And I take a screenshot of "Final Verification Complete"

    @journal_transfer @e2e @screenshots @standard1 @negative_testing
    Scenario: Error handling during journal portion transfer standard1 with screenshots
        Given I am on the login page
        And I take a screenshot of "Error Test - Login Page"
        # Test invalid login - reuse existing validation logic
        Then I should see appropriate error handling
        And I take a screenshot of "Error State Documented"

    @journal_transfer @e2e @screenshots @standard1 @validation_testing  
    Scenario: Form validation during journal portion transfer standard1 with screenshots
        Given the eWealth Manager application is available
        And I have test data for "journal_portion_transfer_standard1"
        And the test data is loaded from CSV
        And I am on the login page
        When I login with valid credentials
        Then I should be redirected to the home page
        And I take a screenshot of "Validation Test - Authenticated"
        # Test form validation using existing orchestrated flow validation
        When I attempt to execute the complete journal transfer orchestrated flow
        Then the validation should handle incomplete data appropriately
        And I take a screenshot of "Form Validation Documented"