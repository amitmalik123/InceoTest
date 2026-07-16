@squad5SmokeTest
Feature: BAW Transfer Records

  @toar @baw @prodSmoke
  Scenario Outline: TOAR_Record
    When User click on Open New Work Item button
    When Select work item type "Custodian Change Request"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    Then Click on update transfer button
    Then enter transfer details for work item "Custodian Change Request" with "Percent" allocation in destination
    And Validate notes history section "TOAR Record created successfully"

    Examples:
      | SheetName | RowNumber |
      | TOAR      | 2         |

  @toad @baw 
  Scenario Outline: TOAD_Record
    When User click on Open New Work Item button
    When Select work item type "<WorkItemType>"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    Then Click on update transfer button
    Then enter transfer details for work item "<WorkItemType>" with "Percent" allocation in destination
    And Validate notes history section "TOAD Record created successfully"

    Examples:
      | SheetName | RowNumber | WorkItemType                 |
      | TOAR      | 2         | Full Transfer Out In Kind    |
      | TOAR      | 2         | Partial Transfer Out In Kind |