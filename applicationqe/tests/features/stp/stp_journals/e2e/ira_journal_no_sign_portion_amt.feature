Feature: IRA Journal Transfer - No Signature Portion Amount E2E
    As a financial advisor
    I want to execute an IRA journal portion transfer without obtaining client signature
    So that I can transfer $45.00 from one Traditional IRA to another using the submit-to-review path

    Background:
        Given the eWealth Manager application is available
        And I have test data for "ira_journal_no_sign_portion_amt"
        And the test data is loaded from CSV

    @journal_transfer @e2e @ira_journal @no_signature @portion_transfer @submit_to_review @ira
    Scenario: Complete E2E IRA journal portion transfer with no signature
        # Login Phase
        Given I am on the login page
        When I handle cookie consent banner using multiple strategies  
        And I login with valid credentials
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

        # Transaction Configuration - IRA Portion Amount
        When I select "Journal Portion of Account" as the distribution type
        And I take a screenshot of "Distribution Type Selected"
        And I configure the journal portion with amount "45.00" and portion type "$ Amount"
        And I take a screenshot of "Transfer Amount Configured"
        And I select "Do Not Obtain Client Signature(s)" as the signature option
        And I take a screenshot of "No Signature Option Selected"
        And I click Next to proceed to the summary page
        And I take a screenshot of "Request Summary Loaded"

        # Submit without Signature
        When I click the Submit to Review button
        And I take a screenshot of "After Submit To Review"
        Then the completed request summary page should be displayed
        And I take a screenshot of "Request Confirmation Displayed"
        
        # Tracking Center Verification
        When I click the A or B number to open tracking center  
        Then I should see my submitted transaction details in the tracking center
        And I take a screenshot of "Tracking Center Verification"

    @journal_transfer @e2e @ira_journal @no_signature @regression
    Scenario Outline: IRA journal no-signature portion amount with different amounts
        Given I have test data for "ira_journal_no_sign_portion_amt"
        And I modify the transaction amount to "<amount>"
        When I execute the complete journal transfer flow
        Then the request should be submitted successfully via "Submit to Review"
        And the confirmation should display "Portion of Account | $<amount>"
        
        Examples:
            | amount |
            | 25.00  |
            | 50.00  |
            | 100.00 |