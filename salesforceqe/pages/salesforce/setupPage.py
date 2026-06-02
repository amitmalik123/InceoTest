import time


class Setup:
    def __init__(self, page):
        self.page = page
        
    def login_as_different_user(self, userName):
        self.page.locator("div.setupGear").click()
        with self.page.expect_popup() as popup_info:
            self.page.locator("a[title='Setup']").click()
            newPage = popup_info.value
            newPage.wait_for_load_state()
            newPage.locator("input[title='Search Setup']").fill(userName)
            self.page.wait_for_timeout(3000)
            newPage.get_by_role("link", name=userName).click()
            newPage.frame_locator("div.content > iframe").locator("td#topButtonRow > input:nth-child(4)").click()
            time.sleep(2)