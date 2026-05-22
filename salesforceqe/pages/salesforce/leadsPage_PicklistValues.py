from playwright.sync_api import expect

class LeadsPage_PicklistValues():
    
    def __init__(self, Page):
        self.page = Page
        self.page.leadSourceDropdown = self.page.locator("button[aria-label='Lead Source']")
        self.page.leadSourceDropdown1 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='--None--']")
        #self.page.leadSourceDropdown2 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='AssetMark Event']")
        self.page.leadSourceDropdown2 = self.page.get_by_role("option", name="AssetMark Event")
        self.page.leadSourceDropdown3 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='BD Conference']")
        self.page.leadSourceDropdown4 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Webinar']")
        self.page.leadSourceDropdown5 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Referral - Adhesion']")
        self.page.leadSourceDropdown6 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Referral - External']")
        self.page.leadSourceDropdown7 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='3rd Party Data']")
        self.page.leadSourceDropdown8 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Inbound Call']")
        self.page.leadSourceDropdown9 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Outbound Call']")
        self.page.leadSourceDropdown10 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='BD Rep List']")
        self.page.leadSourceDropdown11 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='OSJ/Producer Group']")
        self.page.leadSourceDropdown12 = self.page.locator("div[aria-label='Lead Source'] lightning-base-combobox-item [title='Acquisition']")
        
        # self.page.leadStatusDropdown = self.page.locator("button[aria-label='Lead Status']")
        # self.page.leadStatusDropdownValue1 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='--None--']")
        # self.page.leadStatusDropdownValue2 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Marketing Qualification']")
        # self.page.leadStatusDropdownValue3 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Sales Ops Review']")
        # self.page.leadStatusDropdownValue4 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Nurture']")
        # self.page.leadStatusDropdownValue5 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Actively Being Worked']")
        # self.page.leadStatusDropdownValue6 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Unqualified']")
        # self.page.leadStatusDropdownValue7 = self.page.locator("div[aria-label='Lead Status'] lightning-base-combobox-item [title='Converted']")
        
        # self.page.leadTypeDropdown = self.page.locator("button[aria-label='Lead Type']")
        # self.page.leadTypeDropdownValue1 = self.page.locator("div[aria-label='Lead Type'] lightning-base-combobox-item [title='New Advisor']")
        
        self.page.marketingFunnelDropdown = self.page.locator("button[aria-label='Marketing Funnel Stage']")
        self.page.marketingFunnelDropdownValue1 = self.page.locator("div[aria-label='Marketing Funnel Stage'] lightning-base-combobox-item [title='--None--']")
        self.page.marketingFunnelDropdownValue2 = self.page.locator("div[aria-label='Marketing Funnel Stage'] lightning-base-combobox-item [title='TOFU']")
        self.page.marketingFunnelDropdownValue3 = self.page.locator("div[aria-label='Marketing Funnel Stage'] lightning-base-combobox-item [title='MOFU']")
        self.page.marketingFunnelDropdownValue4 = self.page.locator("div[aria-label='Marketing Funnel Stage'] lightning-base-combobox-item [title='BOFU']")
        
        self.page.registeredRepTypeDropdown = self.page.locator("button[aria-label='Registered Rep Type']")
        self.page.registeredRepTypeDropdownValue1 = self.page.locator("div[aria-label='Registered Rep Type'] lightning-base-combobox-item [title='--None--']")
        self.page.registeredRepTypeDropdownValue2 = self.page.locator("div[aria-label='Registered Rep Type'] lightning-base-combobox-item [title='Corporate RIA']")
        self.page.registeredRepTypeDropdownValue3 = self.page.locator("div[aria-label='Registered Rep Type'] lightning-base-combobox-item [title='Independent RIA']")
        self.page.registeredRepTypeDropdownValue4 = self.page.locator("div[aria-label='Registered Rep Type'] lightning-base-combobox-item [title='Hybrid RIA']")
        
        self.page.leadChannelDropdown = self.page.locator("button[aria-label='Lead Channel']")
        self.page.leadChannelDropdownValue1 = self.page.locator("div[aria-label='Lead Channel'] lightning-base-combobox-item [title='Corporate Referral']")
        self.page.leadChannelDropdownValue2 = self.page.locator("div[aria-label='Lead Channel'] lightning-base-combobox-item [title='Corporate Advisor']")
        self.page.leadChannelDropdownValue3 = self.page.locator("div[aria-label='Lead Channel'] lightning-base-combobox-item [title='Independent Referral']")
        self.page.leadChannelDropdownValue4 = self.page.locator("div[aria-label='Lead Channel'] lightning-base-combobox-item [title='Independent Advisor']")


    def verify_Lead_Source_Picklist_Values(self):
        self.page.leadSourceDropdown.click()
        expect(self.page.leadSourceDropdown1).to_be_visible()
        expect(self.page.leadSourceDropdown2).to_be_visible()
        expect(self.page.leadSourceDropdown3).to_be_visible()
        expect(self.page.leadSourceDropdown4).to_be_visible()
        expect(self.page.leadSourceDropdown5).to_be_visible()
        expect(self.page.leadSourceDropdown6).to_be_visible()
        expect(self.page.leadSourceDropdown7).to_be_visible()
        expect(self.page.leadSourceDropdown8).to_be_visible()
        expect(self.page.leadSourceDropdown9).to_be_visible()
        expect(self.page.leadSourceDropdown10).to_be_visible()
        expect(self.page.leadSourceDropdown11).to_be_visible()
        expect(self.page.leadSourceDropdown12).to_be_visible()
        

    # def verify_Lead_Status_Picklist_Values(self):
    #     self.page.leadStatusDropdown.click()
    #     expect(self.page.leadStatusDropdownValue1).to_be_visible()
    #     expect(self.page.leadStatusDropdownValue2).to_be_visible()
    #     expect(self.page.leadStatusDropdownValue3).to_be_visible()
    #     expect(self.page.leadStatusDropdownValue4).to_be_visible()
    #     expect(self.page.leadStatusDropdownValue5).to_be_visible()
    #     expect(self.page.leadStatusDropdownValue6).to_be_visible()   
    #     expect(self.page.leadStatusDropdownValue7).to_be_visible()

    # def verify_Lead_Type_Picklist_Values(self):
    #     self.page.leadTypeDropdown.click()
    #     expect(self.page.leadTypeDropdownValue1).to_be_visible()
        
    def verify_Marketing_Funnel_Picklist_Values(self):
        self.page.marketingFunnelDropdown.click()
        expect(self.page.marketingFunnelDropdownValue1).to_be_visible()
        expect(self.page.marketingFunnelDropdownValue2).to_be_visible()
        expect(self.page.marketingFunnelDropdownValue3).to_be_visible()
        expect(self.page.marketingFunnelDropdownValue4).to_be_visible()

    def verify_Registered_Rep_Type_Picklist_Values(self):
        self.page.registeredRepTypeDropdown.wait_for(state="visible", timeout=10000)
        self.page.registeredRepTypeDropdown.click()
        self.page.registeredRepTypeDropdownValue1.wait_for(state="visible", timeout=10000)
        expect(self.page.registeredRepTypeDropdownValue1).to_be_visible()
        expect(self.page.registeredRepTypeDropdownValue2).to_be_visible()
        expect(self.page.registeredRepTypeDropdownValue3).to_be_visible()
        expect(self.page.registeredRepTypeDropdownValue4).to_be_visible()

    def verify_Lead_Channel_Dependent_Picklist_Values(self):
        self.page.registeredRepTypeDropdown.click()
        self.page.registeredRepTypeDropdownValue2.wait_for(state="visible", timeout=10000)
        self.page.registeredRepTypeDropdownValue2.click()
        self.page.leadChannelDropdown.click()
        expect(self.page.leadChannelDropdownValue1).to_be_visible()
        expect(self.page.leadChannelDropdownValue2).to_be_visible()
        self.page.leadChannelDropdownValue1.click() # To close the dropdown

        self.page.registeredRepTypeDropdown.click()
        self.page.registeredRepTypeDropdownValue3.wait_for(state="visible", timeout=10000)
        self.page.registeredRepTypeDropdownValue3.click()
        self.page.leadChannelDropdown.click()
        expect(self.page.leadChannelDropdownValue3).to_be_visible()
        expect(self.page.leadChannelDropdownValue4).to_be_visible()
        self.page.leadChannelDropdownValue3.click() # To close the dropdown

        self.page.registeredRepTypeDropdown.click()
        self.page.registeredRepTypeDropdownValue4.wait_for(state="visible", timeout=10000)
        self.page.registeredRepTypeDropdownValue4.click()
        self.page.leadChannelDropdown.click()
        expect(self.page.leadChannelDropdownValue1).to_be_visible()
        expect(self.page.leadChannelDropdownValue2).to_be_visible()
        expect(self.page.leadChannelDropdownValue3).to_be_visible()
        expect(self.page.leadChannelDropdownValue4).to_be_visible()
        # self.page.leadChannelDropdownValue1.click() # To close the dropdown