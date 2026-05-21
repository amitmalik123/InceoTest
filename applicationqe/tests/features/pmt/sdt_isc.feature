@Test_ISC
Feature: SDTISC Flow

  Scenario Outline: Successfully change investments on a client account

    Given User login into ewm application on test11 environment
    When User switches user ID with agent "<agent>" for account "<account>"
    And User enters agent ID from test data
    And User is on the account wizard tab and search the client
    And Click on client management option "Change Investments"
    And Click on account number and navigate to investment selection tab
    Then Validate Account Number On Destination Investment Tab
    When Select new investment on destination investment tab
    Then Validate New Investment Modal
    When User selects investment strategy "Single Strategy Account"
    And User selects investment profile "Core Markets"
    When User confirms investment selection
    And User selects allocation option "Full"
    And User selects risk tolerance "Moderate"
    And User selects time horizon "10 years"
    And User selects liquidity needs "10%"
    And User clicks next to review
    And User clicks next to complete
    And User clicks next to complete
    When User clicks on complete and print button
    Then User navigates to docu sign page and clicks on Continue and Finish button
    And User opens the tracking record
    And User upload the PDF file
    And User verify the tracking Id starts with B
    Given User launches SDT ISC process portal login page
    When User logs into SDT ISC process portal as "user1"
    And User searches for the stored B-number in the dashboard
    And User verifies exact B-number match and clicks Run button
    And User selects "In Process-Auto close Pending Settlement" from the status dropdown
    And User clicks on D number checkbox
    And User clicks on ICT Activation checkbox
    And User clicks on Activate ICT button
    And User clicks OK on Activation popup
    And User clicks Save & Exit button
    And User clicks OK on Activation popup
    #And User repeats Save and Exit cycle if B-number still visible
    When User logs into SDT ISC process portal as "user2"
    And User searches for the stored B-number in the dashboard
    And User verifies exact B-number match and clicks Run button
    And User clicks on Add/Update QC Reasons button
    And User selects "Not Processed" from dropdown
    And User selects "Additional Request Not Processed" from dropdown
    And User selects "BAW TestUser2" from dropdown
    And User clicks on Add button
    And User selects "Verified" from dropdown
    And User clicks on Save button
    Then QC Reason is added as "Verified" in QC Reasons section
    When User clicks on Return To Last User button in FollowUp and Ownership
    And User clicks Save & Exit button
    And User clicks OK on Activation popup
    When User logs into SDT ISC process portal as "user1"
    And User searches for the stored B-number in the dashboard
    And User verifies exact B-number match and clicks Run button
    And User selects "In Process-Auto close Pending Settlement" from the status dropdown
    And User clicks Save & Exit button
    And User clicks OK on Activation popup

    Examples:
      | agent  | account  |
      | AGAH4S | 40200164 |

