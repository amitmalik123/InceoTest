
Feature: OA Trading Tool

 @smoke
  Scenario Outline: OA Tool Landing Page
    Given User with role "oa-ira" is loaded
    When I navigate to Clients menu
    And I click on Account List
    And User is on the accountlist tab and search with the accountNo
    And User should click on searched account and navigate to account wizard page
    And User should pick account information from the selected account
    And User should execute db query to get OA Status of Account and Update to close them all for "Source"
    And User should execute db query to get HouseholdID
    And User should execute db query to get Client and Agent name
    And User should execute db query to get account ID
    Then User should navigate to OA Tool Landing page
    Then User should get bearer token from devTool
    And User should add request header parameters For "TradeInfoSearch"
    And User should add request body parameters for TradeInfoSearch API
    And User should post the response for "TradeInfoSearch" endpoint
    Then User should verify status code 200
    Then User should extract details from TradeInfoSearch API and store it in generic variables
    And User should validate the Advisor Id on the Page
    And User should validate request type section
    Then User should click request type for OTW
    And User should verify the "Account Information" Heading and the sub-heading as the Account name
    And User should validate the Bottom HyperLinks present which are "Privacy and Security", "Terms and Conditions" and "Supported Browsers"
    And User should validate the AssetMark image and the description as "AssetMark, Inc. All rights reserved."
    Then User should click next button on OA tool Landing page
    

    Examples: 
      | SheetName          | RowNumber | Type | Description                                                                            | AccountType | Option                              | AccountSelection | SLOAOption              | SLOASubOption | POA |
      #| OATradeActionsTool |        2 | ACH  | Select an instruction from the list below to view its details or add new instructions. | Checking    | ACH (Contributions and Withdrawals) | oneAccount       | Withdrawals Only - SLOA | Esign         | No  |
      #| OATradeActionsTool |         3 | ACH  | Select an instruction from the list below to view its details or add new instructions. | Checking    | ACH (Contributions and Withdrawals) | oneAccount       | Withdrawals Only - SLOA | Esign         | No  |
      | OATradeActionsTool |         4 | ACH  | Select an instruction from the list below to view its details or add new instructions. | Checking    | ACH (Contributions and Withdrawals) | oneAccount       | Withdrawals Only - SLOA | Esign         | No  |
      #| OATradeActionsTool |         5 | ACH  | Select an instruction from the list below to view its details or add new instructions. | Checking    | ACH (Contributions and Withdrawals) | oneAccount       | Withdrawals Only - SLOA | Esign         | No  |
      #| OATradeActionsTool |         6 | ACH  | Select an instruction from the list below to view its details or add new instructions. | Checking    | ACH (Contributions and Withdrawals) | oneAccount       | Withdrawals Only - SLOA | Esign         | No  |
