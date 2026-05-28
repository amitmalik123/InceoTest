from playwright.sync_api import expect

class LeadsPage_Fields():
    
    def __init__(self, Page):
        self.page = Page
        #self.page.newButton = self.page.get_by_role("button", name="New")
        self.page.newButton = self.page.locator("li[data-target-selection-name='sfdc:StandardButton.Lead.New']")
        # Salesforce renders the "New" action twice (visible action bar + hidden overflow menu).
        # Target the inner clickable anchor/button and filter to the visible instance.
        # self.page.newButton = self.page.locator(
        #     "li[data-target-selection-name='sfdc:StandardButton.Lead.New'] a, "
        #     "li[data-target-selection-name='sfdc:StandardButton.Lead.New'] button"
        # ).locator("visible=true").first
        self.page.firstNameInput = self.page.locator("input[name='firstName']")
        self.page.lastNameInput = self.page.locator("input[name='lastName']")
        self.page.emailInput = self.page.locator("input[name='Email']")
        self.page.phoneInput = self.page.locator("input[name='Phone']")
        #self.page.companyInput = self.page.locator("input[name='Company']")
        #self.page.addressInformationHeader = self.page.locator("h3>[title='Address Information']")
        self.page.addressSearchInput = self.page.locator("input[aria-label='Address Search']")
        self.page.streetInput = self.page.locator("textarea[name='street']")
        self.page.cityInput = self.page.locator("input[name='city']")
        self.page.provinceInput = self.page.locator("input[name='province']")
        self.page.postalCodeInput = self.page.locator("input[name='postalCode']")
        self.page.countryInput = self.page.locator("input[name='country']") 
        self.page.brokerDealerAccountInput = self.page.locator("input[aria-label='Broker Dealer'][role='combobox']")
        self.page.advisorFirmAccountInput = self.page.locator("input[aria-label='Advisor Firm'][role='combobox']")
        self.page.affiliatedNetworkAccountInput = self.page.locator("input[aria-label='Affiliated Network'][role='combobox']")
        #self.page.crdFirmInput = self.page.locator("input[name='CRD_Firm__c']")
        # Fall back to aria-label match in case the API name differs (e.g. CRD_Advisor_Number__c)
        self.page.crdAdvisorInput = self.page.locator("input[name='CRD_Advisor__c']")
        #self.page.opportunityStageDropdown = self.page.locator("button[aria-label='Opportunity Stage']")
        #self.page.opportunityStageDropdown = self.page.get_by_role("combobox", name="Opportunity Stage")
        #self.page.opportunityStageDropdownValue1 = self.page.locator("div[aria-label='Opportunity Stage'] lightning-base-combobox-item [title='Prospecting']")
        #self.page.opportunityStageDropdownValue2 = self.page.locator("div[aria-label='Opportunity Stage'] lightning-base-combobox-item [title='Qualified']")
        #self.page.opportunityAmountInput = self.page.locator("input[name='Opportunity_Amount__c']")
        #self.page.expectedAUMInput = self.page.locator("input[name='Expected_AUM_Commitment_Next_12_Months__c']")
        #self.page.opportunityCloseDateInput = self.page.locator("input[name='Opportunity_Close_Date__c']")


    def verify_Standard_Fields(self):
        # Wait for list view actions bar to fully render before clicking New
        self.page.newButton.wait_for(state="visible", timeout=50000)
        self.page.newButton.scroll_into_view_if_needed()
        self.page.newButton.click()
        expect(self.page.firstNameInput).to_be_visible()
        expect(self.page.lastNameInput).to_be_visible()
        expect(self.page.emailInput).to_be_visible()
        expect(self.page.phoneInput).to_be_visible()
        #expect(self.page.companyInput).to_be_visible()
        #expect(self.page.addressInformationHeader).to_be_visible()
        expect(self.page.addressSearchInput).to_be_visible()
        expect(self.page.streetInput).to_be_visible()
        expect(self.page.cityInput).to_be_visible()
        expect(self.page.provinceInput).to_be_visible()
        expect(self.page.postalCodeInput).to_be_visible()
        expect(self.page.countryInput).to_be_visible()

    def verify_Lookup_Fields(self):
        expect(self.page.brokerDealerAccountInput).to_be_visible()
        expect(self.page.advisorFirmAccountInput).to_be_visible()
        expect(self.page.affiliatedNetworkAccountInput).to_be_visible()
        

    def verify_CRD_Fields(self):
        self.page.reload()
        self.page.wait_for_timeout(2000)
        #self.page.crdFirmInput.wait_for(state="visible", timeout=10000)
        #expect(self.page.crdFirmInput).to_be_visible()
        #self.page.crdAdvisorInput.first.scroll_into_view_if_needed()
        self.page.crdAdvisorInput.first.wait_for(state="visible", timeout=10000)
        expect(self.page.crdAdvisorInput.first).to_be_visible()
        self.page.cancelButton.click()

    # def verify_Opportunity_Related_Fields(self):
    #     self.page.wait_for_timeout(2000)
    #     self.page.opportunityStageDropdown.focus()
    #     self.page.opportunityStageDropdown.wait_for(state="visible", timeout=10000)
    #     self.page.opportunityStageDropdown.click()
    #     self.page.wait_for_timeout(2000)
    #     expect(self.page.opportunityStageDropdownValue1).to_be_visible()
    #     expect(self.page.opportunityStageDropdownValue2).to_be_visible()
    #     expect(self.page.opportunityAmountInput).to_be_visible()
    #     expect(self.page.expectedAUMInput).to_be_visible()
    #     expect(self.page.opportunityCloseDateInput).to_be_visible()
    #     self.page.cancelButton.click()