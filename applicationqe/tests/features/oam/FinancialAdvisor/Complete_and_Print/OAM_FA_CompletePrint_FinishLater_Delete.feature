Feature: OAM_Initiated by FA_Complete and Print_Finish Later with Delete

  @OAM_Smoke @FNT_regression @OAM_S14
  Scenario Outline: S14_OAM_Initiated by FA_Complete and Print_Finish Later with Delete
    When User navigate to Clients menu
    And User click on Account List
    And User is on the Account List tab and search for Account Number
    And User click on searched account and navigate to account wizard page
    Then Account Number is displayed and radio button is selected
    When User select OAM Request and Type
    Then Verify Form Heading must be same as selected OAM Type
    When User select Submission Type
    Then User should be redirected to the DocuSign page
    And Verify docusign Review and continue dialog text "Please review and sign the document electronically."
    When User confirm and Continue the docusign Review and continue dialog
    Then Verify As_authorized_by stamp presence
    When User Finish later the DocuSign process
    Then Finish Later pop up should be displayed
    When User delete the document
    And User navigate to Tracking Center
    And Search the DNumber
    Then Verify no search result message should be displayed
  
  Examples:
    | SheetName | RowNumber |
    | OAM       | 15        |


  