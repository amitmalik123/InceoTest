"""
Constants for test automation framework
Contains disclosure texts, validation messages, and other constant values
"""
import os
from typing import List


class BeneAccountUrls:
   

    class DEV:
        BASE         = "https://app.dev01.assetmark.com/bene?householdid=C19744"
        DECEASED     = "https://app.dev01.assetmark.com/bene?householdId=C99796"
        ENTITY       = "https://app.dev01.assetmark.com/bene?householdid=RTTEST"
        FRAUD_FROZEN = "https://app.dev01.assetmark.com/bene?householdId=CE64Y9"
        POA          = "https://app.dev01.assetmark.com/bene?householdId=C19744"

    class TEST11:
        BASE         = "https://app.test01.assetmark.com/clients/AG8959/CE6MD5/W1706A/manage-beneficiaries"
        DECEASED     = ""  # TODO: set test11 URL for Deceased scenario
        ENTITY       = ""  # TODO: set test11 URL for Entity scenario
        FRAUD_FROZEN = ""  # TODO: set test11 URL for Fraud/Frozen scenario
        POA          = ""  # TODO: set test11 URL for POA scenario

    @classmethod
    def for_env(cls, env: str = None):
        """Return the URL group for the given environment (defaults to TEST_ENV)."""
        env = env or os.getenv("TEST_ENV", "dev")
        if env == "test11":
            return cls.TEST11
        return cls.DEV


class Constants:
    """Constants class containing all static test data and validation texts"""
    
    # Disclosure titles and headers
    DISCLOSURES_TITLE = "Acknowledgements and Agreements"
    DISCLAIMER_TEXT = "Upon completion of this request, I certify that:"

    # E-signature constants
    Esign_WarningText = "You will be redirected to Docusign for completing the e-Signing process."
    
    # Disclosure Methods
    @staticmethod
    def get_withdrawal_disclosures(disclosure_type: str) -> List[str]:
        """Get withdrawal disclosures based on delivery method"""
        withdrawalDisclosures = [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the Rules and Conditions applicable to this withdrawal included in the IRA custodial agreement.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian for my IRA shall in no way be held responsible.",
            "Final distribution amounts may change due to specific state withholding requirements and withholding amounts rounding to the nearest whole dollar."
        ]
        
        if "Check" in disclosure_type:
            withdrawalDisclosures.append("If selected, an $18 overnight fee will be charged to the account if the distribution is less than $100,000.")
        
        return withdrawalDisclosures
    
    @staticmethod
    def get_withdrawal_disclosures_dm2(disclosure_type: str) -> List[str]:
        """Get withdrawal disclosures DM2 based on delivery method"""
        withdrawalDisclosures = [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the Rules and Conditions applicable to this withdrawal included in the IRA custodial agreement.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian for my IRA shall in no way be held responsible.",
            "Final distribution amounts may change due to specific state withholding requirements and withholding amounts rounding to the nearest whole dollar.",
            "This request will be submitted for processing once all parties have electronically signed the request."
        ]
        
        if "Check" in disclosure_type:
            withdrawalDisclosures.append("If selected, an $18 overnight fee will be charged to the account if the distribution is less than $100,000.")
        
        return withdrawalDisclosures
    
    @staticmethod
    def get_contribution_disclosures() -> List[str]:
        """Get contribution disclosures"""
        return [
            "Assetmark Trust Company may request a contribution from the bank account provided.",
            "I am authorized on behalf of my client to initiate this transaction.",
            "All information I have provided to complete this request is true and accurate.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that:",
            "1) The instructions indicated in this request are at the request of the account owner(s).",
            "2) The requested funds are currently available and accessible in the bank account provided.",
            "3) Any potential consequences that may arise from funds not being sufficient at the time the contribution posts will be at the responsibility of the Client.",
            "I assume responsibility for any adverse consequences which may arise from this contribution and agree that AssetMark Trust Company as Custodian shall in no way be held responsible."
        ]
    
    @staticmethod
    def get_withdrawal_disclosures_no_restricted() -> List[str]:
        """Get withdrawal disclosures without restricted cash"""
        return [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian shall in no way be held responsible.",
            "If taking a withdrawal from a UTMA/UGMA account, the client has confirmed the funds will only be used for the benefit of the minor."
        ]
    
    @staticmethod
    def get_withdrawal_disclosures_no_restricted_dm2() -> List[str]:
        """Get withdrawal disclosures DM2 without restricted cash"""
        return [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian shall in no way be held responsible.",
            "If taking a withdrawal from a UTMA/UGMA account, the client has confirmed the funds will only be used for the benefit of the minor.",
            "This request will be submitted for processing once all parties have electronically signed the request."
        ]
    
    @staticmethod
    def get_cancel_disclosures() -> List[str]:
        """Get cancel disclosures"""
        return [
            "AssetMark Trust Company will cancel the client's recurring disbursement immediately. If the disbursement is scheduled to go out today or the following business day, the cancellation will take effect on the next distribution.",
            "If cash has already been raised to satisfy the next distribution, the cash will invest back into the account.",
            "I acknowledge responsibility for any adverse consequences which may arise from this cancellation and agree that AssetMark Trust Company as custodian shall not be held responsible.",
            "I am authorized on behalf of my client to request this cancellation.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that this request is valid. I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the custodial agreement Rules and Conditions applicable to this systematic withdrawal."
        ]
    
    @staticmethod
    def get_add_ach_disclosures() -> List[str]:
        """Get Add ACH disclosures"""
        return [
            "All information provided for this request is true, accurate, complete and authorized, and I, or the representative of our firm, have confirmed, either by phone or in person, this with the account owner(s). I acknowledge that failure to properly verify the information and instructions may result in financial liability to me and/or my firm.",
            "I acknowledge that the requested changes will not be effective until accepted by AssetMark, and that a reasonable amount of time must be allowed for the requested change.",
            "I agree that AssetMark, Inc., its affiliates, and their directors, employees and agents, and their successors shall be held harmless from any and all claims, judgments, settlements and other liabilities and damages (including attorneys' fees) arising out of or relating to their reliance on this request."
        ]
    
    @staticmethod
    def get_roth_conversion_summary_disclosure() -> List[str]:
        """Get Roth Conversion Summary disclosure"""
        return [
            "I am authorized on behalf of my client to submit this request.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the custodial agreement Terms and Conditions applicable to this request.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that this request is valid. I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "I acknowledge responsibility for any adverse consequences which may arise from this request and agree that AssetMark Trust Company as custodian shall not be held responsible."
        ]

    @staticmethod
    def get_establish_aip_disclosures() -> List[str]:
        """Get Establish AIP Acknowledgements and Agreements disclosures (Non-IRA)"""
        return [
            "All information provided for this request is true, accurate, complete and authorized, and I, or the representative of our firm, have confirmed, either by phone or in person, this with the account owner(s). I acknowledge that failure to properly verify the information and instructions may result in financial liability to me and/or my firm.",
            "I acknowledge that the requested changes will not be effective until accepted by AssetMark, and that a reasonable amount of time must be allowed for the requested change.",
            "I agree that AssetMark, Inc., its affiliates, and their directors, employees and agents, and their successors shall be held harmless from any and all claims, judgments, settlements and other liabilities and damages (including attorneys' fees) arising out of or relating to their reliance on this request.",
            "If the automatic investment plan (AIP) is being established one business day before the next scheduled AIP date, the plan may not be able to be established before funds post. If funds do not post, the plan will begin on the next scheduled occurrence."
        ]

    @staticmethod
    def get_establish_aip_disclosures_ira() -> List[str]:
        """Get Establish AIP Acknowledgements and Agreements disclosures (IRA)"""
        return [
            "All information provided for this request is true, accurate, complete and authorized, and I, or the representative of our firm, have confirmed, either by phone or in person, this with the account owner(s). I acknowledge that failure to properly verify the information and instructions may result in financial liability to me and/or my firm.",
            "I acknowledge that the requested changes will not be effective until accepted by AssetMark, and that a reasonable amount of time must be allowed for the requested change.",
            "I agree that AssetMark, Inc., its affiliates, and their directors, employees and agents, and their successors shall be held harmless from any and all claims, judgments, settlements and other liabilities and damages (including attorneys' fees) arising out of or relating to their reliance on this request.",
            "If the automatic investment plan (AIP) is being established one business day before the next scheduled AIP date, the plan may not be able to be established before funds post. If funds do not post, the plan will begin on the next scheduled occurrence.",
            "I have confirmed the direct relationship and/or association of that bank account owner to the AssetMark account owner and attest the funds being contributed are from a legal and legitimate source."
        ]

    @staticmethod
    def get_establish_aip_disclosures_ira_prod() -> List[str]:
        """Get Establish AIP Acknowledgements and Agreements disclosures (IRA) for PROD environment"""
        return [
            "All information provided for this request is true, accurate, complete and authorized, and I, or the representative of our firm, have confirmed, either by phone or in person, this with the account owner(s). I acknowledge that failure to properly verify the information and instructions may result in financial liability to me and/or my firm.",
            "I acknowledge that the requested changes will not be effective until accepted by AssetMark, and that a reasonable amount of time must be allowed for the requested change.",
            "I agree that AssetMark, Inc., its affiliates, and their directors, employees and agents, and their successors shall be held harmless from any and all claims, judgments, settlements and other liabilities and damages (including attorneys' fees) arising out of or relating to their reliance on this request.",
            "If the automatic investment plan (AIP) is being established one business day before the next scheduled AIP date, the plan may not be able to be established before funds post. If funds do not post, the plan will begin on the next scheduled occurrence."
        ]

    # Instance Audit Notes Constants
    @staticmethod
    def notes_sloa_esign_admin() -> List[str]:
        """Notes for SLOA Esign Admin role"""
        return [
            "New request submitted by Advisor through the DM Tool",
            "Step PopulatePDFSessionObject completed successfully",
            "Step UpdateWorkItemStatus and advisorAlert.",
            "Step GenerateEnvelope completed successfully",
            "Step CreateDItem completed successfully",
            "Step GetEsignTokenURL completed successfully"
        ]
    
    @staticmethod
    def notes_sloa_esign_advisor_via_admin() -> List[str]:
        """Notes for SLOA Esign Advisor via Admin role"""
        return [
            "New request submitted by Advisor through the DM Tool",
            "Step PopulatePDFSessionObject completed successfully",
            "Step UpdateWorkItemStatus and advisorAlert.",
            "Step GenerateEnvelope completed successfully",
            "Step CreateDItem completed successfully",
            "Step GetEsignTokenURL completed successfully",
            "Request details passed by Process Initiator",
            "Step GetWorkItemDetails completed",
            "Step GetWorkItemDetails completed",
            "Step UpdateWorkItem completed",
            "Converted D# to A# Successfully",
            "Step UpdateDocument completed",
            "Step CreateAINSRecord completed successfully",
            "Step Get Notification Recipients completed",
            "Step Send Email Notification completed",
            "Step UpdateTrackingCenterItemNote completed"
        ]
    
    @staticmethod
    def notes_sloa_esign() -> List[str]:
        """Notes for SLOA Esign"""
        return [
            "New request submitted by Advisor through the DM Tool",
            "Step PopulatePDFSessionObject completed successfully",
            "Step GenerateEnvelope completed successfully",
            "Step CreateDItem completed successfully",
            "Step GetEsignTokenURL completed successfully",
            "Request details passed by Process Initiator",
            "Step GetWorkItemDetails completed",
            "Step UpdateWorkItem completed",
            "Step UpdateDocument completed",
            "Converted D# to A# Successfully",
            "Step CreateAINSRecord completed successfully",
            "Step Get Notification Recipients completed",
            "Step Send Email Notification completed",
            "Step UpdateTrackingCenterItemNote completed"
        ]
    
    @staticmethod
    def notes_sloa_print() -> List[str]:
        """Notes for SLOA Print"""
        return [
            "New request submitted by Advisor through the DM Tool",
            "Step PopulatePDFSessionObject completed successfully",
            "Step UpdateWorkItemStatus and advisorAlert.",
            "Step GenerateEnvelope completed successfully",
            "Step CreateDItem completed successfully",
            "Step GetEsignTokenURL completed successfully"
        ]
    
    @staticmethod
    def notes_sloa_no_esign_admin() -> List[str]:
        """Notes for SLOA NoEsign Admin role"""
        return [
            "Step CreateAItem completed successfully",
            "Step CreatePDF completed successfully",
            "Step UploadPDFToFileBoundServer completed successfully",
            "Step Stage DM Request completed successfully",
            "Update Tracking Center Success",
            "Step Staged Request Summary URL completed successfully",
            "Send Email Notification to Advisor Success"
        ]
    
    @staticmethod
    def notes_sloa_no_esign_advisor_via_admin() -> List[str]:
        """Notes for SLOA NoEsign Advisor via Admin role"""
        return [
            "Step CreateAItem completed successfully",
            "Step CreatePDF completed successfully",
            "Step UploadPDFToFileBoundServer completed successfully",
            "Step Stage DM Request completed successfully",
            "Update Tracking Center Success",
            "Step Staged Request Summary URL completed successfully",
            "Send Email Notification to Advisor Success",
            "Step CreateAINSRecord completed successfully",
            "Step Get Notification Recipients completed",
            "Step Send Email Notification completed",
            "Step UpdateTrackingCenterItemNote completed"
        ]
    
    @staticmethod
    def notes_sloa_no_esign() -> List[str]:
        """Notes for SLOA NoEsign"""
        return [
            "Step CreateAItem completed successfully",
            "Step CreatePDF completed successfully",
            "Step UploadPDFToFileBoundServer completed successfully",
            "Step Stage DM Request completed successfully",
            "Update Tracking Center Success",
            "Step Staged Request Summary URL completed successfully",
            "Send Email Notification to Advisor Success",
            "Step CreateAINSRecord completed successfully",
            "Step Get Notification Recipients completed",
            "Step Send Email Notification completed",
            "Step UpdateTrackingCenterItemNote completed"
        ]    
    @staticmethod
    def get_withdrawal_disclosures(disclosure_type: str) -> List[str]:
        """
        Get withdrawal disclosures for ACH or Check
        
        Args:
            disclosure_type: Either "ACH" or "Check"
            
        Returns:
            List of disclosure strings
        """
        withdrawal_disclosures = [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the Rules and Conditions applicable to this withdrawal included in the IRA custodial agreement.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian for my IRA shall in no way be held responsible.",
            "Final distribution amounts may change due to specific state withholding requirements and withholding amounts rounding to the nearest whole dollar."
        ]
        
        if "Check" in disclosure_type:
            withdrawal_disclosures.append(
                "If selected, an $18 overnight fee will be charged to the account if the distribution is less than $100,000."
            )
        
        return withdrawal_disclosures
    
    @staticmethod
    def get_withdrawal_disclosures_dm2(disclosure_type: str) -> List[str]:
        """
        Get withdrawal disclosures for DM2 (ACH or Check)
        
        Args:
            disclosure_type: Either "ACH" or "Check"
            
        Returns:
            List of disclosure strings
        """
        withdrawal_disclosures = [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the Rules and Conditions applicable to this withdrawal included in the IRA custodial agreement.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian for my IRA shall in no way be held responsible.",
            "Final distribution amounts may change due to specific state withholding requirements and withholding amounts rounding to the nearest whole dollar.",
            "This request will be submitted for processing once all parties have electronically signed the request."
        ]
        
        if "Check" in disclosure_type:
            withdrawal_disclosures.append(
                "If selected, an $18 overnight fee will be charged to the account if the distribution is less than $100,000."
            )
        
        return withdrawal_disclosures
    
    @staticmethod
    def get_withdrawal_disclosures_no_restricted() -> List[str]:
        """
        Get withdrawal disclosures for non-restricted accounts
        
        Returns:
            List of disclosure strings
        """
        return [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian shall in no way be held responsible.",
            "If taking a withdrawal from a UTMA/UGMA account, the client has confirmed the funds will only be used for the benefit of the minor."
        ]
    
    @staticmethod
    def get_withdrawal_disclosures_no_restricted_dm2() -> List[str]:
        """
        Get withdrawal disclosures for non-restricted accounts in DM2
        
        Returns:
            List of disclosure strings
        """
        return [
            "AssetMark Trust Company may initiate the debit to my client's account.",
            "I am authorized on behalf of my client to initiate this distribution.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that the instructions indicated in this request are at the request of the account owner(s). I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I assume responsibility for any adverse consequences which may arise from these withdrawals and agree that Assetmark Trust Company as Custodian shall in no way be held responsible.",
            "If taking a withdrawal from a UTMA/UGMA account, the client has confirmed the funds will only be used for the benefit of the minor.",
            "This request will be submitted for processing once all parties have electronically signed the request."
        ]
    
    @staticmethod
    def get_contribution_disclosures() -> List[str]:
        """
        Get contribution disclosures
        
        Returns:
            List of disclosure strings
        """
        # Placeholder - implement based on actual requirements
        return []
    
    @staticmethod
    def get_cancel_disclosures() -> List[str]:
        """
        Get cancellation disclosures for SWP
        
        Returns:
            List of disclosure strings
        """
        return [
            "AssetMark Trust Company will cancel the client's recurring disbursement immediately. If the disbursement is scheduled to go out today or the following business day, the cancellation will take effect on the next distribution.",
            "If cash has already been raised to satisfy the next distribution, the cash will invest back into the account.",
            "I acknowledge responsibility for any adverse consequences which may arise from this cancellation and agree that AssetMark Trust Company as custodian shall not be held responsible.",
            "I am authorized on behalf of my client to request this cancellation.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that this request is valid. I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the custodial agreement Rules and Conditions applicable to this systematic withdrawal."
        ]
    
    @staticmethod
    def get_add_ach_disclosures() -> List[str]:
        return [
            "All information provided for this request is true, accurate, complete and authorized, and I, or the representative of our firm, have confirmed, either by phone or in person, this with the account owner(s). I acknowledge that failure to properly verify the information and instructions may result in financial liability to me and/or my firm.",
            "I acknowledge that the requested changes will not be effective until accepted by AssetMark, and that a reasonable amount of time must be allowed for the requested change.",
            "I agree that AssetMark, Inc., its affiliates, and their directors, employees and agents, and their successors shall be held harmless from any and all claims, judgments, settlements and other liabilities and damages (including attorneys' fees) arising out of or relating to their reliance on this request."
        ]

    @staticmethod
    def get_roth_conversion_summary_disclosure() -> List[str]:
        """
        Get Roth Conversion and IRA Journals summary disclosures
        
        Returns:
            List of disclosure strings
        """
        return [
            "I am authorized on behalf of my client to submit this request.",
            "All information I have provided to complete this request is true and accurate.",
            "I have read and understand the custodial agreement Terms and Conditions applicable to this request.",
            "I have verbally confirmed by phone or in person with the authorized account owner(s) that this request is valid. I recognize that there may be financial liability to myself or my firm if I do not properly confirm the identity of the account owner.",
            "I acknowledge responsibility for any adverse consequences which may arise from this request and agree that AssetMark Trust Company as custodian shall not be held responsible."
        ]
