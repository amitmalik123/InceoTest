Feature: Journal Transfer Functionality
    As a financial advisor
    I want to create journal transfers between client accounts  
    So that I can move assets efficiently while maintaining compliance

    Background:
        Given I am on the eWealth Manager login page
        When I enter my credentials and handle cookie consent
        Then I should be successfully logged in to the home page

    @journal_transfer @smoke @authentication
    Scenario: Complete Login Flow with Cookie Consent
        Given I navigate to the login page "https://test11.ewealthmanager.com/ewmLogin/account/login"
        Then the login page should load successfully
        And the page title should contain "AssetMark"
        And username and password fields should be visible
        When I handle cookie consent banner using multiple strategies
        Then the cookie consent banner should be dismissed
        And no consent-related overlays should remain
        When I enter username credentials in the username field
        Then the username field should accept input without validation errors
        When I enter password credentials in the password field  
        Then the password field should accept input and mask the text
        When I click the SIGN IN button
        Then the button click should be registered and navigation should begin
        And the URL should change to contain "en.aspx"
        And I should be authenticated and redirected to home page

    @journal_transfer @navigation
    Scenario: Navigate to Journal Transfer Page
        Given I am logged in to the application
        When I navigate to journal transfer URL with advisor, household, and account parameters
        Then the journal transfer page should load
        And the page title should be "AssetMark - Digital Maintenance"
        And "Transfer Assets Between Accounts" heading should be visible
        When I dismiss live chat popup if present
        Then the chat interface should not obstruct page elements
        And the main content area should be fully accessible
        And the transfer page heading should be displayed
        And journal sub-heading text should be visible
        And advisor ID should be shown on page
        And navigation buttons should be present

    @journal_transfer @account_selection @standard
    Scenario: Select Standard Destination Account
        Given I am on the journal transfer page
        When I select destination account from the available list of accounts
        Then the destination account should be selectable
        And account selection should be highlighted
        And selection should trigger page update
        Then source account information should be displayed correctly
        And destination account details should be shown
        And "Investment Account Details" section should appear
        And CANCEL and NEXT buttons should be visible and clickable

    @journal_transfer @account_selection @other_account
    Scenario: Configure Other Account Details
        Given I am on the journal transfer page
        When I select "Other Account" from destination account options
        Then additional input fields should appear
        And the form should expand for manual entry
        When I fill in Other Account name field with "Test Account"
        Then the account name field should accept text input
        And entered text should persist without validation errors
        When I generate and enter account number "88888888"
        Then the account number field should accept numeric input
        And generated number should meet format requirements
        When I confirm account number by re-entering it
        Then numbers should match validation and pass
        When I check the Qualified account checkbox
        Then the checkbox should show checked state
        When I select account status radio button
        Then the account status should be selected with only one option chosen

    @journal_transfer @transaction_configuration @portion
    Scenario: Configure Journal Portion Transfer
        Given I have selected a destination account and proceeded
        When I click NEXT button to proceed to transaction details page
        Then the transaction details page should load
        And source and destination accounts should still be displayed
        And distribution options should be visible
        When I select "Journal Portion of Account" radio button
        Then portion distribution option should be selected
        And amount input field should become available
        And percentage calculation area should appear
        When I choose "$ Amount" for journal portion type
        Then dollar amount option should be selected
        And amount textbox should be available for input
        When I enter specific dollar amount "$45.00"
        Then the amount field should accept numeric input
        And value should be formatted correctly
        And approximate percentage calculation should appear
        And signature options should be available and clickable

    @journal_transfer @transaction_configuration @securities
    Scenario: Configure Journal Securities Transfer
        Given I have selected a destination account and proceeded to transaction details
        When I select "Journal Securities" radio button
        Then securities distribution option should be selected
        And securities selection interface should appear
        And All button options should become available
        When I click "All" buttons to select securities for the first 2 available
        Then securities should be selected when All buttons are clicked
        And selection count should update
        And selected securities should be highlighted
        And the interface should respond to user interactions

    @journal_transfer @esignature
    Scenario: Configure Electronic Signature Details
        Given I have configured transaction details with electronic signature option
        When I navigate to electronic signature configuration section
        Then e-signature section should be visible
        And email and phone fields should be available
        When I select authorized account from dropdown if combobox is present
        Then account options should be displayed and selectable
        When I enter email address "test@example.com" in the email field
        Then the email field should accept valid email format
        And entered email should persist without validation errors
        When I enter phone number "(555) 123-4567" in the phone field
        Then the phone field should accept numeric input
        And phone number should be formatted correctly
        When I check the confirmation checkbox for e-signature agreement
        Then the checkbox should show checked state
        And agreement terms should be acknowledged
        When I click NEXT button to proceed
        Then e-signature configuration should be saved
        And system should advance to next step without validation errors

    @journal_transfer @review_submission @standard
    Scenario: Review Request Summary and Submit Standard Flow
        Given I have completed transaction configuration
        When the Request Summary page loads
        Then "Request Summary" heading should be visible
        And request type should show as "Journal"
        And all account information should be displayed correctly
        And source and destination account details should be accurate in summary
        And transaction amount should be displayed in correct format
        And restricted cash information should be clearly presented
        When I identify the submission pathway as "SUBMIT"
        Then the correct submit button should be visible and enabled
        When I click SUBMIT button for direct processing
        Then the request should be submitted successfully
        And confirmation page should begin loading
        And any warnings should be handled appropriately

    @journal_transfer @review_submission @warnings
    Scenario: Submit Request with Warnings to Review
        Given I have a transaction that generates warnings
        When the Review Summary page loads with warnings present
        Then warning messages should be displayed clearly
        And "SUBMIT TO REVIEW" button should be visible
        When I click SUBMIT TO REVIEW button
        Then the submit to review button should respond
        And system should capture warning details
        And request should enter review workflow
        And warning messages should be recorded for audit trail

    @journal_transfer @docusign @esignature_flow
    Scenario: Complete DocuSign Electronic Signature Process
        Given I have submitted a request with electronic signature option
        When I am redirected to DocuSign after submission
        Then DocuSign URL should contain expected pattern
        And DocuSign interface should load with signature page displayed
        When I locate and check DocuSign confirmation checkbox
        Then confirmation checkbox should be visible and selectable
        And agreement terms should be displayed
        When I click Continue button to proceed with signing  
        Then continue button should advance process
        And signature interface should appear with document ready for signing
        When I click available Sign buttons to complete signatures
        Then sign buttons should be clickable
        And signature process should progress through multiple signatures
        When I click Finish button to complete DocuSign process
        Then finish button should complete signing
        And DocuSign process should conclude with system returning to application
        And "Ready for Signatures" confirmation text should appear
        And DocuSign integration should be confirmed with process completion acknowledged

    @journal_transfer @confirmation
    Scenario: Verify Request Confirmation Details  
        Given I have successfully submitted a journal transfer request
        When I wait for confirmation page to load after submission
        Then confirmation text "Request submitted successfully" should appear
        And status should show as "In Process - Pending Settlement"
        And item number should be generated and displayed
        When I extract item number using regex pattern matching
        Then item number should match pattern A followed by 9 digits
        And item number should be exactly 10 characters long
        And item number should be unique and trackable
        Then all confirmation page details should be verified
        And date/time stamp should follow MM/DD/YYYY, HH:MM:SS AM/PM PT format
        And CLOSE button should be available with printing instructions
        And item number should be clickable for tracking

    @journal_transfer @tracking @navigation
    Scenario: Navigate to and Use Tracking Center
        Given I have received a confirmation with item number
        When I click on item number to navigate to tracking center
        Then tracking center page should load
        And item should appear in tracking system
        And request details should be accessible
        When I handle document upload for print signature requests
        Then "Upload Documents" dialog should appear if needed
        And file selection should be available
        When I upload required PDF documents
        Then upload process should complete successfully
        And upload dialog should close after completion

    @journal_transfer @tracking @verification
    Scenario: Verify Complete Tracking Center Details
        Given I am in the tracking center with a submitted request
        When I wait for item to appear in tracking center with retry logic
        Then item number should appear within 40 seconds maximum
        And system should handle delays gracefully
        And item number should match extracted number and be displayed prominently
        Then request status should show "Request Received" or "In Process"
        And status should be updated and accurate with progress information
        And request type should show as "Journal Request" with correct classification
        Then source and destination account details should be displayed consistently
        And transfer amount should be displayed correctly with currency formatting
        And value should match original transaction
        And all tracking details should be recorded for audit trail
        And information should be available for reporting

    @journal_transfer @error_handling
    Scenario Outline: Handle Transfer Validation Errors  
        Given I navigate to the journal transfer page
        When I attempt to configure a transfer with "<error_scenario>"
        Then I should see appropriate "<validation_message>"
        And the system should prevent submission until corrected

        Examples:
            | error_scenario           | validation_message                      |
            | insufficient_funds       | Warning about exceeding available cash  |
            | invalid_account_number   | Account number format validation        |
            | missing_required_fields  | Required field validation messages      |
            | duplicate_account_selection | Cannot transfer to same account error |

    @journal_transfer @end_to_end @comprehensive
    Scenario: Complete Journal Transfer End-to-End Flow
        Given I start with login to eWealth Manager
        And I navigate to journal transfer functionality
        When I select accounts and configure transaction details  
        And I choose signature preferences and review request
        And I submit the request with appropriate handling
        Then I should receive confirmation with tracking capability
        And I should be able to track the request through completion
        And all audit trails should be maintained throughout the process