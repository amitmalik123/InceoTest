from typing import Union, List, Optional
from playwright.sync_api import Locator, Page, FrameLocator, expect

from pages.ewm.base_page import BasePage
from pages.stp.stp_manageBene.locators.manage_bene_detail_locators import ManageBeneDetailLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageBeneDetailPage(BasePage):
    """
    Page object for Add Beneficiary modal in Manage Beneficiaries feature.
    Handles Individual (Spouse/Non-Spouse), Trust, and Entity beneficiary types.
    """

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        loc = ManageBeneDetailLocators
        
        self.beneficiaries_section = context.locator(loc.BENEFICIARIES_SECTION)
        self.add_beneficiary_button: Locator = context.locator(loc.ADD_BENEFICIARY_BUTTON)
        self.notification_locator: Locator = context.locator(loc.NOTIFICATION_LOCATOR)
        
        self.account_holder_heading: Locator = context.locator(loc.ACCOUNT_HOLDER_HEADING)
        
        self.account_cards: Locator = context.locator(loc.ACCOUNT_CARDS)
        self.contingent_empty_state: Locator = context.locator(loc.CONTINGENT_EMPTY_STATE)
        self.account_card_title: Locator = context.locator(loc.ACCOUNT_CARD_TITLE)
        self.primary_beneficiary_name: Locator = context.locator(loc.PRIMARY_BENEFICIARY_NAME)
        
        self.contingent_empty: Locator = context.locator(loc.CONTINGENT_EMPTY)
        self.account_title_with_contingent_empty: Locator = context.locator(loc.ACCOUNT_TITLE_WITH_CONTINGENT_EMPTY)
        self.beneficiary_cards: Locator = context.locator(loc.BENEFICIARY_CARDS)
        
        self.signature_options_section: Locator = context.locator(loc.SIGNATURE_OPTIONS_SECTION)
        self.electronic_signature_radio: Locator = context.locator(loc.ELECTRONIC_SIGNATURE_RADIO)
        self.physical_signature_radio: Locator = context.locator(loc.PHYSICAL_SIGNATURE_RADIO)
        self.continue_to_esignature_button: Locator = context.locator(loc.CONTINUE_TO_ESIGNATURE_BUTTON)
        self.continue_to_review_button: Locator = context.locator(loc.CONTINUE_TO_REVIEW_BUTTON)

    def wait_for_page_load(self) -> None:
        """Wait for the Manage Beneficiaries page to load."""
        logger.info("Waiting for Manage Beneficiaries page to load")
        self.beneficiaries_section.wait_for(state="visible", timeout=10000)
        logger.info("Manage Beneficiaries page loaded successfully")

    def is_beneficiaries_section_present(self) -> bool:
        logger.info("Checking if beneficiaries section (Manage Beneficiaries button) is present")
        try:
            self.beneficiaries_section.wait_for(state="visible", timeout=30000)
            result = self.beneficiaries_section.is_visible()
        except Exception:
            result = False
        logger.info(f"Beneficiaries section present: {result}")
        return result

    def get_primary_account_holder_name(self) -> str:
        
        logger.info("Getting primary account holder name from page heading")
        self.account_holder_heading.wait_for(state="visible", timeout=5000)
        account_holder_name = self.account_holder_heading.inner_text().strip()
        logger.info(f"[OK] Primary account holder name from page: {account_holder_name}")
        return account_holder_name

    def get_accounts_with_no_contingent_beneficiaries(self) -> List[dict]:
        
        logger.info("Getting accounts with no contingent beneficiaries")
        accounts_with_no_contingent = []
        
        # Use .first to avoid strict-mode violation when multiple accounts
        # have no contingent beneficiaries (locator matches > 1 element).
        self.contingent_empty.first.wait_for(state="visible", timeout=5000)
        contingent_count = self.contingent_empty.count()
        logger.info(f"Found {contingent_count} accounts with no contingent beneficiaries")
        
        for i in range(contingent_count):
            try:        
                if self.account_title_with_contingent_empty.count() > 0:
                    
                    account_info = self.account_title_with_contingent_empty.first.inner_text()

                    account_data = {
                        'account_info': account_info   
                    }
                    accounts_with_no_contingent.append(account_data)
                    logger.info(f"[OK] Found account with no contingent: {account_info}")
                else:
                    logger.warning(f"Card {i+1}: Account title locator not found")
            except Exception as e:
                logger.error(f"Error processing contingent empty {i+1}: {str(e)}", exc_info=True)
        
        logger.info(f"Total accounts with no contingent beneficiaries: {len(accounts_with_no_contingent)}")
        return accounts_with_no_contingent

    def get_first_beneficiary_name_by_relation(self, relation: str) -> str:
        """Return the name of the first beneficiary whose relation label matches `relation`.

        XPath axis used:
          span[contains(@class,'MuiTypography-cardTextPrimary')]
            [following-sibling::span[contains(@class,'MuiTypography-cardTextSecondary')
                                     and normalize-space()='{relation}']]
        This navigates from the name span forward to its sibling relation span to filter by
        relation without leaving the name context.
        """
        logger.info(f"Looking for first beneficiary with relation: '{relation}' on manage bene page")
        xpath = (
            f"(//span[contains(@class,'MuiTypography-cardTextPrimary')]"
            f"[following-sibling::span[contains(@class,'MuiTypography-cardTextSecondary')"
            f" and normalize-space()='{relation}']])[1]"
        )
        name_locator = self.context.locator(f"xpath={xpath}")
        # Use a short poll instead of wait_for to give a clear assertion error
        # when no beneficiary of this relation exists on the page.
        self.context.wait_for_timeout(1000)
        if name_locator.count() == 0:
            raise AssertionError(
                f"No beneficiary with relation '{relation}' found on the manage beneficiaries page. "
                f"Cannot proceed with Existing beneficiary flow for this relation type."
            )
        name = name_locator.first.inner_text().strip()
        logger.info(f"[OK] Found beneficiary '{name}' with relation '{relation}'")
        return name

    def click_add_beneficiary_button(self) -> None:
        """Click the Add Beneficiary button to open add beneficiary form."""
        logger.info("Clicking Add Beneficiary button")
        self.add_beneficiary_button.wait_for(state="visible", timeout=5000)
        self.add_beneficiary_button.click()
        logger.info("[OK] Add Beneficiary button clicked successfully")

    def verifyBeneficiaryDetails(self, fullName: str, relationship: str) -> None:
       
        logger.info(f"Verifying beneficiary details for: {fullName} ({relationship})")
        
        self.beneficiary_cards.first.wait_for(state="visible", timeout=10000)
        
        nameXpath = f"//span[contains(@class, 'MuiTypography-cardTextPrimary')][contains(normalize-space(.), '{fullName}')]"
        nameElement = self.context.locator(f"xpath={nameXpath}")
        
        expect(nameElement).to_be_visible(timeout=15000)
        logger.info(f"[OK] Beneficiary name '{fullName}' is displayed")
        
        relationshipXpath = f"{nameXpath}/following-sibling::span[contains(@class, 'MuiTypography-cardTextSecondary')]"
        relationshipElement = self.context.locator(f"xpath={relationshipXpath}")
        
        expect(relationshipElement).to_have_text(relationship, timeout=10000)
        logger.info(f"[OK] Relationship '{relationship}' is displayed correctly")
    
    def clickDeleteButtonForBeneficiary(self, beneficiaryName: str) -> None:
        
        logger.info(f"Clicking delete button for beneficiary: {beneficiaryName}")
        
        deleteButtonXpath = (
            f"//span[contains(@class, 'MuiTypography-cardTextPrimary')][contains(text(), '{beneficiaryName}')]"
            f"/ancestor::div[contains(@class, 'MuiBox-root')]"
            f"//button[contains(@aria-label, 'Delete {beneficiaryName}')]"
        )
        
        deleteButton = self.context.locator(f"xpath={deleteButtonXpath}")
        deleteButton.scroll_into_view_if_needed()
        deleteButton.wait_for(state="visible", timeout=10000)
        deleteButton.click()
        
        logger.info(f"[OK] Delete button clicked for beneficiary '{beneficiaryName}'")

    def click_edit_button(self, beneficiary_name: str) -> None:
        """Click the Edit icon button for the named beneficiary row.

        DOM axis path:
          span.MuiTypography-cardTextPrimary (name)
            -> parent::div            (name-column container, css-1yw9ps3)
            -> following-sibling::div (actions column, css-dd64rs)
            -> button[@aria-label='Edit {name}']  (MuiIconButton)
        """
        logger.info(f"Clicking Edit button for beneficiary: {beneficiary_name}")
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"contains(normalize-space(text()),'{beneficiary_name}')]"
            f"/parent::div/following-sibling::div"
            f"//button[contains(@aria-label,'Edit {beneficiary_name}')]"
        )
        edit_button = self.context.locator(f"xpath={xpath}")
        edit_button.scroll_into_view_if_needed()
        edit_button.wait_for(state="visible", timeout=5000)
        edit_button.click()
        logger.info(f"[OK] Edit button clicked for '{beneficiary_name}'")

    def getDeleteButtonForAddedBeneficiary(self, beneficiaryName: str) -> Locator:
        logger.info(f"Getting delete button locator for ADDED beneficiary: {beneficiaryName}")
        
        deleteButtonXpath = (
            f"//span[normalize-space()='{beneficiaryName}']"
            f"/ancestor::div[.//span[normalize-space()='ADDED']]"
            f"//button[@aria-label='Delete {beneficiaryName}']"
        )
        
        return self.context.locator(f"xpath={deleteButtonXpath}")

    def deleteAddedBeneficiary(self, beneficiaryName: str) -> None:
        logger.info(f"Deleting ADDED beneficiary: {beneficiaryName}")
        
        deleteButton = self.getDeleteButtonForAddedBeneficiary(beneficiaryName)
        deleteButton.scroll_into_view_if_needed()
        logger.info(f"Scrolled delete button into view for '{beneficiaryName}'")
        
        deleteButton.wait_for(state="visible", timeout=10000)
        
        try:
            deleteButton.click(timeout=5000)
            logger.info(f"[OK] ADDED beneficiary '{beneficiaryName}' delete button clicked")
        except Exception as e:
            logger.warning(f"Normal click failed, trying force click: {e}")
            deleteButton.click(force=True)
            logger.info(f"[OK] ADDED beneficiary '{beneficiaryName}' delete button clicked with force")

    def getNotificationText(self) -> str:
        logger.info("Waiting for notification to appear")
        
        self.notification_locator.wait_for(state="visible", timeout=2000)
        notificationText = self.notification_locator.inner_text().strip()
        
        logger.info(f"Notification text: {notificationText}")
        return notificationText

    def selectSignatureOption(self, optionText: str) -> None:
        
        logger.info(f"Selecting signature option: {optionText}")
        
        self.signature_options_section.wait_for(state="visible", timeout=10000)
        
        if "Electronic" in optionText:
            self.electronic_signature_radio.scroll_into_view_if_needed()
            self.electronic_signature_radio.check()
            logger.info("[OK] Electronic signature option selected")
        elif "Physical" in optionText:
            self.physical_signature_radio.scroll_into_view_if_needed()
            self.physical_signature_radio.check()
            logger.info("[OK] Physical signature option selected")
        else:
            raise ValueError(f"Invalid signature option: {optionText}")
        
        self.context.wait_for_timeout(500)

    def isButtonEnabled(self, buttonText: str) -> bool:
        
        logger.info(f"Checking if button '{buttonText}' is enabled")
        
        if "e-Signature" in buttonText:
            button = self.continue_to_esignature_button
        elif "Review" in buttonText:
            button = self.continue_to_review_button
        else:
            raise ValueError(f"Unknown button: {buttonText}")
        
        button.scroll_into_view_if_needed()
        is_enabled = button.is_enabled()
        logger.info(f"Button '{buttonText}' enabled: {is_enabled}")
        return is_enabled

    def isButtonDisabled(self, buttonText: str) -> bool:
        
        logger.info(f"Checking if button '{buttonText}' is disabled")
        is_disabled = not self.isButtonEnabled(buttonText)
        logger.info(f"Button '{buttonText}' disabled: {is_disabled}")
        return is_disabled

    def click_continue_to_esignature(self) -> None:
        logger.info("Clicking 'Continue to e-Signature Details' button")
        self.continue_to_esignature_button.scroll_into_view_if_needed()
        self.continue_to_esignature_button.click()
        logger.info("Clicked 'Continue to e-Signature Details' button")

    def click_continue_to_review(self) -> None:
        logger.info("Clicking 'Continue to Review' button")
        self.continue_to_review_button.scroll_into_view_if_needed()
        self.continue_to_review_button.click()
        logger.info("Clicked 'Continue to Review' button")

    def verify_beneficiary_in_designation_section(self, beneficiary_name: str, designation: str, account_identifier: Optional[str] = None) -> bool:
        logger.info(f"Verifying beneficiary '{beneficiary_name}' in {designation} section")

        if account_identifier:
            # Scope to the specific account card whose own header contains account_identifier,
            # then narrow to the correct designation section within it.
            designation_section_xpath = (
                f"//div[contains(@class,'MuiCard-root')]"
                f"[./div[contains(@class,'MuiCardHeader-root')]"
                f"//span[contains(@class,'MuiCardHeader-title') and contains(.,'{account_identifier}')]]"
                f"//span[contains(@class,'MuiTypography-cardHeaderTitle') and normalize-space(text())='{designation}']"
                f"/ancestor::div[.//button[normalize-space(.)='Allocate Equally']][1]"
                f"//span[contains(@class,'MuiTypography-cardTextPrimary') and contains(normalize-space(.),'{beneficiary_name}')]"
            )
        else:
            # No account scoping — search across all designation sections on the page.
            designation_section_xpath = (
                f"//span[contains(@class,'MuiTypography-cardHeaderTitle') and normalize-space(text())='{designation}']"
                f"/ancestor::div[.//button[normalize-space(.)='Allocate Equally']][1]"
                f"//span[contains(@class,'MuiTypography-cardTextPrimary') and contains(normalize-space(.),'{beneficiary_name}')]"
            )

        logger.info(f"  - Using XPath: {designation_section_xpath}")

        beneficiary_element = self.context.locator(f"xpath={designation_section_xpath}").first

        beneficiary_element.wait_for(state="visible", timeout=15000)
        is_visible = beneficiary_element.is_visible()

        if is_visible:
            actual_beneficiary_name = beneficiary_element.inner_text().strip()
            logger.info(f"[OK] Beneficiary '{actual_beneficiary_name}' found in '{designation}' section")
            return True

        return False

    def get_added_label_locator(self, beneficiary_name: str) -> "Locator":
        
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"contains(normalize-space(text()),'{beneficiary_name}')]"
            f"/parent::div/following-sibling::div"
            f"//span[contains(@class,'MuiChip-label') and normalize-space(text())='ADDED']"
        )
        logger.info(f"Building ADDED label locator for '{beneficiary_name}' using XPath: {xpath}")
        return self.context.locator(f"xpath={xpath}")

    def get_first_beneficiary_info_and_click_edit(self) -> dict:
        """
        Reads name, relationship (user type) and allocation from the very first
        beneficiary row on the page, then clicks its Edit button.

        DOM axis path per row (css-ifddmn container):
          div.css-ifddmn
            ├─ div.css-1yw9ps3
            │   ├─ span.MuiTypography-cardTextPrimary   → name
            │   └─ span.MuiTypography-cardTextSecondary  → relationship
            ├─ div.css-dd64rs
            │   └─ button[aria-label='Edit <name>']       → edit button
            └─ div.css-f0eqg5
                └─ input[type='number']                   → allocation value

        Returns:
            {
              'name': 'Danny L Smith',
              'relationship': 'Non-Spouse',
              'allocation': 45.0,
            }
        """
        # Locate first Edit button on the page (any section, any card)
        first_edit_btn = self.context.locator(
            "xpath=//button[starts-with(@aria-label,'Edit ')]"
        ).first
        first_edit_btn.wait_for(state="visible", timeout=10000)

        # aria-label is 'Edit <name>', strip the prefix to get the name
        aria_label = first_edit_btn.get_attribute("aria-label")
        name = aria_label.replace("Edit ", "", 1).strip()
        logger.info(f"First Edit button found — beneficiary name: '{name}'")

        # Navigate from the Edit button up to the row container (css-ifddmn)
        # then collect sibling info using XPath relative to the name span
        row_xpath = (
            f"//button[@aria-label='Edit {name}']"
            f"/ancestor::div[contains(@class,'css-ifddmn')]"
        )
        row = self.context.locator(f"xpath={row_xpath}")

        relationship = row.locator("span.MuiTypography-cardTextSecondary").first.inner_text().strip()
        logger.info(f"  Relationship: {relationship}")

        alloc_input = row.locator("input[type='number']")
        allocation = (
            float(alloc_input.get_attribute("value"))
            if alloc_input.count() > 0 and alloc_input.get_attribute("value")
            else None
        )
        logger.info(f"  Allocation: {allocation}%")

        logger.info(f"Clicking Edit button for first beneficiary: '{name}'")
        first_edit_btn.scroll_into_view_if_needed()
        first_edit_btn.click()
        logger.info(f"[OK] Edit button clicked for '{name}'")

        return {"name": name, "relationship": relationship, "allocation": allocation}
        
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"contains(normalize-space(text()),'{beneficiary_name}')]"
            f"/parent::div/following-sibling::div"
            f"//span[contains(@class,'MuiChip-label') and normalize-space(text())='ADDED']"
        )
        logger.info(f"Building ADDED label locator for '{beneficiary_name}' using XPath: {xpath}")
        return self.context.locator(f"xpath={xpath}")

    def get_all_section_allocation_totals(self) -> list:
        """
        Collects allocation totals and beneficiary details for every Primary and
        Contingent section on the page.

        Fix 1 — account_card_xpath: uses ./div[contains(@class,'MuiCardHeader-root')]
          (direct child) so the outer 'Beneficiaries' wrapper card (whose own header
          title is 'Beneficiaries', no '•') is excluded even though its descendant
          inner cards DO have '•' in their titles.

        Fix 2 — section total XPath: uses
          ancestor::div[.//button[normalize-space(.)='Allocate Equally']][1]
          to reach the nearest section-container div, then searches downward for
          the 'Total:' paragraph — avoids the fragile parent/parent/following-sibling
          chain that silently produced no results.

        Returns:
            [
              {
                'account': 'Tesla C On, Inherited IRA • 40401241',
                'sections': [
                  {
                    'type': 'Primary',
                    'total_text': 'Total: 100.00%',
                    'total_pct': 100.0,
                    'beneficiaries': [{'name': 'Danny L Smith', 'allocation': 45.0}, ...]
                  },
                  { 'type': 'Contingent', ... }
                ]
              },
              ...
            ]
        """
        import re

        # FIX 1: scope to the card's OWN (direct-child) MuiCardHeader-root so the
        # outer 'Beneficiaries' wrapper card — which contains descendant account cards
        # with '•' — is not matched.
        account_card_xpath = (
            "//div[contains(@class,'MuiCard-root')]"
            "[./div[contains(@class,'MuiCardHeader-root')]"
            "//span[contains(@class,'MuiCardHeader-title') and contains(.,'\u2022')]]"
        )
        account_cards = self.context.locator(f"xpath={account_card_xpath}")
        try:
            account_cards.first.wait_for(timeout=15000)
        except Exception:
            pass
        n_cards = account_cards.count()
        logger.info(f"Found {n_cards} account card(s) to check allocations")

        results = []
        for i in range(n_cards):
            card = account_cards.nth(i)
            # Read title from the card's own direct header (not a descendant card's header)
            account_title = card.locator(
                "xpath=./div[contains(@class,'MuiCardHeader-root')]"
                "//span[contains(@class,'MuiCardHeader-title')]"
            ).inner_text().strip()
            logger.info(f"Processing card [{i+1}]: {account_title}")

            card_data = {'account': account_title, 'sections': []}

            for section_type in ('Primary', 'Contingent'):
                section_label = card.locator(
                    f"xpath=.//span[contains(@class,'MuiTypography-cardHeaderTitle')"
                    f" and normalize-space(text())='{section_type}']"
                )
                if section_label.count() == 0:
                    logger.info(f"  No '{section_type}' section in card — skipping")
                    continue

                # FIX 2: climb to nearest ancestor that owns an 'Allocate Equally'
                # button (= the Primary or Contingent section container div), then
                # search downward.  [1] picks the nearest such ancestor.
                section_container = card.locator(
                    f"xpath=.//span[contains(@class,'MuiTypography-cardHeaderTitle')"
                    f" and normalize-space(text())='{section_type}']"
                    f"/ancestor::div[.//button[normalize-space(.)='Allocate Equally']][1]"
                )
                if section_container.count() == 0:
                    logger.warning(f"  '{section_type}' section container not found — skipping")
                    continue

                total_loc = section_container.locator("xpath=.//p[contains(.,'Total:')]")
                if total_loc.count() == 0:
                    logger.warning(f"  '{section_type}': Total: text not found within section container")
                    continue

                total_text = total_loc.first.inner_text().strip()
                match = re.search(r'Total:\s*([\d.]+)%', total_text)
                total_pct = float(match.group(1)) if match else None
                logger.info(f"  [{section_type}] {total_text} → {total_pct}%")

                # Beneficiary names within the section container
                name_locs = section_container.locator("span.MuiTypography-cardTextPrimary")
                beneficiaries = []
                n_benes = name_locs.count()
                for k in range(n_benes):
                    name = name_locs.nth(k).inner_text().strip()
                    # Find the allocation input co-located in the same bene row
                    alloc_xpath = (
                        f"xpath=.//span[contains(@class,'MuiTypography-cardTextPrimary')"
                        f" and normalize-space(.)='{name}']"
                        f"/ancestor::div[.//input[@type='number']][1]"
                        f"//input[@type='number']"
                    )
                    alloc_input = section_container.locator(alloc_xpath)
                    alloc_val = (
                        float(alloc_input.get_attribute('value'))
                        if alloc_input.count() > 0 and alloc_input.get_attribute('value')
                        else None
                    )
                    beneficiaries.append({'name': name, 'allocation': alloc_val})
                    logger.info(f"    {name}: {alloc_val}%")

                card_data['sections'].append({
                    'type': section_type,
                    'total_text': total_text,
                    'total_pct': total_pct,
                    'beneficiaries': beneficiaries,
                })

            results.append(card_data)

        return results


    def get_toast_text(self) -> str:
        """
        Return the text of the first visible toast/alert notification.
        Tries div[role='alert'], .MuiAlert-root, .Snackbar in order.
        Returns empty string if none is visible.
        """
        for selector in ("div[role='alert']", ".MuiAlert-root", ".Snackbar"):
            loc = self.context.locator(selector)
            if loc.is_visible():
                return loc.text_content() or ""
        return ""

    def is_toast_visible(self) -> bool:
        """Return True if any toast/alert notification is currently visible."""
        for selector in ("div[role='alert']", ".MuiAlert-root", ".Snackbar"):
            if self.context.locator(selector).is_visible():
                return True
        return False

   

    def is_confirmation_modal_visible(self) -> bool:
        """Return True if a confirmation dialog modal is currently visible."""
        return self.context.locator("div[role='dialog'], .MuiDialog-root").first.is_visible()

    def get_confirm_dialog_button(self) -> Locator:
        """Return the confirmation action button from an open dialog (Confirm/Yes/Delete/Remove)."""
        return self.context.locator(
            "button:has-text('Confirm'), button:has-text('Yes'), "
            "button:has-text('Delete'), button:has-text('Remove')"
        ).first

    def confirm_dialog_action(self) -> None:
        """Click the confirmation button in an open dialog."""
        self.get_confirm_dialog_button().click()
        logger.info("Confirmation dialog button clicked")