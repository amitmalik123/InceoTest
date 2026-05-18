Feature: Journal Transfer Request End-to-End Workflow
    As a financial advisor
    I want to complete the entire journal transfer request process from login to submission
    So that I can efficiently process asset transfers between client accounts with proper documentation

    @journal_transfer_request @e2e @complete_workflow @smoke
    Scenario: Complete Journal Transfer Request from Login to Submission
        Given the eWealth Manager application is available
        And I have valid test credentials
        And test data is loaded for journal transfer scenarios
        And I navigate to the login page
        
        When I handle cookie consent if present
        And I enter my username and password credentials
        And I click the sign in button
        And I verify the landing page has loaded correctly
        
        Given I navigate to the journal transfer page
        When the journal transfer page loads
        And I dismiss the live chat popup if present
        And I select a destination account from the available list
        And I click the Next button to proceed to transaction details
        
        When I select "Journal Portion of Account" as distribution type
        And I select "$ Amount" as the portion type
        And I enter the transfer amount
        When I select "Obtain Electronic Client Signature(s)" as the signature option
        And I click the Next button to proceed to the review page
        
        When I verify that all entered details are correct on the review page
        And I click the Submit button to finalize the journal transfer request
        Then I should see a confirmation message indicating successful submission
        

        