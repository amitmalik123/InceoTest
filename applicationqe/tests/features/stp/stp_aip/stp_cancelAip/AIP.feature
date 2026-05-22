@e2e @critical
Feature: Feature: Cancel AIP - Regression
  As a financial advisor
  I want to cancel an Automatic Investment Plan (AIP) instruction
  So that I can manage my clients' investment preferences

@smoke
Scenario Outline: Cancel AIP_Online submit_Immediate
    Given User with role "cancel-swp-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account for Cancel AIP
    And Select "Contributions" request and "Cancel Automatic Investment Plan" type in Account Management
    And User clicks on next button and jumps to Cancel AIP Landing Page
    And User should add request header parameters For "CreatePeriodicAIP"
    And User should add request body parameters for createPerodicAIP
    And User should post the response for "CreatePeriodicAIP" endpoint
    Then User should verify status code 200    
    And User refreshes the page to view the API created 
    And User should validate AIP is displayed and click on AIP details on Landing Page
    And User selects the first AIP and clicks the Delete Button
    And User is able to Navigate to the Selection Layout Page
    And User is able to Validate End Date is displayed and selects the appropriate radio button for End Date selection
    And User should enter "notobtain" as Signature Options for account on the Selection Page
    And User should click on the Next Button on the Selection Page
    Then User should click on the Submit Button on Cancel AIP Summary Page
    And User should get Item Number from Confirmation Page for Cancel AIP
    And User should click on item number for Cancel AIP
    Then User should execute azure db query with item number and verify note "Step Delete AIP record Completed" for CancelAIP where stepID is "69"
    #Then User should execute azure db query with item number and verify note "Step UpdateTrackingCenterNotes completed successfully" for CancelAIP where stepID is "69"
    Examples: 
      | SheetName | RowNumber | Category |
      | CancelAIP |         2 | ADG      |


 @smoke
  Scenario Outline: CancelAIP OnlineSubmit with Future End Date
    Given User with role "cancel-swp-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And Select "Contributions" request and "Cancel Automatic Investment Plan" type in Account Management
    And User clicks on next button and jumps to Cancel AIP Landing Page
    And User should add request header parameters For "CreatePeriodicAIP"
    And User should add request body parameters for createPerodicAIP
    And User should post the response for "CreatePeriodicAIP" endpoint
    Then User should verify status code 200    
    And User refreshes the page to view the API created 
    And User should validate AIP is displayed and click on AIP details on Landing Page
    And User selects the first AIP and clicks the Delete Button
    And User is able to Navigate to the Selection Layout Page
    And User should be able to select Future End Date in calendar field
    And User should enter "notobtain" as Signature Options for account on the Selection Page
    And User should click on the Next Button on the Selection Page
    Then User should click on the Submit For Review Button on Cancel AIP Summary Page
    And User should get Item Number from Confirmation Page for Cancel AIP
    And User should click on item number for Cancel AIP
    Then User should validate info panel contents with status "Request Received" and item description as "Automatic Investment Plan Request - Cancel" for "Cancel AIP Online STR"

    #Then User execute db query to fetch external status from Tracking centre database as "Request Received" for Roth Conversions
    Examples: 
      | SheetName                     | RowNumber |
      | CancelAutomaticInvestmentPlan |         5 |

