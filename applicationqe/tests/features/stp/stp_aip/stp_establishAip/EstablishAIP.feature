@FullRegression
Feature: Establish AIP


  @smoke
  Scenario Outline: Establish AIP_Landing page Non-IRA Account
    Given User with role "non-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    When User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account for Establish AIP
    And Select "Contributions" request and "Establish Automatic Investment Plan" type in Account Management
    # AIP Landing Page
    And User clicks on next button and jumps to Establish AIP Landing Page
    And User verifies Account Information on Landing Page
    And User clicks on the Add button in the Establish AIP Landing Page
    # Origination Selection Page
    And User verifies Account Information on Origination Selection Page
    And User clicks on View Details and verifies Instruction Details modal closes with cross and Close button
    And User should see the required texts on Select Origination page and clicks on Next
    # Add AIP Page
    And the advisor enters a valid contribution amount
    And the advisor selects the frequency as "Monthly"
    And the advisor chooses the start and end dates from the calendar
    And User verifies Account Information on Add AIP Page
    And User selects the signature option "Do Not Obtain Client Signature(s) – Only Advisor Authorization Required" and clicks Next
    # Summary Page
    And User verifies all values on the Summary Page
    And User verifies the Acknowledgements and Agreements section
    And User clicks the Submit button
    # Confirmation Page
    And User verifies the success banner on Confirmation Page
    And User verifies the Request Summary section on Confirmation Page
    And User verifies the Request Details section on Confirmation Page
    And User verifies Account Information on Confirmation Page
    And User clicks the Close button

    # And User should validate the Bottom HyperLinks present which are "Privacy and Security Policy", "Terms of Use" and "Supported Browsers" for Establish AIP
    # And User should validate the Bottom HyperLinks are clickable and takes the user to respective pages for Establish AIP
    
    Examples: 
      | SheetName     | RowNumber | AccountType |
      | Establish AIP |         2 | Non-IRA     |


  @smoke
  Scenario Outline: Establish AIP_Landing page IRA Account
    Given User with role "ira-account" is loaded
    When I navigate to Clients menu
    And I click on Account List
    When User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account for Establish AIP
    And Select "Contributions" request and "Establish Automatic Investment Plan" type in Account Management
    # AIP Landing Page
    And User clicks on next button and jumps to Establish AIP Landing Page
    And User verifies Account Information on Landing Page
    And User clicks on the Add button in the Establish AIP Landing Page
    # Origination Selection Page
    And User verifies Account Information on Origination Selection Page
    And User clicks on View Details and verifies Instruction Details modal closes with cross and Close button
    And User should see the required texts on Select Origination page and clicks on Next
    # Add AIP Page
    And the advisor enters a valid contribution amount
    And the advisor selects the frequency as "Monthly"
    And the advisor chooses the start and end dates from the calendar
    And User verifies Account Information on Add AIP Page
    And User selects the signature option "Do Not Obtain Client Signature(s) – Only Advisor Authorization Required" and clicks Next
    # Summary Page
    And User verifies all values on the Summary Page
    And User verifies the Acknowledgements and Agreements section
    And User clicks the Submit button
    # Confirmation Page
    And User verifies the success banner on Confirmation Page
    And User verifies the Request Summary section on Confirmation Page
    And User verifies the Request Details section on Confirmation Page
    And User verifies Account Information on Confirmation Page
    And User clicks the Close button

    Examples: 
      | SheetName     | RowNumber | AccountType |
      | Establish AIP |         3 | IRA         |