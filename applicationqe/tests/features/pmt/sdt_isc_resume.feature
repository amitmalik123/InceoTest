@Test_ISC_Resume
Feature: SDTISC Resume - BAW Portal Only

  Resumes the SDT ISC flow from the BAW Process Portal step using a known
  B-number (DEFAULT_B_NUMBER in tests/steps/pmt/sdt_isc_steps.py). Skips the
  EWM / Change Investments / DocuSign / PDF upload / B-number generation
  half of the full sdt_isc.feature so the BAW Coach (D-number, ICT
  Activation, QC Reasons) steps can be iterated on faster.

  Scenario: Resume SDT ISC BAW portal flow with stored B-number
    Given User launches SDT ISC process portal login page
    When User logs into SDT ISC process portal as "user1"
    And User searches for the stored B-number in the dashboard
    And User verifies exact B-number match and clicks Run button
    And User clicks on D number checkbox
    And User clicks on ICT Activation checkbox
    And User clicks on Activate ICT button
    And User clicks OK on Activation popup
    #And User clicks Save & Exit button
    And User selects "In Process-Auto close Pending Settlement" from the status dropdown
    And User clicks Save & Exit button
    And User clicks OK on Activation popup
    Given User launches SDT ISC process portal login page
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
