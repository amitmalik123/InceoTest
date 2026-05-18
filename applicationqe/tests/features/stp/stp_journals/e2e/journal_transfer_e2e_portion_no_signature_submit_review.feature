Feature: Journal Transfer E2E - Portion Amount with No Signature Submit to Review
    As a financial advisor
    I want to submit a journal portion transfer without obtaining signature
    So that the request is routed through the submit-to-review path

    @journal_transfer @e2e @portion_amount @no_signature @submit_to_review
    Scenario: Portion no-signature submit-to-review
        Given I navigate to the login page
        When I handle cookie consent if present
        And I enter my username and password credentials
        And I click the sign in button
        Then I should be successfully authenticated
        Given I navigate to the journal transfer page
        When the journal transfer page loads
        And I dismiss the live chat popup if present
        And I select a destination account from the available list
        And I click the Next button to proceed to transaction details
        And I select "Journal Portion of Account" as distribution type
        And I click the "Enter Details" button to access the form
        And I select "$ Amount" as the portion type
        And I enter the transfer amount
        And I select "Do Not Obtain Client Signature(s)" as the signature option
        And I click Next to proceed to the summary page
        And I click the Submit to Review button
        Then the completed request summary page should be displayed
        When I click the A or B number to open tracking center
        Then I should see my submitted transaction details in the tracking center
