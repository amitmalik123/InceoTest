Feature: Check Association To Transfer

  @baw @CheckAssociationToTransfer @prodSmoke
  Scenario Outline: Check work item association in Transfer In
    When User click on Open New Work Item button
    When Select work item type "Digital Check"
    When Enter Custodial Account value
    And Select account row from search results
    And Select individual owner and click run now
    And Fetch b number from shell process page
    When User clicks on Create New Digital Record and Add Update Check details
    Then User updates check details and clicks save and close
    Then User selects shell B number and clicks Save and Exit
    When User click on Open New Work Item button
    When Select work item type "Custodian Change Request"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    Then Click on update transfer button
    Then enter transfer details for work item "Custodian Change Request" with "Percent" allocation in destination without creating TOAR record
    Then Associate Check work item with transfer
    Then Verify the added note for Associate Check
    Then Verify the added note in check work item for Associate Check

    Examples:
      | SheetName    | RowNumber |
      | TOAR         | 2         |

  @CloseWorkItem 
  Scenario Outline: Closing work item after completed the testing
  Given User should login to BAW application and click on the dashboard
  When Closing work item after testing for "B100161459"

  Examples:
      | SheetName    | RowNumber |
      | TOAR         | 2         |