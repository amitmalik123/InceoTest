Feature: Complete Journal Transfer End-to-End User Journey
    As a financial advisor using eWealth Manager
    I want to complete journal transfers from login to tracking
    So that I can efficiently transfer assets between accounts with full visibility

    Background:
        Given the eWealth Manager application is available
        And I have valid test credentials
        And test data is loaded for journal transfer scenarios

    @e2e @complete_flow @smoke @critical @journal_transfer_portion
    Scenario: Complete Journal Transfer Flow - Standard Portion Transfer
        # STEP 1: LOGIN FLOW - Authentication and Cookie Consent
        Given I navigate to the login page
        When I handle cookie consent if present
        And I enter my username and password credentials
        And I click the sign in button
        Then I should be successfully authenticated
        And I should be redirected to the home page
        And the URL should contain "en.aspx"

        # STEP 2: LANDING PAGE FLOW - Home Page Verification  
        Given I am on the authenticated home page
        When I verify the landing page has loaded correctly
        Then the home page elements should be visible
        And I should have access to navigation options
        
        # STEP 3: TRANSFER PAGE FLOW - Journal Transfer Configuration
        Given I navigate to the journal transfer page
        When the journal transfer page loads
        Then I should see the "Transfer Assets Between Accounts" heading
        And I should see the journal transfer form
        And I should see available destination accounts
        
        When I dismiss the live chat popup if present
        And I select a destination account from the available list
        And I click the Next button to proceed to transaction details
        Then the transaction configuration page should load
        And I should see source and destination account details
        And I should see distribution type options
        
        When I select "Journal Portion of Account" as distribution type
        And I select "$ Amount" as the portion type
        And I enter the transfer amount
        And I select "Obtain Electronic Client Signature(s)" as the signature option
        Then the transaction configuration should be complete
        And the Next button should be enabled
        
        # STEP 4: SUMMARY PAGE FLOW - Review and Submission
        When I click Next to proceed to the summary page
        Then the transaction summary page should load
        And I should see the transaction details summary
        And I should see the correct source and destination accounts
        And I should see the correct transfer amount
        And I should see the signature option selected
        
        When I click the Submit button
        Then the transaction should be submitted successfully
        And I should see a confirmation message
        And I should receive a transaction reference number
        
        # STEP 5: TRACKING CENTER FLOW - Transaction Confirmation
        When I navigate to the tracking center
        Then I should see the tracking center page
        And I should see my submitted transaction in the list
        And I should see the correct transaction status
        And I should see the transaction details match my submission

    @e2e @complete_flow @securities @esignature @high
    Scenario: Complete Journal Transfer Flow - Securities Transfer with E-Signature
        # STEP 1: LOGIN FLOW
        Given I navigate to the login page
        When I complete the login process with cookie consent
        Then I should be successfully authenticated

        # STEP 2: LANDING PAGE FLOW
        Given I am on the authenticated home page  
        Then the landing page should be verified

        # STEP 3: TRANSFER PAGE FLOW - Securities Configuration
        Given I navigate to the journal transfer page
        When I complete the initial page setup
        And I select a destination account
        And I proceed to transaction details
        And I select "Journal Securities" as distribution type
        Then I should see the securities selection interface
        
        When I select securities using the "All" buttons
        And I select "Obtain Electronic Client Signature(s)" as the signature option
        Then the securities configuration should be complete
        
        # STEP 4: E-SIGNATURE CONFIGURATION FLOW
        When I proceed to the e-signature configuration page
        Then I should see the e-signature setup form
        
        When I select an authorized user from the dropdown
        And I enter the client email address
        And I enter the client phone number
        And I check the e-signature confirmation checkbox
        And I proceed to the e-signature summary page
        Then the e-signature configuration should be complete
        
        # STEP 5: SUMMARY PAGE FLOW - E-Signature Summary
        When I review the securities transfer with e-signature summary
        Then I should see the securities transfer e-signature summary
        And I should see the selected securities details
        And I should see the e-signature configuration details
        
        When I submit the securities transfer with e-signature
        Then the securities e-signature transaction should be submitted successfully
        
        # STEP 6: TRACKING CENTER FLOW  
        When I check the tracking center for e-signature transaction
        Then the securities e-signature transfer should appear in tracking
        And the e-signature status should be correctly displayed

    @e2e @complete_flow @esignature @high  
    Scenario: Complete Journal Transfer Flow - Electronic Signature
        # STEP 1: LOGIN FLOW
        Given I navigate to the login page
        When I complete the login process with cookie consent  
        Then I should be successfully authenticated

        # STEP 2: LANDING PAGE FLOW
        Given I am on the authenticated home page
        Then the landing page should be verified

        # STEP 3: TRANSFER PAGE FLOW - E-Signature Configuration  
        Given I navigate to the journal transfer page
        When I complete the account selection process
        And I configure the transaction details
        And I select "Obtain Electronic Client Signature" as the signature option
        Then the transaction should be configured for e-signature
        
        # STEP 4: SUMMARY PAGE FLOW - Electronic Signature Handling
        When I proceed to the e-signature section
        Then I should see the electronic signature configuration page
        And I should see email and phone number fields
        
        When I enter the client email address
        And I enter the client phone number  
        And I check the confirmation checkbox
        And I proceed to the final summary
        Then I should see the complete transaction summary with e-signature
        
        When I submit the transaction with e-signature
        Then the transaction should be submitted for electronic signature
        And I should see confirmation of the e-signature process
        
        # STEP 5: TRACKING CENTER FLOW
        When I check the tracking center for e-signature transaction
        Then the e-signature transaction should appear in tracking
        And the status should indicate pending e-signature

    @e2e @error_handling @medium
    Scenario: Complete Flow Error Handling and Recovery
        # Test error scenarios and recovery
        Given I have an invalid test data scenario
        When I attempt to execute the complete flow
        Then an appropriate error should be raised
        And the error message should be informative
        
        Given I have valid test data after the error
        When I execute the complete flow again
        Then the flow should succeed after recovery
        And all steps should complete successfully

    @e2e @individual_steps @debug @low
    Scenario: Individual Flow Step Validation
        # Test individual steps for debugging
        Given I want to validate individual flow steps
        
        When I execute only the login flow step
        Then the login step should complete successfully
        And I should be on the home page
        
        When I execute the landing page flow step
        Then the landing page validation should pass
        
        When I execute the transfer page flow step  
        Then the transfer page configuration should complete
        And I should have a configured transaction

    @e2e @performance @monitoring @medium
    Scenario: Complete Flow Performance Monitoring
        # Monitor performance of the complete flow
        Given I want to monitor the complete flow performance
        
        When I execute the complete flow with timing
        Then each step should complete within acceptable time limits:
            | Step | Maximum Time |
            | Login Flow | 30 seconds |
            | Landing Page Flow | 10 seconds |  
            | Transfer Page Flow | 60 seconds |
            | Summary Page Flow | 30 seconds |
            | Tracking Center Flow | 20 seconds |
        
        And the total flow should complete within 3 minutes
        And all screenshots should be captured successfully
        And the allure report should contain all step details

    @e2e @data_driven @scenarios @medium  
    Scenario Outline: Complete Flow with Different Test Scenarios
        # Test the complete flow with different data scenarios
        Given I have test data for scenario "<scenario_name>"
        
        When I execute the complete journal transfer flow
        Then all flow steps should complete successfully
        And the transaction should be submitted with "<expected_type>" type
        And the tracking center should show "<expected_status>" status
        
        Examples:
            | scenario_name | expected_type | expected_status |
            | journal_portion_transfer_standard1 | Portion Transfer | Submitted |
            | journal_securities_transfer_standard | Securities Transfer | Submitted |
            | journal_other_account_scenario | Other Account Transfer | Submitted |

    @e2e @cross_browser @compatibility @low
    Scenario: Complete Flow Cross-Browser Compatibility
        # Test complete flow across different browsers
        Given I want to test cross-browser compatibility
        
        When I execute the complete flow in different browsers:
            | Browser |
            | chromium |
            | firefox |
            | webkit |
        
        Then the complete flow should work consistently across all browsers
        And all validations should pass in each browser
        And screenshots should be captured for each browser