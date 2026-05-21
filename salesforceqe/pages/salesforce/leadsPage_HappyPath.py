from playwright.sync_api import expect
from pages.salesforce.leadsPage_Fields import LeadsPage_Fields
from pages.salesforce.leadsPage_PicklistValues import LeadsPage_PicklistValues

class LeadsPage_HappyPath():
    
    def __init__(self, Page):
        self.page = Page
        self.leadFields = LeadsPage_Fields(Page)
        self.leadPicklistValues = LeadsPage_PicklistValues(Page)
        #self.page.leadOption = self.page.locator("a[title='Leads']")
        self.page.path = self.page.locator("div[dir='ltr']")
        # Save/Cancel buttons are also defined in LeadsPage_ValidationErrors, but
        # define them here too so HappyPath works without ValidationErrors being
        # instantiated first (e.g. in the BDD Lead_Conversion scenario).
        self.page.saveButton = self.page.locator('button[name="SaveEdit"]')
        self.page.cancelButton = self.page.locator('button[name="CancelEdit"]')
        self.page.leadConversionButton = self.page.locator("button[name='Lead.Lead_Conversion']")

    def create_Lead_with_Valid_Data(self, firstName, lastName, email):
        self.page.locator("a[title='Leads']").click()
        self.page.newButton.click()
        self.page.firstNameInput.fill(firstName)
        self.page.lastNameInput.fill(lastName)
        self.page.leadSourceDropdown.focus()
        self.page.leadSourceDropdown.wait_for(state="visible", timeout=5000)
        self.page.leadSourceDropdown.click()
        self.page.wait_for_timeout(2000)
        self.page.leadSourceDropdown2.click()
        self.page.wait_for_timeout(2000)
        self.page.emailInput.fill(email)
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.saveButton.click()
        self.page.wait_for_timeout(5000)
        tabCount = self.page.locator("div[aria-label='Workspaces'] a[role='tab'] ").count()
        if tabCount >= 2:
            self.page.keyboard.press("Shift+W")
            self.page.get_by_role("button", name="Close All").click()
            self.page.wait_for_timeout(10000)
            self.page.locator("a[title='Leads']").click()
        else:
            self.page.keyboard.press("Shift+W")
            self.page.locator("a[title='Leads']").click()
        self.page.locator("a[title='"+firstName + " " + lastName+"']").click()
        self.page.wait_for_selector("[name='primaryField']")
        expect(self.page.locator("[name='primaryField']")).to_have_text(firstName + " " + lastName)

    def verify_Path_On_Leads_Page(self, firstName, lastName):
        expect(self.page.locator("li[data-name='Marketing Qualification']")).to_be_visible()
        self.page.locator("li[data-name='Marketing Qualification']").click()        
        expect(self.page.path).to_have_text("Lead has expressed an interest to ‘buy’ and has engaged with Marketing Content but we don’t know who they are.")
        expect(self.page.locator("li[data-name='Sales Ops Review']")).to_be_visible()
        self.page.locator("li[data-name='Sales Ops Review']").click()
        expect(self.page.path).to_have_text("Lead engaged with BOFU Marketing Content but we need Sales Ops to identify this lead, missing CRD.")
        expect(self.page.locator("li[data-name='Nurture']")).to_be_visible()
        self.page.locator("li[data-name='Nurture']").click()
        expect(self.page.path).to_have_text("The Advisor has been qualified and deemed to be a potential fit for AssetMark, but is not in a buying cycle right now. Advisors in this status should be part of marketing nurture campaigns or Sales drip campaigns.")
        expect(self.page.locator("li[data-name='Actively Being Worked']")).to_be_visible()
        self.page.locator("li[data-name='Actively Being Worked']").click()
        expect(self.page.path).to_have_text("The Sales owner is actively engaged with the advisor to determine if there is a buying opportunity and a sales catalyst. These are typically BOFU leads and assigned to a Sales Cadence.")
        expect(self.page.locator("li[data-name='Unqualified']")).to_be_visible()
        self.page.locator("li[data-name='Unqualified']").click()
        expect(self.page.path).to_have_text("The Advisor has been qualified and deemed not a fit for AMK. The Advisor does not have a reason to be a good fit to partner with AssetMark.")
        expect(self.page.locator("li[data-name='converted']")).to_be_visible()
        self.page.locator("li[data-name='converted']").click()
        expect(self.page.path).not_to_be_visible()