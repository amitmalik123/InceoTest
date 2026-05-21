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
        self.page.fill('input[name="username"]', userId)
        self.page.fill('input[name="pw"]', password)
        self.page.click("#Login")
