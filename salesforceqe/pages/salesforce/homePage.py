from pages.salesforce.setupPage import Setup

class Homepage:
    def __init__(self, Page):
        self.page = Page
        self.page.appLauncherButton = self.page.locator('button[title="App Launcher"]')
        self.page.searchAppInput = self.page.locator("input[placeholder='Search apps and items...']")
        self.page.appOption = lambda appName: self.page.get_by_role("option", name=appName)
        self.page.showNavigationMenuButton = self.page.get_by_role("button", name="Show Navigation Menu")
        self.page.leadsTab = self.page.locator("a[data-label='Leads']")

    def navigate_to_app(self, appName):
        self.page.bring_to_front()  # Focuses the current page
        self.page.reload()
        self.page.wait_for_timeout(2000)  # Wait for 2 seconds after reload
        self.page.appLauncherButton.click()
        self.page.searchAppInput.wait_for(state="visible", timeout=5000)  # Waits for the search input to be visible
        #self.page.searchAppInput.fill(appName)
        for attempt in range(3):
            self.page.searchAppInput.fill(appName)
            try:
                self.page.appOption(appName).wait_for(state="visible", timeout=3000)  # Waits for the app option to be visible
                break
            except Exception:
                if attempt == 2:
                    raise
                self.page.wait_for_timeout(500)
        #self.page.appOption(appName).wait_for(state="visible", timeout=10000)  # Waits for the app option to be visible
        self.page.appOption(appName).click()
        self.page.wait_for_timeout(2000)
     
    def access_leads_tab(self):
        self.page.showNavigationMenuButton.click()
        self.page.leadsTab.click()
        self.page.wait_for_timeout(2000)