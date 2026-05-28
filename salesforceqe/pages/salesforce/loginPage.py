import json

class LoginPage:
    def __init__(self, page):
        self.page = page

    def login_to_salesforce_sbx(self, environment):
        with open('data/salesforce/credentials.json') as f:
            credentials = json.load(f)
            if environment == "PwCQA":
                user_credentials = credentials.get("user_credentials", [])[0]
                testEnv = user_credentials["environment"]
                userId = user_credentials["username"]
                password = user_credentials["password"]
            elif environment == "FSCQA":
                user_credentials = credentials.get("user_credentials", [])[1]
                testEnv = user_credentials["environment"]
                userId = user_credentials["username"]
                password = user_credentials["password"]

        self.page.goto(testEnv)
        # If a previous scenario already authenticated this session-scoped
        # browser, Salesforce redirects past the login form. Skip in that case.
        username_field = self.page.locator('input[name="username"]')
        password_field = self.page.locator('input[name="pw"]')
        login_button = self.page.locator("#Login")
        try:
            username_field.wait_for(state="visible", timeout=5000)
            # password_field.wait_for(state="visible", timeout=5000)
            # login_button.wait_for(state="visible", timeout=5000)
        except Exception:
            return  # already logged in
        username_field.fill(userId)
        password_field.fill(password)
        login_button.click()
        

    def logout_from_salesforce_sbx(self):
        # Implement logout logic if needed, e.g., click on user profile and select logout
        self.page.wait_for_timeout(3000)  # wait for any pending operations to complete before logout
        self.page.locator("a[href='/secur/logout.jsp']").click()  # Click on user logout link
              
        