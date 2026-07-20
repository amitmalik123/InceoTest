from ast import Assert
import logging
import random
import re
import time
from typing import List, Optional
from datetime import datetime, timedelta
from allure_pytest import helper
from utils.helpers import random_number as generate_random_number, random_alpha
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.ewm.construct_portfolio_page import ConstructPortfolioPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class AccountSetupPage(BasePage):
    """Account Setup Page Object for managing account holder information and custodian-specific flows"""

    PAGE_NAME = "ACCOUNT SETUP PAGE"

    def __init__(self, page: Page, page_verification: bool = True, home_url: str = ""):
        """Initialize Account Setup Page with optional verification"""
        super().__init__(page)
        self.form_root = self.active_root()
        
        # Initialize all locators as instance attributes
        # Page elements
        self.page_label: Locator = self.form_root.locator(".label-page")
        self.add_trustee_button: Locator = self.form_root.locator("[data-toggle*='Hold_PeoplePicker_Multi_COUNT']")
        self.add_holder_button: Locator = self.form_root.locator("[data-toggle*='Hold_PeoplePicker']:not([data-toggle*='Multi'])")
        self.add_holder_button_fallback: Locator = self.form_root.locator("[data-toggle*='Hold_PeoplePicker']")
        self.add_new_link: Locator = self.form_root.locator("text=/^Add New$/")
        self.save_account_button: Locator = self.form_root.locator("button.people-picker-save-button:visible")
        
        # Account details input fields
        self.name_input: Locator = self.form_root.locator("input[name='Hold_Name_FIRSTNAME_0']")
        self.last_name_input: Locator = self.form_root.locator("input[name='Hold_Name_LASTNAME_0']")
        self.birth_date_input: Locator = self.form_root.locator("input[name='Hold_DOB_0']")
        self.ssn_input: Locator = self.form_root.locator("input[name*='Hold_SSN_0']:not([type='hidden'])")
        self.phone_input: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Phone_0")
        self.email_input: Locator = self.form_root.locator("input[id*='Hold_Email_0']")
        self.email_error: Locator = self.form_root.locator(
            "input[id*='Hold_Email_0'] ~ .field-validation-error, "
            "div[id*='Hold_Email_0'] .error-text, "
            ".validation-summary-errors:near(input[id*='Hold_Email_0'])"
        )
        self.ssn_tax_reporting: Locator = self.form_root.locator("#line_Questions_0__Info_TaxNum")
        self.address_2yrs_checkbox: Locator = self.form_root.locator("#question_line_Questions_0__Hold_PrevAddr_sect_No_0_tab")
        self.employment_status_dropdown: Locator = self.form_root.locator("#Hold_Employ_Status_0_id > .firstmenu > a")
        self.employment_status_container: Locator = self.form_root.locator("#Hold_Employ_Status_0_id")
        self.employment_list: Locator = self.form_root.locator("//*[@id='Hold_Employ_Status_0_id']/dd/dl/dd/a")
        self.employer_name_input: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Employ_Name_0")
        self.employer_business_type_input: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Employ_BusType_0")
        self.employer_years_input: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Employ_Years_0")
        self.employer_occupation_input: Locator = self.form_root.locator("#question_line_Questions_2__Hold_Employ_Occ_0")
        self.employer_iir_dropdown: Locator = self.form_root.locator("#Hold_Employ_IIR_0_id > .firstmenu > a")
        self.employer_iir_options: Locator = self.form_root.locator("#Hold_Employ_IIR_0_id >> dd >> dl >> dd >> a")
        self.employer_address_add_link: Locator = self.form_root.locator("#Hold_Employ_Address_0 a:has-text('Add Address')")
        
        # Address modal fields
        self.add_address_button: Locator = self.form_root.locator("a.address-select[data-questionid='Hold_HomeAddr_0']")
        self.address_line_input: Locator = self.form_root.locator(
            "div.modal:visible input[name='Hold_HomeAddr_ADDRESS1_0_Modal']"
        )
        self.city_input: Locator = self.form_root.locator(
            "div.modal:visible input[name='Hold_HomeAddr_CITY_0_Modal']"
        )
        self.state_dropdown: Locator = self.form_root.locator("#Hold_HomeAddr_STATE_0_Modal_id")
        self.zip_input: Locator = self.form_root.locator(
            "div.modal:visible input[name='Hold_HomeAddr_ZIP_0_Modal']"
        )
        self.state_options: Locator = self.form_root.locator(".show-dropdown.styled-ddl > dd > a")
        self.save_address_button: Locator = self.form_root.locator("div.modal:visible button[data-save-address-url='/AccountSetup/Interview/AddAddressToDomain']")
        self.verify_address_modal_save: Locator = self.form_root.locator("div.modal:visible button:has-text('Save')")
        
        # Navigation buttons - btn-next buttons are the form action buttons
        self.go_to_account_features_button: Locator = self.form_root.locator("button.btn-next[data-url*='Feat_Page']")
        self.account_information_button: Locator = self.form_root.locator("a[href*='Info_Page'], button:has-text('Account Information'), a:has-text('Account Information')").first
        self.account_features_button: Locator = self.form_root.locator("button.btn-next[data-url*='Feat_Page']")
        self.go_to_funding_method_button: Locator = self.form_root.locator("button.btn-next[data-url*='Fund_Page']")
        self.check_funding: Locator = self.form_root.locator("#question_Fund_Check_tab")
        self.enclosed_check_tab: Locator = self.form_root.locator("#Fund_Check_Amount")
        self.online_access_document_delivery_button: Locator = self.form_root.locator("//span[contains(text(),'Online Access & Document Delivery')]")
        self.review_all_accounts_button: Locator = self.form_root.locator("button.btn-next[data-url*='ReviewAllAccounts']")
        
        # Account list selection (when Account Information page shows a list of accounts)
        self.account_list_rows: Locator = self.form_root.locator("//tr[contains(@class, 'account')] | //div[contains(@class, 'account-row')] | //li[contains(@class, 'account')]")
        
        # Custodian/Registration type specific locators
        self.is_associated_with_exchange: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Affiliations_RBD_N_0_tab")
        self.is_director_or_shareholder: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Affiliation_Dir_N_0_tab")
        self.trustee_grantor_checkbox: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Trustor_N_0_tab")
        self.trust_revocable_checkbox: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Revoc_Authorization_No_0_tab")
        self.trust_revocable_radio: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_Type_Rev_tab")
        self.can_provide_netx_investor_access: Locator = self.form_root.locator("#line_Questions_0__Info_NetXInvestor_N_tab")
        self.trusted_contact: Locator = self.form_root.locator("#line_Questions_1__Info_PAS_TrustedContact_N_tab")
        self.can_share_prs_address: Locator = self.form_root.locator("#line_Questions_3__Info_PAS_InformationSharing_N_tab")
        self.individual_control_person: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Control_Person_No_0_tab")
        self.individual_entity_owner: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Entity_Owner_No_0_tab")
        self.mother_maiden_name: Locator = self.form_root.locator("#question_line_Questions_0__Hold_MoMaNa_0")
        self.income_source_input: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Employ_Inc_Source_0")
        self.custodial_interview_name: Locator = self.form_root.locator("//*[@id='account_setup_main']/div/label")
        self.donor_page_text: Locator = self.form_root.locator("//div[@id='Hold_PageIndiv_Label' or @id='Hold_PageMulti_Label']//label")
        self.is_donor_info_required: Locator = self.form_root.locator("//*[@id='IA_Name_Msg_0']|//*[@id='Hold_Donor_Msg_0']")
        self.add_new_beneficiary: Locator = self.form_root.locator("span:has-text('Add Beneficiary')")
        self.primary_beneficiaries_button: Locator = self.form_root.locator("button:has-text('Primary Beneficiaries')")
        self.contingent_beneficiaries_button: Locator = self.form_root.locator("button:has-text('Contingent Beneficiaries')")
        self.tax_management_service_button: Locator = self.form_root.locator("//span[normalize-space(text())='Tax Management Services']/ancestor::button")
        
        # LLC Information locators - use form_root for iframe/page dual-flow
        self.llc_info_button: Locator = self.form_root.locator("//span[contains(text(), 'LLC Information')]/ancestor::button")
        self.trust_info_button: Locator = self.form_root.locator("//span[contains(text(), 'Trust Information')]/ancestor::button")
        self.trustors_button: Locator = self.form_root.locator("//span[contains(text(), 'Trustors')]/ancestor::button")
        self.tin_number_input: Locator = self.form_root.locator("#line_Questions_0__Info_Tin")
        # LLC Type checkbox - direct ID selector from Java Selenium: By.xpath("//*[@id='line_Questions_0__Info_LLC_Ccorp_tab']")
        self.llc_type_checkbox: Locator = self.form_root.locator("#line_Questions_0__Info_LLC_Ccorp_tab")
        self.beneficial_ownership_checkbox: Locator = self.form_root.locator("#line_Questions_0__Info_CP_EntityOwner_ControlPerson_Additional_Yes_tab")
        self.individual_control_person_llc: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__Info_CP_EntityOwner_ControlPerson_Yes_0_tab")
        self.entity_owner_llc: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__Info_CP_EntityOwner_EntityOwner_Yes_0_tab")
        self.beneficial_first_name: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__firstName_Info_CP_Hold_Name_FIRSTNAME_0")
        self.beneficial_last_name: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__lastName_Info_CP_Hold_Name_LASTNAME_0")
        self.beneficial_dob: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__Info_CP_Hold_DOB_0")
        self.beneficial_ssn: Locator = self.form_root.locator("#line_Questions_0__line_Questions_1__Info_CP_Hold_SSN_0")
        self.beneficial_address_line1: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__Info_CP_Hold_Addr_A_ADDRESS1_0")
        self.beneficial_city: Locator = self.form_root.locator("#line_Questions_0__line_Questions_0__Info_CP_Hold_Addr_A_CITY_0")
        self.beneficial_state_dropdown: Locator = self.form_root.locator("[id*='Info_CP_Hold_Addr_A_STATE_0_tab']")
        self.beneficial_zip: Locator = self.form_root.locator("#line_Questions_0__line_Questions_2__Info_CP_Hold_Addr_A_ZIP_0")
        
        # Grantor/Trustee specific locators - use form_root for dual-flow
        self.grantor_button: Locator = self.form_root.locator("//span[contains(text(), 'Grantor or Additional Party')]/ancestor::button")
        
        # Existing account selection locators
        self.existing_account_option: Locator = self.form_root.locator("//div[@class='popover-content custom-popover-content']/div[1] | (//div[contains(@class,'picker-name')])[1]")
        self.individual_relation_dropdown: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Trustor_Relat_DecGrant_tab")
        self.country_dropdown: Locator = self.form_root.locator("#Hold_Trustor_Country_Dom_0_id >> dt >> a >> span:nth-of-type(2)")
        self.country_list: Locator = self.form_root.locator("#Hold_Trustor_Country_Dom_0_id >> dd >> dl >> dd >> a")
        
        # Trust Information specific locators (from Java reference)
        self.type_of_trust_dropdown: Locator = self.form_root.locator("#Info_Trust_Type_id")
        self.list_of_trust_types: Locator = self.form_root.locator("#Info_Trust_Type_id >> dd >> a")
        self.type_of_trust_prs_dropdown: Locator = self.form_root.locator("#Info_Trust_Addl_Dist_id > dt > a > span:nth-of-type(1)")
        self.type_of_trust_prs_list: Locator = self.form_root.locator("#Info_Trust_Addl_Dist_id > dd > dl > dd > a")
        self.date_of_trust: Locator = self.form_root.locator("//*[@id[contains(., 'line_Questions_') and contains(., '__Info_Trust_Date')]] | //*[@id='line_Questions_1__Info_Trust_Date']")
        self.trust_needed_authorization_dropdown: Locator = self.form_root.locator("#Info_Trust_Act_Num_id")
        self.trust_needed_authorization_options: Locator = self.form_root.locator("#Info_Trust_Act_Num_id >> dd >> dl >> dd >> a")
        self.trustees_act_independently: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_Auth_N_tab")
        self.trust_nature_input: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_Nature")
        self.last_amendment_input: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_Date_Amend")
        self.trustees_natural_persons_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_NaturalPerson_No_tab")
        self.beneficiaries_natural_persons_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_NaturalPersonBene_No_tab")
        self.trust_legally_compliant_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_Organized_No_tab")
        self.trust_cdd_exempt_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_CDD_N_tab")
        self.trust_offshore_no: Locator = self.form_root.locator("#line_Questions_1__Info_Trust_Offshore_N_tab")
        self.trust_cash_asset_mgmt_allowed_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_AuthChecking_N_tab")
        self.trust_allow_poa_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_AuthPOA_N_tab")
        self.trust_allow_option_trading_no: Locator = self.form_root.locator("#line_Questions_0__Info_Trust_AuthOptions_N_tab")
        self.ira_account_funded_no: Locator = self.form_root.locator("#line_Questions_1__Info_IRA_Inher_Relat_Orig_tab")
        self.ira_decedent_name_input: Locator = self.form_root.locator("#line_Questions_0__Info_IRA_Inher_Relat_Name")
        self.ira_decedent_dob_input: Locator = self.form_root.locator("#line_Questions_0__Info_IRA_Inher_Relat_dob")
        self.ira_decedent_dod_input: Locator = self.form_root.locator("#line_Questions_1__Info_IRA_Inher_Relat_dod")
        self.beneficiary_relationship_spouse: Locator = self.form_root.locator("[id*='Prim_Bene_Acct_Relat_Spouse_0_tab'], [id*='Info_IRA_Inher_Relat_Orig_Rel_Sps_tab']")
        self.plan_established_on: Locator = self.form_root.locator("#line_Questions_1__Info_Plan_Date")
        self.decedent_first_name: Locator = self.form_root.locator("#line_Questions_0__Info_Dec_Name_First")
        self.decedent_last_name: Locator = self.form_root.locator("#line_Questions_2__Info_Dec_Name_Last")
        
        # Trustee Title locator (401k - required field on trustee page)
        self.trustee_title_input: Locator = self.form_root.locator("input[name='Hold_Trustee_Title_0']")

        # Participant locators (401k)
        self.participant_button: Locator = self.form_root.locator("//button[contains(@class, 'btn-next') and .//span[text()='Participant']]")
        self.add_participant_button: Locator = self.form_root.locator("a[data-toggle='Hold_PeoplePicker_Multi_Participant_COUNT']")
        self.participant_existing_client: Locator = self.form_root.locator(".popover-content .popover-picker[data-domaintype='Person']:not(.popover-picker-add)")
        self.participant_add_new: Locator = self.form_root.locator(".popover-content .popover-picker-add:not(.redtail-popover)")
        self.participant_business_owner_radio: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Participant_Relationship_Owner_tab")
        self.participant_spouse_radio: Locator = self.form_root.locator("#question_line_Questions_0__Hold_Participant_Relationship_Spouse_tab")
        self.participant_first_name: Locator = self.form_root.locator("input[name='Hold_Participant_Name_FIRSTNAME']")
        self.participant_last_name: Locator = self.form_root.locator("input[name='Hold_Participant_Name_LASTNAME']")
        self.participant_dob: Locator = self.form_root.locator("input[name='Hold_Participant_DOB']")
        self.participant_ssn: Locator = self.form_root.locator("#question_line_Questions_1__Hold_Participant_SSN")
        
        # Retirement Plan Info locators (401k)
        self.retirement_plan_info_button: Locator = self.form_root.locator("//button[contains(@class, 'btn-next') and .//span[contains(text(), 'Retirement Plan Information')]]")
        self.irs_plan_document_section: Locator = self.form_root.locator("#Info_Plan_Administrator")
        self.irs_plan_document_radios: Locator = self.form_root.locator("#Info_Plan_Administrator .radio-tab.hidden-tab")
        self.irs_plan_document_yes_amrs: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Yes_AMRS_tab")
        self.irs_plan_document_yes_convert: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Yes_Convert_tab")
        self.irs_plan_document_yes_outside_tpa: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Yes_Outside_TPA_tab")
        self.irs_plan_document_no_startup: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_No_Startup_tab")
        self.irs_plan_document_no: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_No_Outside_TPA_tab")
        self.irs_plan_document_info_label: Locator = self.form_root.locator("#Info_Plan_Administrator_Label")
        self.plan_sponsor_name_input: Locator = self.form_root.locator("#line_Questions_1__Info_Plan_Administrator_PS_Name")
        self.full_legal_name_input: Locator = self.form_root.locator("#line_Questions_1__Info_Plan_Administrator_Full")
        self.plan_amended_restated_input: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Convert_Amend")
        self.plan_effective_date_input: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Yes_Convert_Eff_Dt")
        self.business_type_dropdown_trigger: Locator = self.form_root.locator("#Info_Plan_Administrator_Business_id > .firstmenu > a")
        self.business_type_options: Locator = self.form_root.locator("#Info_Plan_Administrator_Business_id .styled-ddl > dd > a")
        self.year_end_dropdown_trigger: Locator = self.form_root.locator("#Info_Plan_Administrator_Yr_End_id > .firstmenu > a")
        self.year_end_options: Locator = self.form_root.locator("#Info_Plan_Administrator_Yr_End_id .styled-ddl > dd > a")
        self.add_new_bank_link: Locator = self.form_root.locator("a.bank-select[data-questionid='Info_Employer_Bank']")
        self.epic_email_input: Locator = self.form_root.locator("#line_Questions_0__Info_Plan_Administrator_Email")
        self.bank_modal: Locator = self.page.locator("#Info_Employer_Bank_BankModal")
        self.bank_routing_input: Locator = self.page.locator("#line_Questions_0__RoutingNumber_Info_Employer_Bank_BANKROUTING_Modal")
        self.bank_name_modal_input: Locator = self.page.locator("#line_Questions_0__AccountName_Info_Employer_Bank_BANKNAME_Modal")
        self.bank_account_number_input: Locator = self.page.locator("#line_Questions_0__AccountNumber_Info_Employer_Bank_BANKACCOUNT_Modal")
        self.bank_name_on_account_input: Locator = self.page.locator("#line_Questions_0__AccountTitle_Info_Employer_Bank_BANKNAMEONACCOUNT_Modal")
        self.bank_modal_save_button: Locator = self.page.locator("#Info_Employer_Bank_BankModal button.btn-primary[data-save-bank-url='/AccountSetup/Interview/AddBankToDomain'][data-bank-type='BankTemplateTitle']")
        self.bank_routing_error: Locator = self.page.locator("#Info_Employer_Bank_BankModal span.text-danger")
        self.full_legal_title: Locator = self.form_root.locator("input[name='Info_FullLegalTitle']")
        self.not_saved_error_locator: Locator = self.form_root.locator("div.alert-danger:visible, div.validation-summary-errors:visible, div:has-text('has NOT been saved'):visible")
        
        # IPG FA Authorization locators
        self.ipg_fa_auth_partial: Locator = self.form_root.locator("#Partial")
        self.ipg_fa_auth_full: Locator = self.form_root.locator("#Full")
        self.ipg_fa_auth_none: Locator = self.form_root.locator("#None")
        
        # TMS error handling
        self.tax_management_error_msg: Locator = self.form_root.locator("//div[contains(text(),'The information above has been')]").first
        self.tax_management_info_page_label: Locator = self.form_root.locator("//label[normalize-space(text())='Tax Management Services']")
        self.add_information_link: Locator = self.form_root.locator("//a[text()='Add Information']")
        
        # Additional Info Page locators (for select_state, add_info_page_ssn, account_additional_info)
        self.info_page_state_dropdown: Locator = self.form_root.locator("//*[contains(@id,'_State_id') or contains(@id,'_StOrg_id') or contains(@id,'_Minor_St_tab') or @id='Info_CP_Hold_Addr_A_STATE_0_id']")
        self.info_page_state_list: Locator = self.form_root.locator("//*[contains(@id, '_State_id') or contains(@id, '_StOrg_id') or contains(@id, '_Minor_St_id') or @id='Info_CP_Hold_Addr_A_STATE_0_id']/dd/dl/dd/a")
        self.pershing_trust_state_dropdown_trigger: Locator = self.form_root.locator("#Info_Joint_State_id > .firstmenu > a, #Info_Ent_StOrg_id > .firstmenu > a")
        self.pershing_trust_state_options: Locator = self.form_root.locator("#Info_Joint_State_id dd dl dd a, #Info_Ent_StOrg_id dd dl dd a")
        self.info_page_ssn: Locator = self.form_root.locator("//*[@id='line_Questions_0__Info_SSN_TIN'] | //*[@id='line_Questions_0__Info_SSN_TIN_Trust'] | //*[@id='line_Questions_0__Info_TaxNum_Trust']")
        self.ssn_label: Locator = self.form_root.locator("//span[text()='SSN']")
        # Source of Funds dropdown - triggered by dt > a, options in dd > dl > dd > a structure
        # Multiple locator patterns to handle different contexts/pages
        self.source_of_funds_dropdown_trigger: Locator = self.form_root.locator("#Info_Fund_Meth_id > .firstmenu > a, #Info_Fund_Meth_id dt.firstmenu > a, #Info_Fund_Meth_id dt > a")
        self.source_of_funds_options: Locator = self.form_root.locator("#Info_Fund_Meth_id dd dl dd a, #Info_Fund_Meth_id dd a, [data-selected-value='Info_ISF_Gift']")
        # Keep old names for backwards compatibility
        self.source_funds_dropdown: Locator = self.form_root.locator("#Info_Fund_Meth_id > .firstmenu > a, #Info_Fund_Meth_id dt.firstmenu > a, #Info_Fund_Meth_id dt > a")
        self.source_of_funds_list: Locator = self.form_root.locator("#Info_Fund_Meth_id dd dl dd a, #Info_Fund_Meth_id dd a")
        self.client_marital_status_dropdown: Locator = self.form_root.locator("//*[@id='Info_Marital_Status_id']/dt/a/span[1]")
        self.client_marital_list: Locator = self.form_root.locator("//*[@id='Info_Marital_Status_id']/dd/dl/dd/a")
        self.purpose_of_account_dropdown: Locator = self.form_root.locator("//*[@id='Info_OSF_id']/dt/a/span[1]")
        self.purpose_of_account_list: Locator = self.form_root.locator("//*[@id='Info_OSF_id']/dd/dl/dd/a")
        self.can_tda_share_address: Locator = self.form_root.locator("input[id*='InformationSharing_N_tab']")
        self.prior_advisor_change_type: Locator = self.form_root.locator("//*[@id='line_Questions_0__Info_SDBA_PriorIA_Add_tab']")
        self.retirement_plan_employer_name: Locator = self.form_root.locator("//input[@name='Info_SDBA_RPN']")
        self.retirement_plan_account_number: Locator = self.form_root.locator("//input[@name='Info_SDBA_RPAN']")
        self.investment_account_number: Locator = self.form_root.locator("//input[@name='Info_Investment_AccountNumber_VALUE']")
        
        # REFACTORED: Inline locators moved from methods to __init__
        # Modal locators
        self.modal_visible: Locator = self.form_root.locator("div.modal:visible")
        self.state_modal_span: Locator = self.form_root.locator("#Hold_HomeAddr_STATE_0_Modal_id > .firstmenu > a").first
        
        # Account Information button/link locators
        self.account_info_button_url: Locator = self.form_root.locator("button[data-url*='Info_Page']")
        self.account_info_link_url: Locator = self.form_root.locator("a[href*='Info_Page']")
        self.account_list_links: Locator = self.form_root.locator("//table//a[contains(@href, 'Info_Page')] | //div[contains(@class, 'account-name')]/a | //tr[contains(@class, 'account')]/td[1]/a")
        
        # LLC Type - hidden-tab element, same ID in both navbar and non-navbar flows
        self.llc_type_span: Locator = self.form_root.locator("#line_Questions_0__Info_LLC_Ccorp_tab")
        
        # Beneficial ownership - hidden-tab elements, use form_root for dual-flow
        self.beneficial_ownership_input: Locator = self.form_root.locator(
            "#line_Questions_0__Info_CP_EntityOwner_ControlPerson_Additional_Yes_tab"
        )
        self.control_person_input: Locator = self.form_root.locator(
            "#line_Questions_0__line_Questions_0__Info_CP_EntityOwner_ControlPerson_Yes_0_tab"
        )
        self.entity_owner_input: Locator = self.form_root.locator(
            "#line_Questions_0__line_Questions_0__Info_CP_EntityOwner_EntityOwner_Yes_0_tab"
        )
        
        # Beneficial state menu
        self.beneficial_state_menu: Locator = self.form_root.locator("#Info_CP_Hold_Addr_A_STATE_0_id")
        
        # Navigation buttons (generic)
        self.all_btn_next_buttons: Locator = self.form_root.locator("button.btn-next")
        self.all_buttons: Locator = self.form_root.locator("button")
        
        # Subnav links
        self.subnav_links: Locator = self.form_root.locator("//a[contains(@class, 'subnav-link') and @data-page-id]")
        
        # IPG FA section
        self.fa_section: Locator = self.form_root.locator("//*[@id='Info_FAA']/div/div")
        
        # Fidelity Trust state dropdown fallback
        self.fidelity_trust_state_dropdown_fallback: Locator = self.form_root.locator("#Info_Ent_StOrg_id, [id*='_StOrg_id'], [id*='_State_id']")
        
        # Joint state and fund method dropdowns for account_additional_info
        self.fund_meth_dropdown_trigger: Locator = self.form_root.locator("#Info_Fund_Meth_id > .firstmenu > a")
        self.fund_meth_dropdown_container: Locator = self.form_root.locator("#Info_Fund_Meth_id")
        
        # Popover locators
        self.popover_content: Locator = self.form_root.locator("div.popover-content.custom-popover-content")
        self.picker_name: Locator = self.form_root.locator("div.picker-name")
        
        # Donor info message locator (for evaluation)
        self.donor_info_message_element: Locator = self.form_root.locator("//*[@id='IA_Name_Msg_0']")
        
        # FAA Payment Method / Related Billing locators
        self.faa_payment_method_dropdown: Locator = self.form_root.locator(
            "#Info_FAA_PayMeth_id > .firstmenu > a, "
            "#Info_FAA_PayMeth_id dt > a, "
            "[id*='FAA_PayMeth'] > dt > a"
        )
        self.faa_payment_method_options: Locator = self.form_root.locator(
            "#Info_FAA_PayMeth_id dd dl dd a, "
            "[id*='FAA_PayMeth'] dd a"
        )
        self.debit_another_account_option: Locator = self.form_root.locator(
            "#Info_FAA_PayMeth_id dd a:has-text('Debit from another AssetMark account'), "
            "[id*='FAA_PayMeth'] dd a:has-text('Debit from another AssetMark account')"
        )
        self.billing_model_dropdown: Locator = self.form_root.locator(
            "#Info_FAA_BillAcct_id > .firstmenu > a, "
            "[id*='FAA_BillAcct'] > dt > a, "
            "[id*='FAA_Bill'] > dt > a"
        )
        self.billing_model_options: Locator = self.form_root.locator(
            "#Info_FAA_BillAcct_id dd dl dd a, "
            "[id*='FAA_BillAcct'] dd a, "
            "[id*='FAA_Bill'] dd a"
        )
        self.billing_error_message: Locator = self.form_root.locator(
            "#Info_FAA .field-validation-error, "
            "#Info_FAA .error-message, "
            "[id*='FAA'] .validation-error"
        )
        self.skip_button: Locator = self.form_root.get_by_role("button", name="Skip")   
        self.email_input_modal: Locator = self.form_root.locator("input[id*='EmailAddress']")
        self.email_error_modal: Locator = self.form_root.locator(
            "input[id*='Hold_Email_0'] ~ .field-validation-error, "
            "div[id*='EmailAddressPopup_HtmlId'] .error-message, "
            ".validation-summary-errors:near(input[id*='Hold_Email_0'])"
        ) 

        if page_verification:
            self._verify_page_label()

    def navigate_menu_option(self, option_name: str) -> None:
        """Navigate to a page by clicking on a menu option in the subnav"""
        link = self.form_root.get_by_role("link", name=option_name)
        link.wait_for(state="visible", timeout=10000)
        link.click()
        self._wait_for_page_ready()

    def _verify_page_label(self):
        """Verify account setup page is loaded"""
        try:
            # Wait for page to be ready
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            
            # Try to find any indicator that page is loaded
            # Look for the account holder section or save button
            if self.save_account_button.count() > 0:
                logger.info(f"{self.PAGE_NAME} verification: PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification: FAILED")
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification failed: {str(e).splitlines()[0]}")

    def wait_until_page_fully_loads(self) -> None:
        """Wait for the account setup page to fully load"""
        try:
            # Wait for JS to load
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            # Wait for network to be idle
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except:
                pass
            
            # Wait for the add holder/trustee buttons or any account wizard content
            # Check multiple indicators that the page is ready
            self.page.wait_for_function(
                """() => {
                    // Check if we can find account setup related elements
                    const saveBtn = document.querySelector('button.people-picker-save-button');
                    const holderBtn = document.querySelector('[data-toggle*="Hold_PeoplePicker"]:not([data-toggle*="Multi"])');
                    const trusteeBtn = document.querySelector('[data-toggle*="Hold_PeoplePicker_Multi"]');
                    const form = document.querySelector('form');
                    
                    // Page is ready if we have form and at least one button
                    return form && (saveBtn || holderBtn || trusteeBtn);
                }""",
                timeout=10000
            )
            logger.info("Account setup page fully loaded")
        except Exception as e:
            pass

    # ========== HELPER METHODS ==========
    
    def _wait_for_page_ready(self, timeout: int = 30000) -> None:
        """Common wait pattern for page being ready"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception as e:
            pass
        self.wait_for_loading_data()
    
    def _click_button_with_fallback(self, primary_locator: Locator, fallback_selectors: List[str], 
                                     button_name: str, timeout: int = 10000) -> None:
        """Click button with fallback selectors if primary fails"""
        # Try primary locator
        try:
            if primary_locator.count() > 0 and primary_locator.first.is_visible(timeout=timeout):
                primary_locator.first.scroll_into_view_if_needed()
                primary_locator.first.click()
                logger.info(f"Clicked {button_name} with primary selector")
                return
        except Exception as e:
            logger.warning(f"{button_name} primary selector failed: {str(e)[:100]}")
        
        # Try fallback selectors
        for selector in fallback_selectors:
            try:
                btn = self._get_locator_by_selector(selector).first
                if btn.count() > 0 and btn.is_visible(timeout=2000):
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    logger.info(f"Clicked {button_name} with fallback: {selector}")
                    return
            except Exception:
                continue
        
        raise RuntimeError(f"{button_name} not found with any selector")
    
    def _navigate_to_page(self, button_locator: Locator, page_name: str, 
                          fallback_selectors: Optional[List[str]] = None) -> None:
        """Generic navigation to next page by clicking button"""
        self._wait_for_page_ready()
        
        if fallback_selectors:
            self._click_button_with_fallback(button_locator, fallback_selectors, page_name)
        else:
            button_locator.wait_for(state="visible", timeout=10000)
            button_locator.click()
            logger.info(f"Clicked {page_name} button")
        
        self._wait_for_page_ready()
    
    def _get_existing_account_option(self) -> Locator:
        """Get existing account option from popover - dynamic locator"""
        popover = self._get_locator_by_selector("div.popover-content.custom-popover-content")
        if popover.count() > 0 and popover.first.is_visible(timeout=2000):
            return popover.first.locator("div").first
        return self._get_locator_by_selector("div.picker-name").first
    
    def _get_state_option_locator(self, state_type: str) -> Locator:
        """Get state option locator for a specific state type - dynamic locator helper"""
        return self._get_locator_by_selector(
            f"#Info_Ent_StOrg_id dd a:has-text('{state_type}'), "
            f"dl[data-type='state'] dd a:has-text('{state_type}')"
        ).first

    def _get_locator_by_selector(self, selector: str) -> Locator:
        """Get locator by selector string - dynamic locator helper"""
        # Use the active root (iframe or page) to find the locator
        return self.form_root.locator(selector)

    def _get_text_locator(self, text: str, exact: bool = False) -> Locator:
        """Get locator by text - dynamic locator helper"""
        return self.page.get_by_text(text, exact=exact)

    def _get_tooltip_text_locator(self, text: str, exact: bool = False) -> Locator:
        """Get tooltip child locator by text - dynamic locator helper"""
        return self.page.get_by_role("tooltip").get_by_text(text, exact=exact)
    
    def _get_modal_scoped_locator(self, modal: Locator, selector: str) -> Locator:
        """Get a locator scoped to a specific modal - dynamic locator helper"""
        return modal.locator(selector)
    
    def _select_employment_status(self, employment_status: str, custodian_name: str = "") -> None:
        """Helper method to select employment status from dropdown - works in headed and headless mode"""
        custodian_msg = f" ({custodian_name})" if custodian_name else ""
        
        try:
            # Ensure the dropdown trigger is visible
            self.employment_status_dropdown.wait_for(state="visible", timeout=10000)
            self.employment_status_dropdown.scroll_into_view_if_needed()
            
            # Use regular click (not force) to properly trigger all mouse/hover events
            # force=True skips mouseenter events that the dropdown JS needs to open
            self.employment_status_dropdown.click()
            logger.info("Clicked employment status dropdown")
            
            # Wait for the first option in the list to become visible (confirms dropdown is open)
            self.employment_list.first.wait_for(state="visible", timeout=10000)
            
            # Find and click the matching option
            options = self.employment_list.all()
            logger.info(f"Found {len(options)} employment status options")
            
            # Exact match
            for option in options:
                if option.text_content().strip() == employment_status.strip():
                    option.click()
                    logger.info(f"Selected Employment Status: {employment_status}{custodian_msg}")
                    return
            
            # Case-insensitive fallback
            for option in options:
                if employment_status.lower() in option.text_content().lower():
                    option.click()
                    logger.info(f"Selected Employment Status (case-insensitive): {employment_status}{custodian_msg}")
                    return
            
            available = [o.text_content().strip() for o in options[:15]]
            raise Exception(f"Option '{employment_status}' not found. Available: {available}")
            
        except Exception as e:
            logger.error(f"Employment status selection failed{custodian_msg}: {str(e).splitlines()[0]}")
            raise
    
    def _handle_income_source(self, employment_status: str, source_of_income: str = "") -> None:
        """Helper method to handle income source for unemployed status"""
        if employment_status and ("not employed" in employment_status.lower() or "unemployed" in employment_status.lower()):
            try:
                income = self.income_source_input
                income.wait_for(state="visible", timeout=10000)
                income_value = source_of_income if source_of_income else "bank interest"
                income.fill(income_value)
                logger.info(f"Filled income source: {income_value}")
            except Exception as e:
                logger.warning(f"Could not fill income source: {str(e).splitlines()[0]}")

    def _fill_pershing_employment_details(self, address_line1: str = "") -> None:
        """Fill Pershing employment details when fields are present."""
        try:
            if self.employer_name_input.is_visible(timeout=2000):
                self.employer_name_input.fill("sddsvds")
            if self.employer_business_type_input.is_visible(timeout=2000):
                self.employer_business_type_input.fill("sddsfds")
            if self.employer_years_input.is_visible(timeout=2000):
                self.employer_years_input.fill("6")
            if self.employer_occupation_input.is_visible(timeout=2000):
                self.employer_occupation_input.fill("testy")

            if self.employer_iir_dropdown.is_visible(timeout=2000):
                self.select_option_from_list(
                    self.employer_iir_dropdown,
                    self.employer_iir_options,
                    "Not Applicable",
                    "Selected IIR option"
                )

            if self.employer_address_add_link.is_visible(timeout=2000):
                self.employer_address_add_link.click()
                self.page.wait_for_timeout(500)
                hint = (address_line1.split()[-1] if address_line1 else "SHEPHERD").upper()
                self._get_tooltip_text_locator(hint, exact=False).click()
        except Exception as e:
            logger.warning(f"Pershing employment details fill skipped: {str(e).splitlines()[0]}")

    def _select_source_of_funds(self, source_of_income: str) -> bool:
        """Helper method to select source of funds with fallback approaches"""
        if not source_of_income:
            return False
        
        try:
            # Approach 1: select from known dropdown structure
            self.select_option_from_list(
                self.source_of_funds_dropdown_trigger,
                self.source_of_funds_options,
                source_of_income,
                f"Selected Source of Funds: {source_of_income}"
            )
            return True
        except Exception as e1:
            logger.warning(f"Approach 1 (select_option_from_list) failed: {e1}")
            
            try:
                self.click(self.form_root.locator("#Info_ISF_id"))
                self.click(self.form_root.get_by_text(source_of_income))
            except Exception as e2:
                logger.warning(f"Approach 2 (select_option) failed: {e2}")
                # Approach 2: explicit open + robust option text matching
                trigger = self.form_root.locator(
                    "#Info_Fund_Meth_id > .firstmenu > a, "
                    "#Info_Fund_Meth_id dt > a, "
                    "[id*='Fund_Meth_id'] dt > a"
                ).first
                trigger.wait_for(state="visible", timeout=5000)
                trigger.click(timeout=5000)
                self.page.wait_for_timeout(500)

                options = self.form_root.locator(
                    "#Info_Fund_Meth_id dd dl dd a, "
                    "[id*='Fund_Meth_id'] dd dl dd a"
                ).all()
                requested = " ".join(source_of_income.split()).lower()
                for option in options:
                    option_text = " ".join((option.text_content() or "").split()).lower()
                    if requested == option_text or requested in option_text or option_text in requested:
                        option.click()
                        logger.info(f"Selected Source of Funds using option iteration: {source_of_income}")
                        return True

                # Approach 3: visible text click within opened dropdown
                fallback_option = self.form_root.locator(
                    "#Info_Fund_Meth_id dd a:has-text('" + source_of_income + "'), "
                    "[id*='Fund_Meth_id'] dd a:has-text('" + source_of_income + "')"
                ).first
                if fallback_option.is_visible(timeout=2000):
                    fallback_option.click()
                    logger.info(f"Selected Source of Funds using fallback text locator: {source_of_income}")
                    return True

                logger.warning(f"Source of Funds '{source_of_income}' not found in dropdown options")
                return False
            except Exception as e2:
                logger.warning(f"Approach 2 (option iteration) failed: {e2}")
                return False

    # ========== MAIN METHODS ==========

    def click_add_new_account(self, client_type: str, reg_type: str, step_name: str):
        """Click Add New Account button based on registration type"""
        logger.info(step_name)
        logger.info(f"Reg type: {reg_type}")
        _ = client_type  # Kept for method signature compatibility
        # Wait for page to fully load
        self.wait_until_page_fully_loads()
        
        
        try:
            if reg_type.lower() == "trust":
                logger.info("Selecting trustee button")
                add_trustee = self._get_locator_by_selector(
                    "[data-toggle*='Hold_PeoplePicker_Multi_COUNT']"
                ).first
                
                # Check if trustee button exists in DOM
                count = add_trustee.count()
                logger.info(f"Trustee button count: {count}")
                
                if count == 0:
                    logger.warning("Trustee button not found with primary selector, trying fallback")
                    # Try alternative selectors for trust
                    fallback_selectors = [
                        "button:has-text('Add Trustee')",
                        "button:has-text('Add Account')",
                        "a:has-text('Add Trustee')",
                        "[data-toggle*='Hold_PeoplePicker']",  # Any people picker
                    ]
                    for selector in fallback_selectors:
                        candidate = self._get_locator_by_selector(selector)
                        if candidate.count() > 0:
                            logger.info(f"Using fallback trustee selector: {selector}")
                            add_trustee = candidate.first
                            break
                    
                    if add_trustee.count() == 0:
                        logger.warning("No trustee button found, trying holder button as final fallback")
                        add_trustee = self._get_locator_by_selector(
                            "[data-toggle*='Hold_PeoplePicker']:not([data-toggle*='Multi'])"
                        ).first
                
                add_trustee.wait_for(state="visible", timeout=10000)
                add_trustee.click()
                logger.info("Trustee button clicked")
            else:
                logger.info("Selecting holder button")
                add_holder = self._get_locator_by_selector(
                    "[data-toggle*='Hold_PeoplePicker']:not([data-toggle*='Multi'])"
                ).first
                
                # Check if locator exists
                count = add_holder.count()
                
                if count == 0:
                    # Try alternative selectors by visible text/aria-label
                    try:
                        candidates = self._get_locator_by_selector(
                            "button, a, [role='button']"
                        ).evaluate_all(
                            """
                                els => els
                                    .map(el => ({
                                        text: (el.innerText || '').trim(),
                                        id: el.id || '',
                                        className: el.className || '',
                                        dataToggle: el.getAttribute('data-toggle') || ''
                                    }))
                                    .filter(x => x.text || x.dataToggle)
                                    .filter(x => /add|holder|trust|account/i.test(x.text) || /hold|peoplepicker/i.test(x.dataToggle))
                                    .slice(0, 20)
                            """,
                        )
                    except Exception as e:
                        logger.info(f"Unable to collect candidate buttons: {str(e).splitlines()[0]}")

                    # Try alternative selectors by visible text/aria-label
                    fallback_selectors = [
                        "a[data-toggle='Hold_PeoplePicker_Multi_COUNT']",
                        "a:has-text('Add Authorized Agents')",
                        "button:has-text('Add Account Holder')",
                        "button:has-text('Add Holder')",
                        "[aria-label*='Add'][aria-label*='Holder']",
                    ]
                    for selector in fallback_selectors:
                        candidate = self._get_locator_by_selector(selector)
                        if candidate.count() > 0:
                            add_holder = candidate.first
                            break

                    # Final fallback: use the multi/authorized-agents button when present
                    if add_holder.count() == 0:
                        add_trustee = self._get_locator_by_selector(
                            "[data-toggle*='Hold_PeoplePicker_Multi_COUNT']"
                        )
                        if add_trustee.count() > 0:
                            logger.info("Using authorized-agents button as fallback")
                            add_holder = add_trustee.first
                
                add_holder.wait_for(state="visible", timeout=10000)
                add_holder.click()
                logger.info("Holder button clicked")
            
            # Wait for popover to appear
            self.page.wait_for_timeout(500)
            
            # Click Add New link
            logger.info("Looking for Add New link")
            try:
                add_new = self._get_locator_by_selector("text=/^Add New$/").first
                if add_new.is_visible(timeout=3000):
                    add_new.click()
                    logger.info("Add New link clicked")
                else:
                    logger.info("Add New link not visible; trying first popover option")
                    try:
                        existing_option = self._get_existing_account_option()
                        if existing_option.is_visible(timeout=2000):
                            existing_option.click()
                            logger.info("Popover option clicked")
                        else:
                            logger.info("No popover option visible; continuing without it")
                    except Exception as option_error:
                        logger.warning(f"Popover option not available: {str(option_error)}")
            except Exception as e:
                logger.warning(f"Add New link not available: {str(e).splitlines()[0]}")
        except Exception as e:
            logger.error(f"Error in click_add_new_account: {str(e).splitlines()[0]}")
            # Log current URL for debugging
            logger.info(f"Current URL: {self.page.url}")
            raise

    def add_account(
        self,
        client_type: str,
        first_name: str,
        middle_name: str,
        last_name: str,
        birth_date: str,
        ssn: str,
        step_name: str,
        log_message: str,
    ):
        """Add account holder information"""
        logger.info(step_name)
        
        # First name
        name_input = self._get_locator_by_selector("input[name='Hold_Name_FIRSTNAME_0']").first
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(first_name)
        logger.info(f"enter first name: {first_name}")
        
        # Last name
        last_name_input = self._get_locator_by_selector("input[name='Hold_Name_LASTNAME_0']").first
        last_name_input.wait_for(state="visible", timeout=5000)
        last_name_input.fill(last_name)
        logger.info(f"enter last name: {last_name}")
        
        # Verify donor info requirement if applicable
        if client_type and "Donor Advised Fund" in client_type:
            donor_msg = self.is_donor_info_required
            try:
                bg_color = self.donor_info_message_element.evaluate(
                    "el => getComputedStyle(el).backgroundColor"
                )
                msg_text = donor_msg.text_content()
                logger.info(f"Donor message: {msg_text}, BG Color: {bg_color}")
            except:
                pass
        
        # Birth date
        birth_input = self._get_locator_by_selector("input[name='Hold_DOB_0']").first
        birth_input.wait_for(state="visible", timeout=5000)
        if birth_date is None:
            birth_value = ""
        elif hasattr(birth_date, "strftime"):
            # Handles datetime/date-like objects from Excel loaders.
            birth_value = birth_date.strftime("%m%d%Y")
        else:
            birth_value = str(birth_date).strip()

        # Normalize typical date string variants to MMDDYYYY when possible.
        digits_only = "".join(ch for ch in birth_value if ch.isdigit())
        if len(digits_only) == 8:
            birth_value = digits_only

        if len(birth_value) <= 7:
            birth_value = "01011960"

        birth_input.fill(birth_value)
        logger.info(f"enter dob: {birth_value}")
        
        # SSN
        ssn_input = self._get_locator_by_selector("input[name*='Hold_SSN_0']:not([type='hidden'])").first
        ssn_input.wait_for(state="visible", timeout=5000)
        ssn_value = "" if ssn is None else str(ssn).strip()
        ssn_input.fill(ssn_value)
        logger.info(f"enter SSN: {ssn_value}")

    def add_phone_and_email(self, phone: str, email: str):
        """Add phone and email information"""
        phone_value = "" if phone is None else str(phone).strip()
        email_value = "" if email is None else str(email).strip()

        phone_input = self._get_locator_by_selector("#question_line_Questions_0__Hold_Phone_0").first
        phone_input.wait_for(state="visible", timeout=5000)
        phone_input.fill(phone_value)
        
        email_input = self._get_locator_by_selector("input[id*='Hold_Email_0']").first
        email_input.wait_for(state="visible", timeout=5000)
        email_input.fill(email_value)
        
        # Fill mother's maiden name if visible
        try:
            maiden_name = self._get_locator_by_selector("#question_line_Questions_0__Hold_MoMaNa_0").first
            if maiden_name.is_visible(timeout=2000):
                maiden_name.fill("abcde")
        except:
            pass

    def fill_email(self, email: str) -> None:
        """Fill the account holder email input field."""
        email_value = "" if email is None else str(email).strip()
        self.email_input.first.wait_for(state="visible", timeout=5000)
        self.fill(self.email_input.first, email_value)
        logger.info(f"Filled email field with: {email_value}")

    def add_account_home_address(
        self, address_line: str, city: str, state: str, zip_code: str, step_name: str, log_message: str
    ):
        """Add account home address"""
        logger.info(step_name)
        address_line_value = "" if address_line is None else str(address_line).strip()
        city_value = "" if city is None else str(city).strip()
        state_value = "" if state is None else str(state).strip()
        zip_code_value = "" if zip_code is None else str(zip_code).strip()
        self.page.wait_for_timeout(1000)  # Small pause to ensure any dynamic content has loaded
        
        # Click add address button using data-questionid attribute
        add_addr_btn = self._get_locator_by_selector("a.address-select[data-questionid='Hold_HomeAddr_0']").first
        add_addr_btn.wait_for(state="visible", timeout=5000)
        add_addr_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)  # Wait for scroll to complete
        add_addr_btn.click()
        self.page.wait_for_timeout(500)  # Wait for click handler to execute

        # Wait for address modal to open (retry opening modal if needed)
        modal = self._get_locator_by_selector("div.modal:visible").first
        modal_opened = False
        for attempt in range(3):
            try:
                modal.wait_for(state="visible", timeout=3000)
                modal_opened = True
                break
            except Exception:
                logger.warning(f"Address modal not visible yet (attempt {attempt + 1}/3), retrying Add Address click")
                add_addr_btn.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                add_addr_btn.click(force=True)
                self.page.wait_for_timeout(1000)  # Wait for modal animation

        if not modal_opened:
            visible_inputs = []
            try:
                visible_inputs = self.page.eval_on_selector_all(
                    "input[name*='Addr_ADDRESS1_0_Modal']",
                    "els => els.filter(e => e.offsetParent).map(e => e.name)",
                )
            except Exception:
                pass
            try:
                add_buttons = self.page.eval_on_selector_all(
                    "a.address-select",
                    "els => els.map(e => ({text: (e.innerText || '').trim(), dataQuestionid: e.getAttribute('data-questionid') || '', visible: !!e.offsetParent}))",
                )
                logger.warning(f"Address buttons: {add_buttons}")
            except Exception:
                pass
            raise RuntimeError(
                "Address modal did not open. Visible address line1 inputs: "
                + str(visible_inputs)
            )

        addr_input = self._get_modal_scoped_locator(modal, "input[name*='Addr_ADDRESS1_0_Modal']")
        addr_input.wait_for(state="visible", timeout=5000)
        addr_input.fill(address_line_value)
        logger.info(f"enter address line 1: {address_line_value}")
        
        # City
        city_input = self._get_modal_scoped_locator(modal, "input[name*='Addr_CITY_0_Modal']")
        city_input.wait_for(state="visible", timeout=5000)
        city_input.fill(city_value)
        logger.info(f"enter city: {city_value}")
        
        # State
        state_dropdown = self._get_modal_scoped_locator(modal, "[id*='_STATE_0_Modal_id']")
        if state_dropdown.count() == 0:
            state_dropdown = self._get_locator_by_selector("#Hold_HomeAddr_STATE_0_Modal_id").first
        state_dropdown.wait_for(state="visible", timeout=3000)

        # Keep only the minimal scroll-up adjustment for this modal section.
        try:
            modal.evaluate("el => { el.scrollTop = 0; }")
            self.page.wait_for_timeout(200)
        except Exception:
            pass
        try:
            state_dropdown.click()
        except Exception:
            self.state_modal_span.click()
        
        # Select state from list - try existing dropdown options first, fallback to inspector pattern
        state_selected = False
        state_options = self._get_modal_scoped_locator(modal, ".show-dropdown.styled-ddl > dd > a")
        options = state_options.all()
        for option in options:
            if option.text_content().strip() == state_value:
                option.click()
                state_selected = True
                break
        if not state_selected:
            # Fallback: use Playwright inspector pattern (firstmenu trigger + get_by_text)
            try:
                trigger = self._get_locator_by_selector("#Hold_HomeAddr_STATE_0_Modal_id > .firstmenu > a").first
                trigger.click()
                self.page.wait_for_timeout(300)
                self._get_locator_by_selector("#Hold_HomeAddr_STATE_0_Modal_id").get_by_text(state_value, exact=True).first.click()
                state_selected = True
            except Exception as e:
                logger.warning(f"State fallback selection also failed: {str(e).splitlines()[0]}")
        
        # Zip
        zip_input = self._get_modal_scoped_locator(modal, "input[name*='Addr_ZIP_0_Modal']")
        zip_input.wait_for(state="visible", timeout=5000)
        zip_input.fill(zip_code_value)
        logger.info(f"enter zip: {zip_code_value}")
        
        # Save address
        save_btn = self._get_modal_scoped_locator(
            modal,
            "button[data-save-address-url='/AccountSetup/Interview/AddAddressToDomain']"
        ).first
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click()
        logger.info("click on save button")
        
        # Verify address modal save
        verify_btn = self._get_modal_scoped_locator(modal, "button:has-text('Save')").first
        verify_btn.wait_for(state="visible", timeout=3000)
        verify_btn.click()

    def add_custodian_info(
        
        self,
        custodian: str,
        reg_type: str,
        client_type: str,
        employment_status: str,
        source_of_income: str = "",
        address_line1: str = "",
    ):
        """Add custodian-specific information"""
        custodian = custodian.lower()
        reg_type = reg_type.lower()
        
        if "pershing" in custodian:
            # Click address 2 years checkbox
            try:
                addr_2yrs = self.address_2yrs_checkbox
                if addr_2yrs.is_visible(timeout=2000):
                    addr_2yrs.click()
            except:
                pass
            
            # Select employment status
            self._select_employment_status(employment_status, "Pershing")
            
            # Handle income source for unemployed
            self._handle_income_source(employment_status, source_of_income)

            # Fill employment details if fields are present (C72062)
            self._fill_pershing_employment_details(address_line1)
        
        elif custodian == "schwab" and "self-directed brokerage account" not in reg_type and "donor advised fund" not in client_type.lower():
            # Select employment status
            self._select_employment_status(employment_status, "Schwab")
            
            # Handle income source for unemployed
            self._handle_income_source(employment_status, source_of_income)
            
            # Click exchange and director checkboxes
            try:
                exchange = self.is_associated_with_exchange
                if exchange.is_visible(timeout=2000):
                    exchange.click()
            except:
                pass
            
            try:
                director = self.is_director_or_shareholder
                if director.is_visible(timeout=2000):
                    director.click()
            except:
                pass
        
        elif custodian == "fidelity" and reg_type in ["trust", "individual", "traditional ira"]:
            self.page.wait_for_load_state("domcontentloaded")
            
            # Click trustee/grantor checkbox
            try:
                trustee = self.trustee_grantor_checkbox
                if trustee.is_visible(timeout=2000):
                    trustee.click()
            except:
                pass
            
            # Click trust revocable checkbox
            try:
                revocable = self.trust_revocable_checkbox
                if revocable.is_visible(timeout=2000):
                    revocable.click()
            except:
                pass
            
            # Select employment status
            self._select_employment_status(employment_status, "Fidelity")
            
            # Handle income source for unemployed
            self._handle_income_source(employment_status, source_of_income)

        elif "assetmark" in custodian and "401" in reg_type:
            logger.info("Adding AssetMark 401k trustee title")
            try:
                if self.trustee_title_input.is_visible(timeout=2000):
                    self.trustee_title_input.fill("Trustee")
                    logger.info("Filled Trustee Title field")
            except Exception:
                pass

        elif "assetmark" in custodian and "limited" in reg_type:
            logger.info("Adding AssetMark Limited Liability control person and entity owner")
            # Click control person checkbox
            try:
                control_person = self._get_locator_by_selector(
                    "#question_line_Questions_0__Hold_Control_Person_No_0_tab"
                ).first
                control_person.wait_for(state="visible", timeout=10000)
                control_person.scroll_into_view_if_needed()
                try:
                    control_person.click(timeout=5000)
                except Exception:
                    control_person.click(force=True, timeout=5000)
                logger.info("Clicked control person checkbox")
            except Exception as e:
                logger.warning(f"Control person checkbox error: {str(e).splitlines()[0]}")

            # Click entity owner checkbox
            try:
                entity_owner = self._get_locator_by_selector(
                    "#question_line_Questions_0__Hold_Entity_Owner_No_0_tab"
                ).first
                entity_owner.wait_for(state="visible", timeout=10000)
                entity_owner.scroll_into_view_if_needed()
                try:
                    entity_owner.click(timeout=5000)
                except Exception:
                    entity_owner.click(force=True, timeout=5000)
                logger.info("Clicked entity owner checkbox")
            except Exception as e:
                logger.warning(f"Entity owner checkbox error: {str(e).splitlines()[0]}")

    def save_account(self, client_type: str = "", step_name: str = "", log_message: str = ""):
        """Save account information"""
        self._wait_for_page_ready()
        
        save_btn = self._get_locator_by_selector("button.people-picker-save-button:visible").first
        save_btn.wait_for(state="visible", timeout=5000)
        
        # Try normal click first, then force click if intercepted
        try:
            save_btn.click(timeout=10000)
        except Exception as e:
            logger.warning(f"Normal click failed: {str(e).splitlines()[0]}, trying force click")
            save_btn.click(force=True)
        
        self._wait_for_page_ready()
        
        # Verify donor button disabled if applicable
        if client_type and "Donor Advised Fund" in client_type:
            try:
                add_holder_btn = self._get_locator_by_selector(
                    "[data-toggle*='Hold_PeoplePicker']:not([data-toggle*='Multi'])"
                ).first
                if "disabled" not in (add_holder_btn.get_attribute("class") or ""):
                    logger.warning("Add Donor button should be disabled after saving")
            except:
                pass

    def click_account_information_button(self, step_name: str = "", log_message: str = ""):
        """Navigate to account information"""
        # Check if already on the page
        try:
            info_state = self._get_locator_by_selector(
                "//*[contains(@id,'_State_id') or contains(@id,'_StOrg_id') or contains(@id,'_Minor_St_tab') or @id='Info_CP_Hold_Addr_A_STATE_0_id']"
            ).first
            info_ssn = self._get_locator_by_selector(
                "//*[@id='line_Questions_0__Info_SSN_TIN'] | //*[@id='line_Questions_0__Info_SSN_TIN_Trust'] | //*[@id='line_Questions_0__Info_TaxNum_Trust']"
            ).first
            if info_state.is_visible(timeout=2000) or info_ssn.is_visible(timeout=2000):
                logger.info("Already on Account Information form; skipping click")
                return
        except Exception:
            pass

        # Prefer button over link
        btn = self._get_locator_by_selector("button[data-url*='Info_Page']").first
        link = self._get_locator_by_selector("a[href*='Info_Page']").first

        try:
            if btn.count() > 0 and btn.is_visible(timeout=5000):
                btn.click()
            elif link.count() > 0 and link.is_visible(timeout=5000):
                link.click()
            else:
                raise RuntimeError("Account Information button/link not visible")
        except Exception as e:
            logger.warning(f"Account Information click failed: {str(e)[:200]}")
            raise

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.wait_for_loading_data()
        logger.info(log_message)

    def select_account_from_list(self, first_name: str = "", last_name: str = ""):
        """Select an account from the list after clicking Account Information button"""
        try:
            self._wait_for_page_ready(timeout=10000)
            
            # Check if already on direct form page (not a list page)
            if self.info_page_state_dropdown.is_visible(timeout=2000) or self.info_page_ssn.is_visible(timeout=2000):
                logger.info("Already on account information form - no list present")
                return
            
            # Find account links (exclude navigation buttons)
            account_links = self.account_list_links.all()
            
            if not account_links:
                logger.info("No account list found")
                return
            
            # Search for account by name if provided
            if first_name or last_name:
                search_name = f"{first_name} {last_name}".strip()
                for link in account_links:
                    text = link.text_content().strip()
                    if search_name.lower() in text.lower():
                        link.click()
                        logger.info(f"Selected account: {text}")
                        self._wait_for_page_ready(timeout=10000)
                        return
            
            # Default: select first account
            account_links[0].click()
            logger.info("Selected first account from list")
            self._wait_for_page_ready(timeout=10000)
        except Exception as e:
            logger.warning(f"Error selecting account: {str(e).splitlines()[0]}, continuing anyway")

    def click_llc_info_button(self, step_name: str = "", log_message: str = ""):
        """Click LLC Information button"""
        self._navigate_to_page(self.llc_info_button, "LLC Information")

    def click_trust_info_button(self, step_name: str = "", log_message: str = ""):
        """Click Trust Information button"""
        self._navigate_to_page(self.trust_info_button, "Trust Information")

    def click_trustors_button(self, step_name: str = "", log_message: str = ""):
        """Click Trustors button"""
        self._navigate_to_page(
            self.trustors_button,
            "Trustors",
            fallback_selectors=[
                "a.subnav-link[data-page-id*='Hold_Trustor']",
                "a[href*='pageId=Hold_Trustor']",
                "button[data-url*='pageId=Hold_Trustor']",
                "[data-page-id*='Hold_Trustor']",
            ],
        )

    def click_grantor_button(self, step_name: str = "", log_message: str = ""):
        """Click Grantor or Additional Party button"""
        btn = self.grantor_button
        try:
            btn.wait_for(state="visible", timeout=10000)
            btn.click()
            logger.info("Clicked Grantor button")
        except Exception as e:
            logger.warning(f"Grantor button error: {str(e).splitlines()[0]}")
            logger.info(log_message)
            self.page.wait_for_load_state("domcontentloaded")
            self.wait_for_loading_data()
        except Exception as e:
            logger.error(f"Failed to click grantor button: {str(e).splitlines()[0]}")
            raise

    def add_tin_number(self, custodian: str, reg_type: str, tin_number: str):
        """Add TIN number for AssetMark LLC and 401k accounts"""
        if "assetmark" in custodian.lower() and ("limited" in reg_type.lower() or "401" in reg_type):
            # Use form_root so this works in both iframe (navbar) and page (non-navbar) contexts
            tin_input = self.form_root.locator("#line_Questions_0__Info_Tin")
            tin_input.wait_for(state="visible", timeout=5000)
            tin_value = "" if tin_number is None else str(tin_number).strip()
            tin_input.fill(tin_value)
            logger.info(f"TIN Number entered: {tin_value}")

    def select_llc_type(self, custodian: str, reg_type: str):
        """Select LLC Type checkbox"""
        if "assetmark" in custodian.lower() and "limited" in reg_type.lower():
            # Element is a hidden-tab input (class='hidden-tab') in both navbar and non-navbar flows.
            # Use form_root for iframe/page dual-flow; use attached state since element is never visible;
            # click via JS because normal click is blocked on hidden elements.
            llc_type = self.form_root.locator("#line_Questions_0__Info_LLC_Ccorp_tab")
            llc_type.wait_for(state="attached", timeout=10000)
            llc_type.evaluate("el => el.click()")
            logger.info("LLC Type selected")

    def add_beneficial_ownership_details(self, custodian: str, reg_type: str, beneficial_data: dict):
        """Add beneficial ownership details for AssetMark LLC accounts"""
        if "assetmark" not in custodian.lower() or "limited" not in reg_type.lower():
            return

        def _click_toggle(toggle: Locator, label: str) -> None:
            # These are hidden-tab inputs ΓÇö use attached state and JS click
            target = toggle.first
            target.wait_for(state="attached", timeout=10000)
            target.evaluate("el => el.click()")
            logger.info(f"{label} selected")

        _click_toggle(self.beneficial_ownership_input, "Beneficial ownership")
        _click_toggle(self.control_person_input, "Control person")
        _click_toggle(self.entity_owner_input, "Entity owner")
        
        # Fill first name
        first_name = self.beneficial_first_name
        first_name.wait_for(state="visible", timeout=5000)
        first_name.fill(beneficial_data.get("first_name", "Elaine"))
        
        # Fill last name
        last_name = self.beneficial_last_name
        last_name.wait_for(state="visible", timeout=5000)
        last_name.fill(beneficial_data.get("last_name", "Jjessamine"))
        
        # Fill DOB - use type() to simulate character-by-character typing like Selenium sendKeys()
        dob = self.beneficial_dob
        dob.wait_for(state="visible", timeout=5000)
        dob.click()  # Click to focus the field first
        dob.clear()  # Clear any existing value
        dob_value = beneficial_data.get("dob", "1/1/1960")
        dob.type(dob_value)  # Type character-by-character like sendKeys()
        logger.info(f"Beneficial DOB entered: {dob_value}")
        
        # Fill SSN
        ssn = self.beneficial_ssn
        ssn.wait_for(state="visible", timeout=5000)
        ssn_value = str(beneficial_data.get("ssn", "368367217")).strip()
        ssn.fill(ssn_value)
        
        # Fill address line 1
        addr_line1 = self.beneficial_address_line1
        addr_line1.wait_for(state="visible", timeout=5000)
        addr_line1.fill(beneficial_data.get("address_line1", "1293 Birdnest"))
        
        # Fill city
        city = self.beneficial_city
        city.wait_for(state="visible", timeout=5000)
        city.fill(beneficial_data.get("city", "Alhambra"))
        
        # Select state (using simple case-insensitive text matching like Java Selenium)
        state_val = (beneficial_data.get("state", "AR") or "AR").strip()
        
        # Get dropdown and options locators
        state_menu = self.beneficial_state_menu
        state_trigger = state_menu.locator(".firstmenu > a")
        
        if state_menu.count() > 0:
            # Click dropdown to expand options
            state_trigger.wait_for(state="visible", timeout=5000)
            state_trigger.click()
            state_menu.wait_for(state="visible", timeout=5000)
            
            # Find and click matching option using case-insensitive text comparison
            # Using >> operator for nested element traversal: dd >> dl >> dd >> a
            options = state_menu.locator("dd >> dl >> dd >> a")
            option_found = False
            
            for index in range(options.count()):
                option = options.nth(index)
                option_text = (option.text_content() or "").strip()
                
                # Case-insensitive comparison matching Java equalsIgnoreCase behavior
                if option_text.lower() == state_val.lower():
                    option.click()
                    logger.info(f"Selected state: '{state_val}'")
                    option_found = True
                    break
            
            if not option_found:
                error_msg = f"State '{state_val}' not found in dropdown"
                logger.error(error_msg)
                raise AssertionError(error_msg)
        
        # Fill zip
        zip_code = self.beneficial_zip
        zip_code.wait_for(state="visible", timeout=5000)
        zip_code.fill(beneficial_data.get("zip", "91803"))
        
        logger.info("Beneficial ownership details added successfully")

    def click_account_feature_button(self, step_name: str = "", log_message: str = ""):
        """Click account features button with TMS error handling and enhanced waits"""
        # Recover if page was closed
        try:
            if self.page.is_closed():
                pages = self.page.context.pages
                if pages and not pages[-1].is_closed():
                    self.page = pages[-1]
        except Exception:
            pass
        
        # Wait for page stability
        self._wait_for_page_ready(timeout=30000)
        logger.info("Waiting for page validations to complete...")
        
        btn = self._get_locator_by_selector("button.btn-next[data-url*='Feat_Page']").first
        fallback_selectors = [
            "a[data-url*='Feat_Page']",
            "a[href*='Feat_Page']",
            "button:has-text('Account Features')",
            "a:has-text('Account Features')",
            "button.btn-next[data-url*='Feat']",
            "a[data-url*='Feat']",
        ]

        url_before = self.page.url
        clicked = False
        try:
            self._click_button_with_fallback(btn, fallback_selectors, "Account Features", timeout=30000)
            clicked = True
        except RuntimeError:
            clicked = self._try_multiple_click_strategies(btn)

        if not clicked:
            self._log_button_debug_info()
            raise Exception("Could not find Account Features button with any selector")

        # Wait long enough for navigation to actually start before checking URL.
        # Without this pause the URL check fires before the browser has updated
        # page.url, causing a spurious second click that shakes the UI.
        self.page.wait_for_timeout(2000)

        try:
            if self.page.url == url_before:
                # Navigation hasn't started ΓÇö button may genuinely need a second click
                btn.wait_for(state="visible", timeout=5000)
                if btn.is_visible() and btn.is_enabled():
                    btn.click()
                    logger.info("Account Features button clicked again (navigation had not started)")
                    self.page.wait_for_timeout(2000)
        except Exception:
            logger.info("Button gone / navigation already in progress ΓÇö no second click needed")

        self._wait_for_page_ready(timeout=15000)

        # Handle TMS error if present
        self._handle_tms_error(btn)
    
    def _try_multiple_click_strategies(self, btn: Locator) -> bool:
        """Try multiple strategies to click the Account Features button"""
        # Strategy 1: Wait for button to become visible and enabled
        try:
            logger.info("Strategy 1: Waiting for button visibility...")
            if btn.count() > 0:
                btn.wait_for(state="visible", timeout=60000)
                if btn.is_enabled():
                    btn.click()
                    logger.info("Account Features button clicked (Strategy 1)")
                    return True
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {str(e).splitlines()[0]}")
        
        # Strategy 2: Find any visible btn-next button
        try:
            logger.info("Strategy 2: Looking for any btn-next button...")
            self.page.wait_for_timeout(2000)
            for idx, next_btn in enumerate(self._get_locator_by_selector("button.btn-next").all()):
                try:
                    if next_btn.is_visible() and next_btn.is_enabled():
                        next_btn.click()
                        logger.info(f"Clicked btn-next {idx} (Strategy 2)")
                        return True
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {str(e).splitlines()[0]}")
        
        # Strategy 3: Force click with JavaScript
        try:
            logger.warning("Strategy 3: Force clicking with JavaScript...")
            result = self.page.evaluate(
                """() => {
                    const btn = document.querySelector('button.btn-next[data-url*="Feat_Page"]');
                    if (btn) {
                        btn.style.display = 'block';
                        btn.style.visibility = 'visible';
                        btn.disabled = false;
                        btn.click();
                        return true;
                    }
                    return false;
                }"""
            )
            if result:
                logger.info("Force clicked via JavaScript (Strategy 3)")
                self.page.wait_for_timeout(2000)
                return True
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {str(e).splitlines()[0]}")
        
        return False
    
    def _log_button_debug_info(self) -> None:
        """Log button debug information for troubleshooting"""
        try:
            buttons = self._get_locator_by_selector("button").all()
            logger.warning(f"Total buttons on page: {len(buttons)}")
            for idx, btn_elem in enumerate(buttons[:15]):
                try:
                    text = btn_elem.text_content() or ""
                    data_url = btn_elem.get_attribute("data-url") or ""
                    visible = btn_elem.is_visible()
                    enabled = btn_elem.is_enabled()
                    logger.warning(
                        f"Btn {idx}: text='{text[:20]}', data-url='{data_url}', "
                        f"visible={visible}, enabled={enabled}"
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Debug logging failed: {str(e).splitlines()[0]}")
    
    def _handle_tms_error(self, btn: Locator) -> None:
        """Handle TMS error message if present"""
        try:
            error_msg = self.tax_management_error_msg
            info_label = self.tax_management_info_page_label
            
            if error_msg.count() > 0 and error_msg.first.is_visible(timeout=3000):
                if info_label.is_visible(timeout=3000):
                    logger.warning("TMS error detected, clicking Add Information link")
                    add_info = self.add_information_link
                    add_info.click()
                    
                    # Import and handle TMS
                    construct_page = ConstructPortfolioPage(self.page)
                    construct_page.choose_tms_tax_sensitivity()
                    
                    # Click account features button again
                    btn.click()
                    self.page.wait_for_load_state("domcontentloaded")
                    self.wait_for_loading_data()
        except Exception as e:
            logger.warning(f"TMS error handling failed: {str(e).splitlines()[0]}, continuing anyway")

    def click_online_document_delivery_button(self, step_name: str = "", log_message: str = ""):
        """Click Online Access & Document Delivery button (for scenarios without funding page like C72080)"""
        self._navigate_to_page(self.online_access_document_delivery_button, "Online Access & Document Delivery")
        # Extra wait for navigation
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)

    def click_tax_management_service_button(self, step_name: str = "", log_message: str = ""):
        """Click Tax Management Service button with fallback selectors"""
        self._wait_for_page_ready(timeout=20000)
        
        fallback_selectors = [
            "button:has-text('Tax Management Services')",
            "button:has-text('Tax Management Service')",
            "a:has-text('Tax Management Services')",
            "a:has-text('Tax Management Service')",
            "button[data-url*='Tax']",
            "a[data-url*='Tax']",
        ]
        
        try:
            self._click_button_with_fallback(
                self.tax_management_service_button, 
                fallback_selectors, 
                "Tax Management Service"
            )
            self._wait_for_page_ready()
        except RuntimeError:
            # TMS button not present - continue without failing
            logger.warning("TMS button not visible; continuing without clicking")

    def go_to_account_features_page(self, step_name: str = "", log_message: str = ""):
        """Navigate to account features page"""
        self._navigate_to_page(self.go_to_account_features_button, "Account Features")

    def go_to_funding_method_page(self, step_name: str = "", log_message: str = ""):
        """Navigate to funding method page"""
        # Extended wait for button to appear
        self.page.wait_for_timeout(5000)
        self._wait_for_page_ready(timeout=30000)
    #    self.page.wait_for_timeout(8000)
        
        fallback_selectors = [
            "a[data-url*='Fund_Page']",
            "a[href*='Fund_Page']",
            "button[data-url*='Fund_Page']",
            "button:has-text('Funding Method')",
            "button.btn-next",
            "a[data-url*='Fund'], button[data-url*='Fund']",
            "button[value*='Fund'], input[type='button'][value*='Fund']"
        ]
        
        self._click_button_with_fallback(
            self.go_to_funding_method_button,
            fallback_selectors,
            "Funding Method",
            timeout=30000
        )
        
        logger.info("Navigated to Funding Method page")
        self.page.wait_for_timeout(2000)
        self._wait_for_page_ready(timeout=30000)

    def enter_funding_method(self, funding_method: str) -> None:
        """Select funding method option on funding tab."""
        funding_data = (funding_method or "").split(",")
        if not funding_data or not funding_data[0]:
            logger.warning("Funding method value is empty; skipping selection")
            return

        try:
            self.check_funding.wait_for(state="visible", timeout=10000)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)

        # Check funding type - use JavaScript click for custom radio buttons
        if funding_data[0].strip() == "Check":
            self.check_funding.evaluate("el => el.click()")
            logger.info("Selected Check funding type")

        # Enclosed check - use JavaScript click
        if len(funding_data) > 2 and funding_data[2].strip() == "Enclosed Check":
            self.enclosed_check_tab.evaluate("el => el.click()")
            logger.info("Selected Enclosed Check")

    def review_all_accounts(self, step_name: str = "", log_message: str = ""):
        """Navigate to review all accounts page"""
        
        self._wait_for_page_ready(timeout=15000)
        
        review_btn = self.review_all_accounts_button
        review_btn.wait_for(state="visible", timeout=10000)
        review_btn.click()
        logger.info("Review All Accounts button clicked")
        
        
        self._wait_for_page_ready(timeout=15000)        
        # Click again if button still visible (sometimes needs double-click)
        try:
            if review_btn.is_visible(timeout=5000):
                review_btn.wait_for(state="visible", timeout=10000)
                review_btn.click()
                logger.info("Review All Accounts button clicked again")                
                self._wait_for_page_ready(timeout=15000)
        except Exception:
            logger.info("Button not visible - navigation successful")
        
        logger.info(log_message)
        # Return None since ReviewAllAccountsPage doesn't exist yet
        return None

    def add_ssn_tax_reporting(self, ssn: str):
        """Add SSN for tax reporting"""
        ssn_input = self.ssn_tax_reporting
        ssn_input.wait_for(state="visible", timeout=5000)
        ssn_input.fill(ssn)
        logger.info(f"SSN tax reporting has been entered: {ssn}")

    def verify_custodial_interview_page_list(self, client_type: str, custodian: str):
        """Verify custodial interview page list for donor advised funds"""
        if client_type.lower() == "donor advised fund":
            pages = self.subnav_links.all()
            page_names = [p.text_content().strip() for p in pages if p.text_content().strip()]
            
            custodian_lower = custodian.lower()
            if "assetmark" in custodian_lower:
                Assertions.assert_true("Account Features" in page_names, f"Expected 'Account Features' for custodian: {custodian}")
            elif any(c in custodian_lower for c in ["fidelity", "schwab", "pershing"]):
                Assertions.assert_true("Account Features" not in page_names, f"Should not have 'Account Features' for custodian: {custodian}")

    def verify_donor_page_text(self, client_type: str, custodian: str):
        """Verify donor page text for donor advised funds"""
        if client_type.lower() == "donor advised fund":
            page_name = self.custodial_interview_name.text_content()
            Assertions.assert_true("Donor" in page_name, "Expected 'Donor' in the page")
            
            donor_text = self.donor_page_text.text_content()
            expected = "Provide name and information for one Donor to be listed on the account"
            Assertions.assert_true(expected in donor_text, f"Expected '{expected}' in donor page text")

    def add_mother_maiden_name(self, client_type: str, custodian: str, reg_type: str, maiden_name: str):
        """Add mother's maiden name for Schwab accounts"""
        if custodian.lower() == "schwab" and "donor advised fund" not in client_type.lower():
            mother_input = self.mother_maiden_name
            mother_input.wait_for(state="visible", timeout=5000)
            mother_input.fill(maiden_name)
            logger.info(f"Mother's maiden name entered: {maiden_name}")

    def click_existing_account(
        self,
        custodian: str,
        reg_type: str,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        country_name: str
    ):
        """Click to add an existing account holder/trustee to the account"""
        logger.info("Clicking add holder button to select existing account")
        custodian_lower = (custodian or "").lower()
        reg_type_lower = (reg_type or "").lower()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        
        # Click add holder button (with fallback for Trustor/Trustee multi picker variants)
        add_holder = self.add_holder_button
        try:
            add_holder.wait_for(state="visible", timeout=3000)
        except Exception:
            logger.info("Primary add_holder locator not visible, trying fallback locator")
            add_holder = self.add_holder_button_fallback
            add_holder.wait_for(state="visible", timeout=10000)

        add_holder.first.scroll_into_view_if_needed()
        add_holder.first.click()
        self.page.wait_for_timeout(5000)  # Wait for popover to appear

        # Click existing account option - retry once if popover is slow to appear
        existing_option = self.existing_account_option.first
        try:
            existing_option.wait_for(state="visible", timeout=15000)
        except Exception:
            logger.info("Popover not visible, retrying add holder click")
            add_holder.first.click(force=True)
            self.page.wait_for_timeout(5000)  # Wait for popover to appear
            existing_option.wait_for(state="visible", timeout=15000)
        existing_option.click()
        logger.info("Selected existing account")
        
        # Handle Fidelity-specific individual relation selection
        if custodian and "fidelity" in custodian.lower():
            try:
                individual_relation = self.individual_relation_dropdown
                if individual_relation.is_visible(timeout=2000):
                    individual_relation.click()
                    logger.info("Selected individual relation for Fidelity")
            except Exception as e:
                logger.warning(f"Individual relation selection not needed or failed: {str(e).splitlines()[0]}")
        
        # Handle Pershing-specific country selection
        if is_pershing_roth_ira_trust:
            logger.info(f"Selecting country for Pershing: {country_name}")
            self._select_country_from_list(country_name, reg_type, custodian)
        
        # Wait for any spinners to disappear
        self.wait_for_all_spinners_to_disappear()
        
        # Save the account
        save_btn = self.save_account_button
        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.click()
        logger.info("Clicked save button for existing account")
        
        # Wait for save to complete
        self.wait_for_all_spinners_to_disappear()

    def _select_country_from_list(self, country_name: str, reg_type: str, custodian: str):
        """Helper method to select country from dropdown list"""
        custodian_lower = (custodian or "").lower()
        reg_type_lower = (reg_type or "").lower()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        try:
            # Click country dropdown
            country_dropdown = self.country_dropdown
            country_dropdown.wait_for(state="visible", timeout=5000)
            country_dropdown.click()
            logger.info(f"Opened country dropdown")
            
            # Select the country from the list
            country_options = self.country_list
            country_options.first.wait_for(state="visible", timeout=5000)
            
            # Find and click the matching country option
            all_options = country_options.all()
            for option in all_options:
                option_text = option.text_content().strip()
                if option_text.lower() == country_name.lower():
                    option.click()
                    logger.info(f"Selected country: {country_name}")
                    break
            else:
                logger.warning(f"Country '{country_name}' not found in dropdown, using first option")
                country_options.first.click()
        except Exception as e:
            logger.warning(f"Failed to select country: {str(e).splitlines()[0]}")

    # ========== TRUST INFORMATION METHODS (from Java reference) ==========
    
    def select_trusts_needed_to_give_authorizations(self, trust_needed_type: str, reg_type: str, custodian: str):
        """Select trust needed to give authorization instructions (AssetMark Trust only)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        
        if "assetmark trust" in custodian_lower and (
            reg_type_lower == "trust" or "401" in reg_type_lower or "roth ira trust" in reg_type_lower
        ):
            try:
                self.select_option_from_list(
                    self.trust_needed_authorization_dropdown,
                    self.trust_needed_authorization_options,
                    trust_needed_type,
                    f"Selected Trust Needed Authorization Type: {trust_needed_type}"
                )
                logger.info(f"Selected trust authorization type: {trust_needed_type}")
            except Exception as e:
                logger.warning(f"Failed to select trust authorization: {str(e).splitlines()[0]}")
    
    def enter_date_of_trust(self, date: str, reg_type: str, custodian: str):
        """Enter date of trust (AssetMark Trust, Fidelity, or Pershing)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        
        try:
            should_enter = False
            
            # AssetMark Trust conditions
            if "assetmark trust" in custodian_lower and (reg_type_lower == "trust" or "roth ira trust" in reg_type_lower):
                should_enter = True
            
            # Fidelity conditions
            elif "fidelity" in custodian_lower and reg_type_lower == "trust":
                should_enter = True
            
            # Pershing conditions
            elif "pershing" in custodian_lower and "roth ira trust" in reg_type_lower:
                should_enter = True
            
            if should_enter:
                # Convert date to string (datetime objects from Excel need string conversion)
                from datetime import datetime
                date_value = ""
                if date:
                    if isinstance(date, datetime):
                        date_value = date.strftime("%m%d%Y")
                    else:
                        date_value = str(date).strip()
                        # Zero-pad if needed (e.g. 1012020 -> 01012020)
                        if date_value.isdigit() and len(date_value) == 7:
                            date_value = "0" + date_value

                date_input = self.date_of_trust.first
                if not date_input.is_visible(timeout=2000):
                    date_input = self.form_root.locator(
                        "input[id*='Info_Trust_Date']:visible, "
                        "input[name*='Info_Trust_Date']:visible"
                    ).first

                date_input.wait_for(state="visible", timeout=5000)
                date_input.fill(date_value)
                date_input.blur()
                logger.info(f"Entered date of trust: {date_value}")
        
        except Exception as e:
            logger.warning(f"Failed to enter date of trust: {str(e).splitlines()[0]}")
    
    def select_type_trust(self, type_of_trust: str, reg_type: str, custodian: str):
        """Select type of trust (Fidelity, AssetMark Trust, Pershing Roth IRA Trust)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        
        try:
            self.page.wait_for_load_state("domcontentloaded")
            self.wait_for_loading_data()
            
            # Fidelity - select revocable radio
            if "fidelity" in custodian_lower and reg_type_lower == "trust":
                revocable_radio = self.trust_revocable_radio
                revocable_radio.wait_for(state="visible", timeout=30000)
                revocable_radio.click()
                logger.info("Selected trust type as Revocable (Fidelity)")
            
            # AssetMark Trust - select from dropdown
            elif "assetmark trust" in custodian_lower and (
                reg_type_lower == "trust" or "roth ira trust" in reg_type_lower
            ):
                self.select_option_from_list(
                    self.type_of_trust_dropdown,
                    self.list_of_trust_types,
                    type_of_trust,
                    f"Selected Type of Trust: {type_of_trust}"
                )
                logger.info(f"Selected trust type: {type_of_trust}")

            # Pershing Roth IRA Trust - select from dropdown
            elif "pershing" in custodian_lower and "roth ira trust" in reg_type_lower:
                try:
                    prs_trigger = self.form_root.locator("#Info_Trust_Addl_Dist_id > .firstmenu > a").first
                    prs_trigger.wait_for(state="visible", timeout=4000)
                    prs_trigger.click()
                    self.page.wait_for_timeout(300)

                    requested = " ".join(type_of_trust.split()).lower()
                    prs_options = self.form_root.locator("#Info_Trust_Addl_Dist_id dd a")
                    selected_prs = False
                    for option in prs_options.all():
                        option_text = " ".join((option.text_content() or "").split()).lower()
                        if requested == option_text or requested in option_text or option_text in requested:
                            option.click()
                            selected_prs = True
                            break

                    if not selected_prs:
                        self.page.get_by_text(type_of_trust, exact=False).first.click(timeout=3000)

                    logger.info(f"Selected trust type (Pershing explicit Playwright): {type_of_trust}")
                except Exception:
                    try:
                        self.select_option_from_list(
                            self.type_of_trust_dropdown,
                            self.list_of_trust_types,
                            type_of_trust,
                            f"Selected Type of Trust: {type_of_trust}"
                        )
                        logger.info(f"Selected trust type (Pershing): {type_of_trust}")
                    except Exception:
                        trigger = self.form_root.locator(
                            "#Info_Trust_Type_id dt > a, "
                            "[id*='Trust_Type_id'] dt > a, "
                            "#Info_Trust_Addl_Dist_id dt > a, "
                            "[id*='Trust_Addl_Dist_id'] dt > a"
                        ).first
                        options = self.form_root.locator(
                            "#Info_Trust_Type_id dd dl dd a, "
                            "[id*='Trust_Type_id'] dd dl dd a, "
                            "#Info_Trust_Addl_Dist_id dd dl dd a, "
                            "[id*='Trust_Addl_Dist_id'] dd dl dd a"
                        )
                        trigger.wait_for(state="visible", timeout=5000)
                        trigger.click()
                        self.page.wait_for_timeout(400)

                        requested = " ".join(type_of_trust.split()).lower()
                        selected = False
                        for option in options.all():
                            option_text = " ".join((option.text_content() or "").split()).lower()
                            if requested == option_text or requested in option_text or option_text in requested:
                                option.click()
                                selected = True
                                break

                        if not selected:
                            self.form_root.locator(
                                "#Info_Trust_Type_id dd a:has-text('" + type_of_trust + "'), "
                                "[id*='Trust_Type_id'] dd a:has-text('" + type_of_trust + "'), "
                                "#Info_Trust_Addl_Dist_id dd a:has-text('" + type_of_trust + "'), "
                                "[id*='Trust_Addl_Dist_id'] dd a:has-text('" + type_of_trust + "')"
                            ).first.click(timeout=3000)

                        logger.info(f"Selected trust type (Pershing fallback): {type_of_trust}")
        
        except Exception as e:
            logger.warning(f"Failed to select trust type: {str(e).splitlines()[0]}")
    
    def enter_plan_established_on(self, plan_date: str, reg_type: str, custodian: str):
        """Enter plan established date (AssetMark Trust 401 accounts only)"""
        custodian_lower = custodian.lower()
        
        if "assetmark trust" in custodian_lower and "401" in reg_type:
            try:
                plan_input = self.plan_established_on
                plan_input.wait_for(state="visible", timeout=30000)
                # Use JS to set value for date fields
                self.page.evaluate(
                    f"document.querySelector('#line_Questions_1__Info_Plan_Date').value = '{plan_date}'"
                )
                logger.info(f"Entered plan established date: {plan_date}")
            except Exception as e:
                logger.warning(f"Failed to enter plan established date: {str(e).splitlines()[0]}")
    
    def enter_decedent_name(self, first_name: str, last_name: str, reg_type: str, custodian: str):
        """Enter decedent name (AssetMark Roth IRA Trust/Individual only)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        
        if "assetmark trust" in custodian_lower and (
            "roth ira trust" in reg_type_lower or "roth ira individual" in reg_type_lower
        ):
            try:
                # First name
                dec_fname = self.decedent_first_name
                dec_fname.wait_for(state="visible", timeout=30000)
                self.page.evaluate(
                    f"document.querySelector('#line_Questions_0__Info_Dec_Name_First').value = '{first_name}'"
                )
                logger.info(f"Entered decedent first name: {first_name}")
                
                # Last name
                dec_lname = self.decedent_last_name
                dec_lname.wait_for(state="visible", timeout=30000)
                self.page.evaluate(
                    f"document.querySelector('#line_Questions_2__Info_Dec_Name_Last').value = '{last_name}'"
                )
                logger.info(f"Entered decedent last name: {last_name}")
            
            except Exception as e:
                logger.warning(f"Failed to enter decedent name: {str(e).splitlines()[0]}")
    
    def set_ipg_financial_advisor_authorization(self, fa_auth_level: str, channel: str):
        """Set IPG Financial Advisor Authorization level (IPG channel only)"""
        if channel.upper() != "IPG":
            return
        
        try:
            # Verify Full is selected by default
            full_radio = self.ipg_fa_auth_full
            full_class = full_radio.get_attribute("class")
            
            if full_class and "checked" in full_class:
                logger.info("FA Authorization default: Full radio is selected")
            
            # Set FA authorization level based on input
            if fa_auth_level.lower() == "none":
                none_radio = self.ipg_fa_auth_none
                none_radio.wait_for(state="visible", timeout=3000)
                none_radio.click()
                logger.info("Selected FA Authorization Level as None")
            
            elif fa_auth_level.lower() == "partial":
                partial_radio = self.ipg_fa_auth_partial
                partial_radio.wait_for(state="visible", timeout=3000)
                partial_radio.click()
                logger.info("Selected FA Authorization Level as Partial")
            
            else:
                logger.info("Full FA Authorization level is already selected by default")
            
            # Capture screenshot with highlight
            try:
                if self.fa_section.is_visible():
                    self.page.screenshot(
                        path=f"reports/screenshots/ipg_fa_authorization_{fa_auth_level}.png"
                    )
            except:
                pass
        
        except Exception as e:
            logger.warning(f"Failed to set IPG FA authorization: {str(e).splitlines()[0]}")

    def select_state(self, state_type: str, reg_type: str, custodian: str):
        """Select state dropdown on info page (Fidelity Trust, Pershing Roth IRA Trust)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        is_fidelity_trust = "fidelity" in custodian_lower and reg_type_lower == "trust"
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower

        if is_fidelity_trust or is_pershing_roth_ira_trust:
            try:
                # Use the broad XPath-based locators which work for both Pershing Trust and Fidelity Trust
                state_trigger = self.info_page_state_dropdown
                if not state_trigger.is_visible(timeout=2000):
                    state_trigger = self.fidelity_trust_state_dropdown_fallback.first

                self.select_option_from_list(
                    state_trigger,
                    self.info_page_state_list,
                    state_type,
                    f"Selected State: {state_type}"
                )
                logger.info(f"Successfully selected state: {state_type}")
            except Exception as e:
                logger.warning(f"Failed to select state: {str(e).splitlines()[0]}")
    
    def add_info_page_ssn(self, ssn: str, reg_type: str, custodian: str):
        """Add SSN on info page (AssetMark Trust 401/Roth IRA Trust, Pershing Roth IRA Trust)"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        
        # Check if SSN entry is needed for this custodian/reg_type combination
        if (("assetmark trust" in custodian_lower and ("401" in reg_type or "roth ira trust" in reg_type_lower)) or
            ("pershing" in custodian_lower and "roth ira trust" in reg_type_lower)):
            
            try:
                # Wait for SSN field and enter value
                ssn_field = self.info_page_ssn
                ssn_field.wait_for(state="visible", timeout=5000)
                ssn_value = "" if ssn is None else str(ssn).strip()
                ssn_field.fill(ssn_value)
                logger.info(f"Entered info page SSN: {ssn_value}")
                
                # Click SSN label to trigger validation
                try:
                    ssn_label = self.ssn_label
                    if ssn_label.is_visible(timeout=2000):
                        ssn_label.click()
                except:
                    pass
                
                # Wait for loading to complete
                self.wait_for_loading_data()
                logger.info("Info page SSN has been entered")
            
            except Exception as e:
                logger.warning(f"Failed to add info page SSN: {str(e).splitlines()[0]}")
    
    def account_additional_info(self, reg_type: str, custodian: str, dec_fname: str, dec_lname: str,
                                state_id: str, source_of_income: str, type_of_trust: str, marital_status: str,
                                purpose_of_acc: str, state_name: str, sub_advisory_type: str, faa_payment_method: str):
        """Handle account additional info based on custodian and registration type"""
        custodian_lower = custodian.lower()
        reg_type_lower = reg_type.lower().strip()
        is_pershing_roth_ira_trust = "pershing" in custodian_lower and "roth ira trust" in reg_type_lower
        try:
            self.page.wait_for_load_state("domcontentloaded")
            self.wait_for_loading_data()
            # AssetMark Trust Roth IRA Individual
            if "assetmark trust" in custodian_lower and "roth ira individual" in reg_type_lower:
                self.enter_decedent_name(dec_fname, dec_lname, reg_type, custodian)
            
            # Schwab or Fidelity SDBA
            elif (("schwab" in custodian_lower or "fidelity" in custodian_lower) and
                  "self-directed brokerage account" in reg_type_lower):
                # Wait for page to fully load before accessing SDBA-specific fields
                logger.info("Processing SDBA (Self-Directed Brokerage Account) fields...")
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                self.wait_for_loading_data()
                self.page.wait_for_timeout(3000)  # Extra stabilization wait
                
                if "fidelity" in custodian_lower or "schwab" in custodian_lower:
                    # Click prior advisor change type if present
                    prior_advisor = self.prior_advisor_change_type
                    try:
                        if prior_advisor.count() > 0 and prior_advisor.first.is_visible(timeout=5000):
                            prior_advisor.first.click()
                            logger.info("Γ£ô Clicked prior advisor change type")
                            self.page.wait_for_timeout(500)
                    except Exception as e:
                        logger.warning(f"Prior advisor not visible or clickable: {str(e).splitlines()[0]}")
                    
                    # Enter retirement plan employer name if present
                    employer_name = self.retirement_plan_employer_name
                    try:
                        if employer_name.count() > 0 and employer_name.first.is_visible(timeout=5000):
                            employer_name.first.fill(f"{custodian}_emp_name")
                            logger.info(f"Γ£ô Entered retirement plan employer name: {custodian}_emp_name")
                            self.page.wait_for_timeout(500)
                    except Exception as e:
                        logger.warning(f"Employer name field not visible or fillable: {str(e).splitlines()[0]}")
                    
                    # Enter retirement plan account number if present
                    plan_acct = self.retirement_plan_account_number
                    try:
                        if plan_acct.count() > 0 and plan_acct.first.is_visible(timeout=5000):
                            plan_acct_number = str(int(time.time() * 1000))
                            plan_acct.first.fill(plan_acct_number)
                            logger.info(f"Γ£ô Entered retirement plan account number: {plan_acct_number}")
                            self.page.wait_for_timeout(500)
                    except Exception as e:
                        logger.warning(f"Plan account field not visible or fillable: {str(e).splitlines()[0]}")
                    
                    # Enter investment account number if present - CRITICAL FOR SDBA ACCOUNTS
                    logger.info("Attempting to fill investment account number field...")
                    inv_acct = self.investment_account_number
                    
                    # Check if field exists and is findable
                    field_count = inv_acct.count()
                    logger.info(f"Investment account number field count: {field_count}")
                    
                    if field_count > 0:
                        try:
                            # Wait longer for field to be visible (15 seconds for SDBA)
                            inv_acct.first.wait_for(state="visible", timeout=15000)
                            logger.info("Γ£ô Investment account number field is visible")
                            
                            # Generate 11-digit number starting with 2-9
                            first_digit = random.randint(2, 9)
                            remaining_digits = random.randint(10000000000, 99999999999)  # 10 digits
                            account_number = str(first_digit) + str(remaining_digits)[:10]  # Total 11 digits
                            
                            logger.info(f"Γ£ô Entering investment account number: {account_number}")
                            
                            # Clear and fill the field
                            inv_acct.first.clear()
                            self.page.wait_for_timeout(500)
                            inv_acct.first.fill(account_number)
                            logger.info(f"Γ£ô Investment account number entered successfully: {account_number}")
                            
                            # Wait for field stabilization and blur event processing
                            self.page.wait_for_timeout(1500)
                            inv_acct.first.blur()
                            logger.info("Γ£ô Field blurred for validation")
                            
                            # Wait 5 seconds after entering as required per original spec
                            logger.info("Γ£ô Waiting 5 seconds after entering investment account number...")
                            self.page.wait_for_timeout(5000)
                            
                            # Final wait for page stability
                            self.wait_for_loading_data()
                            self.page.wait_for_timeout(3000)  # Increased from 2000 to 3000
                            logger.info("Γ£ô SDBA investment account number completely filled and verified")
                        except Exception as e:
                            logger.error(f"Failed to fill investment account number: {str(e).splitlines()[0]}", exc_info=True)
                            raise
                    else:
                        logger.warning(f"Investment account number field not found (count: 0) - may not be required for this SDBA variant")
            
            # Fidelity Direct or Schwab Direct
            elif (("fidelity direct" in custodian_lower or "schwab direct" in custodian_lower) and
                  (any(x in reg_type_lower for x in ["self-directed brokerage account", "individual", "trust", 
                                                      "traditional ira", "roth ira individual"]))):
                logger.info("Processing Fidelity/Schwab Direct investment account number...")
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                self.wait_for_loading_data()
                self.page.wait_for_timeout(2000)  # Extra stabilization wait
                
                inv_acct = self.investment_account_number
                if inv_acct.count() > 0 and inv_acct.first.is_visible(timeout=10000):
                    # Generate 11-digit number starting with 2-9
                    first_digit = random.randint(2, 9)
                    remaining_digits = random.randint(10000000000, 99999999999)  # 10 digits
                    account_number = str(first_digit) + str(remaining_digits)[:10]  # Total 11 digits
                    
                    logger.info(f"Γ£ô Entering investment account number for Direct custodian: {account_number}")
                    
                    # Clear and fill the field
                    inv_acct.first.clear()
                    self.page.wait_for_timeout(500)
                    inv_acct.first.fill(generate_random_number(9))
                    logger.info(f"Γ£ô Investment account number entered: {account_number}")
                    
                    # Wait for field stabilization and blur event processing
                    self.page.wait_for_timeout(1000)
                    inv_acct.first.blur()
                    
                    # Wait 5 seconds after entering as required
                    logger.info("Γ£ô Waiting 5 seconds after entering investment account number...")
                    self.page.wait_for_timeout(5000)
                    
                    # Final wait for page stability
                    self.wait_for_loading_data()
                    self.page.wait_for_timeout(2000)
                else:
                    logger.warning(f"Investment account number field not visible for Direct custodian")
            
            # Pershing Individual
            elif "pershing" in custodian_lower and reg_type_lower == "individual":
                # Click NetX investor access
                netx_access = self.can_provide_netx_investor_access
                if netx_access.is_visible(timeout=5000):
                    netx_access.click()
                    logger.info("Clicked NetX investor access")
                
                # Click trusted contact
                trusted = self.trusted_contact
                if trusted.is_visible(timeout=5000):
                    trusted.click()
                    logger.info("Clicked trusted contact")
                
                # Click share PRS address
                share_addr = self.can_share_prs_address
                if share_addr.is_visible(timeout=5000):
                    share_addr.click()
                    logger.info("Clicked share PRS address")
                
                # Select marital status if visible
                if marital_status:
                    try:
                        self.select_option_from_list(
                            self.client_marital_status_dropdown,
                            self.client_marital_list,
                            marital_status,
                            f"Selected Marital Status: {marital_status}"
                        )
                    except:
                        pass
                
                # Select source of funds using new helper method
                if source_of_income:
                    self._select_source_of_funds(source_of_income)

            # Pershing Roth IRA Trust
            elif "pershing" in custodian_lower and "roth ira trust" in reg_type_lower:
                if state_id:
                    try:
                        self.select_state(state_id, reg_type, custodian)
                    except Exception as e:
                        logger.warning(f"Failed to select state for Pershing Roth IRA Trust: {str(e).splitlines()[0]}")

                try:
                    if self.trust_revocable_radio.count() > 0 and self.trust_revocable_radio.first.is_visible(timeout=3000):
                        self.trust_revocable_radio.first.click()
                        logger.info("Clicked isTrustRevocableRadio")
                except Exception as e:
                    logger.warning(f"Failed clicking isTrustRevocableRadio: {str(e).splitlines()[0]}")

                try:
                    if self.trust_nature_input.count() > 0 and self.trust_nature_input.first.is_visible(timeout=3000):
                        self.trust_nature_input.first.fill("Testing")
                        logger.info("Filled trustNature")
                except Exception as e:
                    logger.warning(f"Failed filling trustNature: {str(e).splitlines()[0]}")

                try:
                    if self.last_amendment_input.count() > 0 and self.last_amendment_input.first.is_visible(timeout=3000):
                        self.last_amendment_input.first.fill("01012025")
                        logger.info("Filled lastAmendment")
                except Exception as e:
                    logger.warning(f"Failed filling lastAmendment: {str(e).splitlines()[0]}")

                trust_clicks = [
                    (self.trustees_natural_persons_no, "areTrusteesNaturalPersons"),
                    (self.beneficiaries_natural_persons_no, "allBeneficiariesNatural"),
                    (self.trust_legally_compliant_no, "isTrustLegallyCompliant"),
                    (self.trustees_act_independently, "trusteesActIndependently"),
                    (self.trust_cdd_exempt_no, "isCDDExempt"),
                    (self.trust_offshore_no, "isCustAnOffshoreTrust"),
                    (self.trust_cash_asset_mgmt_allowed_no, "isCashOrAssetMgmtAllowed"),
                    (self.trust_allow_poa_no, "allowPowerOfAttorney"),
                    (self.trust_allow_option_trading_no, "allowOptionTrading"),
                    (self.ira_account_funded_no, "isAccountFunded"),
                    (self.beneficiary_relationship_spouse, "beneficiaryRelationship"),
                    (self.can_provide_netx_investor_access, "canProvidePrsNeXInvestorAccess"),
                    (self.trusted_contact, "trustedContact"),
                    (self.can_share_prs_address, "canSharePRSAddress"),
                ]

                for locator, field_name in trust_clicks:
                    try:
                        if locator.count() > 0 and locator.first.is_visible(timeout=3000):
                            locator.first.click()
                            logger.info(f"Clicked {field_name}")
                    except Exception as e:
                        logger.warning(f"Failed clicking {field_name}: {str(e).splitlines()[0]}")

                trust_fills = [
                    (self.ira_decedent_name_input, "babu", "iraDeceName"),
                    (self.ira_decedent_dob_input, "01011950", "iraDecBday"),
                    (self.ira_decedent_dod_input, "01012023", "iraDecDday"),
                ]

                for locator, value, field_name in trust_fills:
                    try:
                        if locator.count() > 0 and locator.first.is_visible(timeout=3000):
                            locator.first.fill(value)
                            logger.info(f"Filled {field_name}")
                    except Exception as e:
                        logger.warning(f"Failed filling {field_name}: {str(e).splitlines()[0]}")

                if source_of_income:
                    source_selected = self._select_source_of_funds(source_of_income)

            # Schwab Traditional IRA
            elif ("schwab" in custodian_lower and ("traditional ira" in reg_type_lower or "simple ira" in reg_type_lower)):
                logger.info(f"Processing Schwab {reg_type} - clicking required fields...")
                self.wait_for_loading_data()
                existing_plan= 'No'
                if "simple ira" in reg_type_lower:
                    if existing_plan == 'Yes':
                        self.form_root.locator("#line_Questions_0__Info_Simple_Emp_Y_tab").first.click(force=True)
                        logger.info("Clicked Yes for existing Simple IRA plan")
                        self.form_root.locator("#line_Questions_0__Info_Simple_Emp_ID").first.fill(generate_random_number(9))
                        self.form_root.locator("#line_Questions_0__Info_Simple_Emp_Bus_Nm").first.fill(random_alpha(9))
                    else:
                        self.form_root.locator("#line_Questions_0__Info_Simple_Emp_N_tab").first.click(force=True)
                    logger.info("Processing Schwab Simple IRA - clicking required fields...")

                # Click all required tab elements directly (no scroll, no DOM settle waits)
                tab_elements = [
                    ("#Info_SWB_InformationSharing_Y", "Information Sharing - Yes"),
                    ("#Info_Bene_DesElect_PS", "Beneficiary Elections - Per Stirpes"),
                    ("#Info_Bene_Minor_None", "Minor Beneficiaries - None"),
                    ("#Info_AccountNumber_Retain_N", "Grant AssetMark authority - No"),
                ]

                for selector, label in tab_elements:
                    el = self.form_root.locator(selector)
                    if el.count() > 0 and el.first.is_visible(timeout=3000):
                        el.first.click(force=True)
                        logger.info(f"Clicked {label}")

                self.wait_for_loading_data()
                logger.info(f"Schwab {reg_type} account additional info completed")

            # Schwab Individual
            elif ("schwab" in custodian_lower) and reg_type_lower == "individual":
                # Click TDA share address (hidden-tab element ΓÇö use attached + JS click)
                tda_share = self.can_tda_share_address
                try:
                    tda_share.wait_for(state="attached", timeout=5000)
                    tda_share.evaluate("el => el.click()")
                    logger.info("Checked TDA share address")
                except Exception:
                    logger.warning("TDA share address element not found, skipping")
                
                self.page.wait_for_timeout(1000)
                
                # Select source of funds using new helper method
                if source_of_income:
                    self._select_source_of_funds(source_of_income)
                
                # Select purpose of account if visible
                if purpose_of_acc:
                    try:
                        self.select_option_from_list(
                            self.purpose_of_account_dropdown,
                            self.purpose_of_account_list,
                            purpose_of_acc,
                            f"Selected Purpose of Account: {purpose_of_acc}"
                        )
                    except:
                        pass

            
            
            # Fidelity Trust - Select state
            elif "fidelity" in custodian_lower and reg_type_lower == "trust":
                if state_id:
                    try:
                        # Use the dedicated select_state method which has fallback handling
                        self.select_state(state_id, reg_type, custodian)
                    except Exception as e:
                        logger.warning(f"Failed to select state for Fidelity Trust: {str(e).splitlines()[0]}")
            
            self.wait_for_loading_data()
            logger.info("Account additional info processing completed")
        
        except Exception as e:
            logger.warning(f"Error in account_additional_info: {str(e).splitlines()[0]}")

    # ---------- Related Billing / FAA Payment Methods ----------

    def select_faa_payment_method(self, method: str) -> None:
        """Select the FAA payment method from the dropdown."""
        logger.info(f"Selecting FAA payment method: {method}")
        self.page.wait_for_load_state("domcontentloaded")
        self.wait_for_loading_data()
        self.select_option_from_list(
            self.faa_payment_method_dropdown,
            self.faa_payment_method_options,
            method,
            f"Selected FAA payment method: {method}"
        )
        self.wait_for_loading_data()

    def get_billing_model_options(self) -> list[str]:
        """Return all visible model/account options in the billing dropdown."""
        logger.info("Retrieving billing model options from dropdown")
        self.billing_model_dropdown.wait_for(state="visible", timeout=10000)
        self.billing_model_dropdown.click()
        self.page.wait_for_timeout(1000)
        options = self.billing_model_options.all_text_contents()
        # Close dropdown by clicking trigger again
        self.billing_model_dropdown.click()
        cleaned = [opt.strip() for opt in options if opt.strip()]
        logger.info(f"Found {len(cleaned)} billing model options")
        return cleaned

    def is_model_in_billing_dropdown(self, model_name: str) -> bool:
        """Check if a specific model appears in the billing dropdown options."""
        logger.info(f"Checking if model '{model_name}' is in billing dropdown")
        options = self.get_billing_model_options()
        found = any(model_name.lower() in opt.lower() for opt in options)
        logger.info(f"Model '{model_name}' found: {found}")
        return found

    def select_billing_model(self, model_name: str) -> None:
        """Select a specific model from the billing model dropdown."""
        logger.info(f"Selecting billing model: {model_name}")
        self.select_option_from_list(
            self.billing_model_dropdown,
            self.billing_model_options,
            model_name,
            f"Selected billing model: {model_name}"
        )
        self.wait_for_loading_data()

    def is_billing_error_visible(self) -> bool:
        """Check if any billing-related error/validation is shown."""
        logger.info("Checking for billing error message")
        try:
            return self.billing_error_message.first.is_visible(timeout=3000)
        except Exception:
            return False

    def get_billing_model_option_count(self) -> int:
        """Return the count of visible billing model options without opening/closing the dropdown."""
        logger.info("Getting billing model option count")
        options = self.get_billing_model_options()
        return len(options)

    def get_investment_accounts_dropdown_text(self) -> str:
        """Return the currently selected text of the Investment Account(s) dropdown."""
        logger.info("Getting Investment Account(s) dropdown selected text")
        self.billing_model_dropdown.wait_for(state="visible", timeout=10000)
        text = self.billing_model_dropdown.text_content() or ""
        return text.strip()

    # ---------- Email Validation (PRODENG-28716) ----------
    def click_skip_button(self):
        """Click the skip button on the online access document delivery tab."""
        self.navigate_menu_option("Online Access & Document Delivery")
        logger.info("Clicking skip button on online access document delivery tab")
        try:
            self.skip_button.wait_for(state="visible", timeout=5000)
            self.skip_button.click()
            logger.info("Clicked skip button successfully")
        except Exception as e:
            logger.warning(f"Failed to click skip button: {str(e).splitlines()[0]}")

    def click_add_link(self):            
        """Click the 'Add' link to add an email on the online access document delivery tab."""
        logger.info("Clicking 'Add' link to add email on online access document delivery tab")
        try:
            add_link = self.form_root.get_by_text("Add", exact=True).first          
            add_link.click()
            logger.info("Clicked 'Add' link successfully")
        except Exception as e:
            logger.warning(f"Failed to click 'Add' link: {str(e).splitlines()[0]}")

    def fill_email_address_modal(self, email: str):
        """Validate the email address modal on the online access document delivery tab."""
        logger.info("Validating email address modal")
        try:
            Assertions.assert_true(self.email_input_modal.is_visible(timeout=5000), "Email address input modal should be visible")
            logger.info("Email address modal is visible")
        except Exception as e:
            logger.warning(f"Failed to validate email address modal: {str(e).splitlines()[0]}")
        
        email_value = "" if email is None else str(email).strip()
        self.email_input_modal.wait_for(state="visible", timeout=5000)
        self.fill(self.email_input_modal.first, email_value)
        logger.info(f"Filled email field with: {email_value}")

    def condition_to_retain_existing_account(self, test_context: dict, retainAccount: str) -> str | None:
        """Determine if existing account should be retained based on registration type and custodian."""
        should_retain = retainAccount.lower() == "yes"
        if should_retain:
            tab_id = "#line_Questions_0__Info_AccountNumber_Retain_Y_tab"
        else:
            tab_id = "#line_Questions_0__Info_AccountNumber_Retain_N_tab"
        
        retain_tab = self.form_root.locator(tab_id)
        retain_tab.wait_for(state="attached", timeout=10000)
        retain_tab.evaluate("el => el.click()")
        logger.info(
             f"Set retain existing account to '{retainAccount}' for Schwab Individual registration"
        )
        account = self.form_root.locator("#line_Questions_0__Info_Investment_AccountNumber_VALUE") 
        if should_retain:                
            # self.click_online_document_delivery_button()
            # border_color = account.evaluate("el => getComputedStyle(el).borderBottomColor")
            # Assertions.assert_true("rgb(237, 28, 36)" in border_color, f"Account field border bottom color should be red rgb(237, 28, 36), but was '{border_color}'")
            acct_number = str(random.randint(10**8, 10**9 - 1))
            self.fill(account, acct_number)
            self.tab_out(account)
            logger.info(f"Filled investment account number with: {acct_number}")
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.wait_for_loading_data()
            if test_context.get("test_data", {}).get("Custodian", "").lower() == "schwab":
            #    ia_firm_name = self.form_root.get_by_text(re.compile("current IA Firm that AssetMark"))
                alpha= random_alpha(10)
                self.fill(self.form_root.locator("#line_Questions_0__Info_AccountNumber_Retain_PriorIA_Firm"), alpha)
                logger.info(f"Filled IA firm name with: {alpha}")
                test_context["ia_firm_name"] = alpha
            # self.click(self.form_root.get_by_role("button", name="Save"), timeout=5000)
            # self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            # self.wait_for_loading_data()
            Assertions.assert_false(self.form_root.get_by_text("Account Features", exact=True).is_visible(), "Account Features should not be visible after saving")
            Assertions.assert_false(self.form_root.get_by_text("Funding Method", exact=True).is_visible(), "Funding Method should not be visible after saving")
            return acct_number
        else:            
            Assertions.assert_false(account.is_visible(), "Account field should not be visible when not retaining existing account")
            logger.info("Not retaining existing account, proceeding without entering account number")
         #   self.click_account_information_button()
            return None
    
    # ── 401(k) Participant / Retirement Plan Methods ──

    def fill_trustee_title(self, title: str = "Trustee"):
        """Fill Trustee Title field if visible (required for 401k trust accounts)."""
        try:
            if self.trustee_title_input.is_visible(timeout=3000):
                self.trustee_title_input.fill(title)
                logger.info(f"Filled Trustee Title: {title}")
        except Exception:
            logger.info("Trustee Title field not present, skipping")

    def click_participant_button(self, step_name: str = "", log_message: str = ""):
        """Click Participant button"""
        self.participant_button.scroll_into_view_if_needed(timeout=10000)
        self._click_element_with_strategies(self.participant_button, "Participant")
        self._wait_for_page_ready()

    def fill_participant_info(self, first_name: str, last_name: str, birth_date: str, ssn: str, participant_name: str = "", participant_type: str = "New Participant"):
        """Fill participant information for 401k accounts."""
        self.add_participant_button.wait_for(state="visible", timeout=10000)
        self.add_participant_button.click()
        logger.info("Clicked Add Participant button")
        self.page.wait_for_timeout(500)

        existing_visible = self.participant_existing_client.is_visible()
        add_new_visible = self.participant_add_new.is_visible()
        Assertions.assert_true(existing_visible and add_new_visible, "Both 'Existing Client' and 'Add New' options are available in participant popover")
        popover = self.form_root.locator(".popover.custom-popover")
        self.highlight_and_screenshot(popover, "Participant List", color="green", take_screenshot=True)

        if participant_type.lower() == "existing trustee":
            self.participant_existing_client.wait_for(state="visible", timeout=5000)
            self.participant_existing_client.click()
            logger.info("Selected existing client from participant popover")
            self.page.wait_for_timeout(500)

            if "bussiness" in participant_name.lower():
                self.participant_business_owner_radio.wait_for(state="visible", timeout=5000)
                self.participant_business_owner_radio.click(force=True)
                logger.info("Selected Business owner (trustee) radio button")
            elif "spouse" in participant_name.lower():
                self.participant_spouse_radio.wait_for(state="visible", timeout=5000)
                self.participant_spouse_radio.click(force=True)
                logger.info("Selected Spouse radio button")

            self.save_account_button.wait_for(state="visible", timeout=5000)
            self.save_account_button.click()
            logger.info("Clicked participant Save button (Existing Trustee)")
            self._wait_for_page_ready()
            self.notSavedError()
        else:
            self.participant_add_new.wait_for(state="visible", timeout=5000)
            self.participant_add_new.click()
            logger.info("Clicked participant Add New")
            self.page.wait_for_timeout(500)

            if "bussiness" in participant_name.lower():
                self.participant_business_owner_radio.wait_for(state="visible", timeout=5000)
                self.participant_business_owner_radio.click(force=True)
                logger.info("Selected Business owner (trustee) radio button")
            elif "spouse" in participant_name.lower():
                self.participant_spouse_radio.wait_for(state="visible", timeout=5000)
                self.participant_spouse_radio.click(force=True)
                logger.info("Selected Spouse radio button")

            self.participant_first_name.wait_for(state="visible", timeout=5000)
            self.participant_first_name.fill(first_name)

            self.participant_last_name.wait_for(state="visible", timeout=5000)
            self.participant_last_name.fill(last_name)

            self.participant_dob.wait_for(state="visible", timeout=5000)
            if birth_date is None:
                dob_value = "01011960"
            elif hasattr(birth_date, "strftime"):
                dob_value = birth_date.strftime("%m%d%Y")
            else:
                dob_value = str(birth_date).strip()
            digits_only = "".join(ch for ch in dob_value if ch.isdigit())
            if len(digits_only) == 8:
                dob_value = digits_only
            if len(dob_value) <= 7:
                dob_value = "01011960"
            self.participant_dob.fill(dob_value)

            self.participant_ssn.wait_for(state="visible", timeout=5000)
            ssn_value = "" if ssn is None else str(ssn).strip()
            self.participant_ssn.fill(ssn_value)

            self.save_account_button.wait_for(state="visible", timeout=5000)
            self.save_account_button.click()
            logger.info("Clicked participant Save button")
            self._wait_for_page_ready()
            self.notSavedError()

    def click_retirement_plan_info_button(self, step_name: str = "", log_message: str = ""):
        """Click Retirement Plan Information button"""
        self._navigate_to_page(self.retirement_plan_info_button, "Retirement Plan Information")

    def trim_full_legal_title(self, max_length: int = 25) -> None:
        """Navigate to Account Information page and trim Full Legal Title if it exceeds 30 chars."""
        self.click_account_information_button(
            "Account Information button: ",
            "Navigating to Account Information to check Full Legal Title"
        )
        try:
            self.full_legal_title.wait_for(state="visible", timeout=10000)
            current_value = self.full_legal_title.input_value(timeout=5000)
            if len(current_value) > 30:
                trimmed = current_value[:max_length]
                self.full_legal_title.clear()
                self.full_legal_title.fill(trimmed)
                logger.info(f"Full Legal Title trimmed from {len(current_value)} to {len(trimmed)} chars: '{trimmed}'")
            else:
                logger.info(f"Full Legal Title is {len(current_value)} chars - no trim needed")
        except Exception as e:
            logger.warning(f"Full Legal Title field not found or not visible: {e}")

    def validate_irs_plan_document_section(self, reg_type: str, custodian: str):
        """Validate IRS Plan Document section for 401(k)."""
        if "401" in reg_type and "assetmark trust" in custodian.lower():
            self.irs_plan_document_section.wait_for(state="visible", timeout=15000)
            radio_count = self.irs_plan_document_radios.count()
            Assertions.assert_equal(radio_count, 5, f"Expected 5 IRS Plan Document radio options, found {radio_count}")
            logger.info(f"Validated Retirement Plan Info page - IRS Plan Document section with {radio_count} radio options")
            self.highlight_and_screenshot(self.irs_plan_document_section, "IRS Plan Document Section", color="green", take_screenshot=True)

            self.irs_plan_document_info_label.wait_for(state="visible", timeout=10000)
            label_text = self.irs_plan_document_info_label.text_content().strip()
            expected_text = "Individual 401(k) requires a plan document per Internal Revenue Code Section 401(a)"
            Assertions.assert_true(expected_text in label_text, "IRS Plan Document info label contains expected text")
            bg_color = self.irs_plan_document_info_label.evaluate("el => getComputedStyle(el).backgroundColor")
            Assertions.assert_true(bg_color in ["rgb(255, 255, 193)", "#ffffc1"], f"IRS Plan Document info label background color is yellow, actual: {bg_color}")
            logger.info(f"Validated IRS Plan Document info label - text and background color ({bg_color})")

    IRS_PLAN_OPTION_MAP = {
        "option 2": "yes - with another outside third party administrator, but converting to epic retirement services",
        "option 5": "no - i would like to establish the plan with an outside third party administrator (unbundled)",
    }

    def select_irs_plan_document_type(self, irs_plan_docu_type: str, epic_email: str = ""):
        """Select IRS Plan Document radio based on IRSPlanDocuType from feature file."""
        if not irs_plan_docu_type:
            logger.info("No IRSPlanDocuType provided, skipping IRS plan document selection")
            return

        irs_normalized = " ".join(irs_plan_docu_type.split()).lower()
        irs_normalized = self.IRS_PLAN_OPTION_MAP.get(irs_normalized, irs_normalized)

        no_outside_tpa = "no - i would like to establish the plan with an outside third party administrator (unbundled)"
        yes_converting = "yes - with another outside third party administrator, but converting to epic retirement services"
        if irs_normalized == no_outside_tpa:
            self.irs_plan_document_no.wait_for(state="attached", timeout=5000)
            self.irs_plan_document_no.evaluate("el => el.click()")
            logger.info("Selected IRS Plan Document: No - outside TPA (unbundled)")
        elif irs_normalized == yes_converting:
            self._fill_irs_yes_bundled_fields(epic_email)
        else:
            logger.warning(f"Unknown IRSPlanDocuType: '{irs_plan_docu_type}', no radio selected")

    def _fill_irs_yes_bundled_fields(self, epic_email: str = ""):
        """Fill all fields for Yes - Converting to EPIC option."""
        self.irs_plan_document_yes_convert.wait_for(state="attached", timeout=5000)
        self.irs_plan_document_yes_convert.evaluate("el => el.click()")
        logger.info("Clicked Yes - Converting to EPIC radio")
        self.page.wait_for_timeout(1000)

        self.plan_sponsor_name_input.wait_for(state="visible", timeout=5000)
        self.plan_sponsor_name_input.fill("testing")

        self.full_legal_name_input.wait_for(state="visible", timeout=5000)
        self.full_legal_name_input.fill("_401k_test")

        self.plan_amended_restated_input.wait_for(state="visible", timeout=5000)
        self.plan_amended_restated_input.fill("TestPlan")

        self.plan_effective_date_input.wait_for(state="visible", timeout=5000)
        self.plan_effective_date_input.fill("01012020")

        self.select_option_from_list(
            self.business_type_dropdown_trigger,
            self.business_type_options,
            "C-Corporation",
            "Business Type"
        )

        self.select_option_from_list(
            self.year_end_dropdown_trigger,
            self.year_end_options,
            "January 31",
            "Year End"
        )

        if epic_email:
            self.epic_email_input.wait_for(state="visible", timeout=5000)
            self.epic_email_input.fill(epic_email)

        self.add_new_bank_link.wait_for(state="visible", timeout=5000)
        self.add_new_bank_link.click()
        logger.info("Clicked Add New Bank link")

        self.bank_modal.wait_for(state="visible", timeout=10000)
        self.page.wait_for_timeout(500)

        self.bank_routing_input.wait_for(state="visible", timeout=5000)
        self.bank_routing_input.fill("026009593")
        self.tab_out(self.bank_routing_input)
        self.page.wait_for_timeout(2000)

        routing_error_visible = self.bank_routing_error.is_visible()
        Assertions.assert_false(routing_error_visible, "Entered ABA routing number is valid")

        self.bank_name_modal_input.wait_for(state="visible", timeout=5000)
        bank_name_value = self.bank_name_modal_input.input_value()
        Assertions.assert_equal(bank_name_value, "Bank of America, NA", f"Bank Name auto-filled correctly: {bank_name_value}")

        self.bank_account_number_input.wait_for(state="visible", timeout=5000)
        self.bank_account_number_input.fill("3464363465634634634")

        self.bank_name_on_account_input.wait_for(state="visible", timeout=5000)
        self.bank_name_on_account_input.fill("venkateshbabu")

        self.bank_modal_save_button.wait_for(state="visible", timeout=5000)
        self.bank_modal_save_button.click()
        self.page.wait_for_timeout(2000)

        self.notSavedError()
        logger.info("Completed IRS Plan Document: Yes - bundled (all fields filled including bank)")

    def notSavedError(self, timeout: int = 5000) -> None:
        """Check for save-error banner; fail if visible, pass silently if absent."""
        error_banner = self.not_saved_error_locator
        try:
            error_banner.wait_for(state="visible", timeout=timeout)
            error_text = error_banner.text_content() or "The information above has NOT been saved."
            Assertions.fail(f"ERROR: {error_text.strip()} - Data was not saved successfully! URL: {self.page.url}")
        except AssertionError:
            raise
        except Exception:
            Assertions.assert_true(True, "Account Information details saved successfully")


    def uniqueFeatureFileSolution(self) :
        # acc_features = self.page.get_by_text("Account Features", exact=True)
        # acc_features.wait_for(state="visible", timeout=30000)
        # acc_features.click()
        current_segment=" "
        segments_added = []
        logger.info("Clicked Account Features link")
        # Get ALL plus icons in DOM (not just visible) — they persist after save even if hidden
        all_icons = self.page.locator(".plus-button-sign").all()
        total_icons = len(all_icons)
        logger.info(f"Total plus icons in DOM: {total_icons}")
        for i in range(total_icons):
            plus_icon = all_icons[i]
            self.page.wait_for_timeout(500)
            # JS click bypasses visibility — works even if section collapsed after save
            plus_icon.dispatch_event("click")
            logger.info(f"Clicked plus icon {i+1}/{total_icons}")
            self.page.wait_for_timeout(500)
            current_segment = plus_icon.evaluate("""el => {
                const row = el.closest('.row');
                if (row) {
                    const label = row.querySelector('.label-big');
                    if (label) return label.innerText.trim();
                }
                return 'unknown';
            }""")
            logger.info(f"segment label is {current_segment}")
            segments_added.append(current_segment)
            add_information = self.page.locator("a:visible, span:visible, li:visible").filter(has_text="Add Information").first
            try:
                add_information.wait_for(state="attached", timeout=3000)
                logger.info("Add Information link is visible")
                add_information.click()
                logger.info("Clicked Add Information link")
                
            #    self.wait_for_spinner_to_disappear()
                self._fill_all_fields()                 
                # bank link handling
                self._manage_bank_link()
                self._manage_add_address()
            except Exception:
                logger.info(f"No visible 'Add Information' link after clicking plus icon {i+1}, skipping")
                continue            
            logger.info("Clicked Save button after filling fields")            
            self.page.get_by_role("button", name="Save").first.click()
            # Wait for page to stabilize after save before next iteration            
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
        logger.info(f"All segments added: {segments_added}")

    def _get_all_checkboxes_checked(self):
        """Helper method to return all checkbox locators on the page.""" 
        native_checkboxes = self.page.locator(
            "input[type='checkbox'], input[class*='radio-tab'], input[class*='checkbox-tab']"
        ).all()
        for cb in native_checkboxes:
            try:
                cb_class = cb.get_attribute("class") or ""
                cb_type = cb.get_attribute("type") or ""

                if "hidden-tab" in cb_class:
                    cb.wait_for(state="attached", timeout=500)
                    # Only interact if the element is visible and enabled (active)
                    if not cb.is_visible() or not cb.is_enabled():
                        continue
                   
                    clicked = cb.evaluate("""el => {
                        const span = el.nextElementSibling;
                        if (span && span.tagName === 'SPAN' && !span.classList.contains('checked')) {
                            span.click();
                            return 'span';
                        }
                        if (el.parentElement) {
                            el.parentElement.click();
                            return 'parent';
                        }
                        return 'none';
                    }""")
                    if clicked != 'none':
                        logger.info(f"Hidden-tab element: clicked via {clicked}")
                elif cb_type == "checkbox" and cb.is_visible() and cb.is_enabled() and not cb.is_checked():
                    cb.check()
                    logger.info(f"Checked visible checkbox")
            except Exception:
                continue

        # Custom checkbox widgets
        custom_checkboxes = self.page.locator(
            "[data-questiontype='checkbox'] span.toggle-checkbox:not(.checked)"
        ).all()
        for idx, cb in enumerate(custom_checkboxes):
            try:
                cb.evaluate("el => el.click()")
                logger.info(f"clicked on custom checkbox {idx+1}/{len(custom_checkboxes)}")
            except Exception:
                continue

    def _get_all_dropdown_selected(self, option_index: int = 1) :
        
        acted = 0

        # --- Native <select> elements ---
        selects = self.page.locator("select:visible")
        select_count = selects.count()
        for i in range(select_count):
            dropdown = selects.nth(i)
            try:
                if not dropdown.is_enabled():
                    continue
                options_count = dropdown.locator("option").count()
                if options_count == 0:
                    continue
                target_index = option_index if option_index < options_count else options_count - 1
                dropdown.select_option(index=target_index)
                acted += 1
            except Exception:
                continue

        # --- Custom styled dropdowns (dt > a trigger + dd > dl > dd > a options) ---
        triggers = self.form_root.locator(".firstmenu > a:visible")
        trigger_count = triggers.count()

        if trigger_count == 0 and select_count == 0:
            logger.info("_get_all_dropdown_selected: no visible dropdowns found on page")
            return 0

        for i in range(trigger_count):
            trigger = triggers.nth(i)
            try:
                if not trigger.is_visible():
                    continue
                trigger.click()
                self.page.wait_for_timeout(300)

                # Options are siblings in the parent container's dd > dl > dd > a
                parent = self.page.locator(".show-dropdown.styled-ddl:visible, dl.show-dropdown:visible").first
                options = parent.locator("dd a").all() if parent.count() > 0 else []

                if not options:
                    # Fallback: close the dropdown and move on
                    trigger.click()
                    continue

                target = options[option_index] if option_index < len(options) else options[-1]
                target.click()
                acted += 1
            except Exception:
                continue
        return acted

    def _get_all_textboxes_filled(self, fill_value: str = "Test"):        
        """Helper method to fill all visible textboxes on the page with a default value."""
        textboxes = self.page.get_by_role("textbox")
        count = textboxes.count()
        for i in range(count):
            textbox = textboxes.nth(i)
            try:
                if textbox.is_visible() and textbox.is_enabled():
                    mask = textbox.get_attribute("data-am-mask")
                    data_max_value = textbox.get_attribute("data-max-value")
                    name = textbox.get_attribute("name") or ""
                    if mask is not None:
                        mask_lower = mask.lower()
                        if "date" in mask_lower:                            
                            tomorrow = (datetime.today() + timedelta(days=1)).strftime("%m%d%Y")
                            textbox.fill(tomorrow)
                        elif "ssn" in mask_lower:
                            textbox.fill(generate_random_number(9))
                        elif "phone" in mask_lower:
                            textbox.fill("7" + generate_random_number(9))
                        elif "zip" in mask_lower:
                            textbox.fill(generate_random_number(5))
                        elif "currency" in mask_lower:
                            textbox.fill(str(random.randint(10, 100)))
                        elif "email" in mask_lower:
                            textbox.fill(f"user{random.randint(10, 100)}@gmail.com")
                        elif "dob" in mask_lower:
                            textbox.fill((datetime.today() - timedelta(days=365*random.randint(18, 40))).strftime("%m%d%Y"))
                        elif "percent" in mask_lower:
                            textbox.fill(str(random.randint(1, 9)))    
                        elif "integer" in mask_lower and ("Month" in name or "Spec" in name):
                            textbox.fill(str(datetime.today().month))
                        elif "integer" in mask_lower and "Year" in name:                            
                            textbox.fill(str(datetime.today().year))
                        else:
                            textbox.fill(random_alpha(5))
                    else:
                        # Try alpha first; if the field rejects it (e.g. numeric-only),
                        # fall back to a random number string.
                        try:
                            prop_name = textbox.get_attribute("data-domainpropertyname") or ""
                            if "number" in prop_name.lower():
                                textbox.fill(generate_random_number(9))
                            else:
                                textbox.fill(fill_value)
                        except Exception:
                            try:
                                textbox.fill(str(random.randint(100, 9999)))
                            except Exception:
                                pass
            except Exception:
                continue

    def _fill_all_fields(self):     
        self._get_all_dropdown_selected()   
        self._get_all_checkboxes_checked()
        self._get_all_dropdown_selected()
        self._get_all_textboxes_filled()

    def _manage_bank_link(self):
        edit_link = self.page.locator("a.bank-edit").first
        dd_new_bank_link = self.page.locator("a.bank-select").first
        if edit_link.is_visible():
            logger.info("'Edit | Add New Bank' detected — skipping, bank already exists")
        elif dd_new_bank_link.is_visible():
            logger.info("Only 'Add New Bank' visible (no Edit), clicking it")
            dd_new_bank_link.click()
            self._get_all_textboxes_filled()
            self.page.get_by_role("button", name="Save").first.click()

    def _manage_add_address(self):
        # Find all address-picker containers and only click "Add Address" if no "Edit" link is present
        address_pickers = self.page.locator("div.address-picker-btn").all()
        logger.info(f"Found {len(address_pickers)} address-picker divs")

        for idx, picker in enumerate(address_pickers):
            try:
                edit_link = picker.locator("a.address-edit")
                add_link = picker.locator("a.address-select")
                # if edit_link.is_visible():
                #     logger.info(f"Address picker {idx+1}: 'Edit | Add Address' present — skipping")
                #     continue
                if add_link.is_visible():
                    logger.info(f"Address picker {idx+1}: Only 'Add Address' visible, clicking it")
                    add_link.click()
                    self.page.wait_for_timeout(500)
                    # Check if popover appeared with existing address rows
                    popover = self.page.locator("div.popover.custom-popover:visible")
                    if popover.is_visible():
                        existing_row = popover.locator("div.popover-picker:not(.popover-picker-add)").first
                        if existing_row.is_visible():
                            logger.info(f"Address picker {idx+1}: Existing address row found in popover, selecting it")
                            existing_row.click()
                            self.page.wait_for_timeout(500)
                            continue
                        # No existing row — click "Add New" and fill
                        add_new = popover.locator("div.popover-picker-add").first
                        if add_new.is_visible():
                            logger.info(f"Address picker {idx+1}: No existing address, clicking 'Add New'")
                            add_new.click()
                            self._get_all_dropdown_selected()
                            self._get_all_textboxes_filled()
                            self.page.get_by_role("button", name="Save").first.click()
                            self.page.wait_for_timeout(1000)
                            self.page.get_by_role("button", name="Save").first.click()
                            self.page.wait_for_timeout(1000)
                    else:
                        # No popover — direct form opened
                        self._get_all_dropdown_selected()
                        self._get_all_textboxes_filled()
                        self.page.get_by_role("button", name="Save").first.click()
                        self.page.wait_for_timeout(1000)
                        self.page.get_by_role("button", name="Save").first.click()
                        self.page.wait_for_timeout(1000)
            except Exception:
                logger.info(f"Failed to process address picker {idx+1}, skipping")
                continue

        # Also handle any standalone "Add Address" links not inside a picker div
        for link in self.page.get_by_text("Add Address", exact=True).all():
            try:
                in_picker = link.evaluate("el => !!el.closest('.address-picker-btn')")
                if in_picker:
                    continue
                if not link.is_visible():
                    continue
                logger.info("Standalone 'Add Address' link found, clicking it")
                link.click()
                self._get_all_dropdown_selected()
                self._get_all_textboxes_filled()
                self.page.get_by_role("button", name="Save").first.click()
                self.page.wait_for_timeout(1000)
                self.page.get_by_role("button", name="Save").first.click()
                self.page.wait_for_timeout(1000)
            except Exception:
                continue
         