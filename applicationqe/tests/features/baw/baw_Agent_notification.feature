@AgentNotification @baw
Feature: Agent Notification Preference

  @AgentNotification @baw
  Scenario Outline: BAW_AgentNotification
    Given User should login to BAW application and click on the dashboard
    When User click on Open New Work Item button
    When Select work item type "Custodian Change Request"
    When Enter Custodial Account value
    And Select individual owner and click run now
    And Fetch b number from shell process page
    And Click on View Notification Preferences button and verify the notification preferences for the work item

    Examples:
      | SheetName | RowNumber |
      | BAW       | 2         |