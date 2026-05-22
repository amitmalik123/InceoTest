class ICTTrackingCenterLocators:
    BODY_CONTENT = {"css": "div#BodyContent"}
    LOGOUT_LINK  = {"role": "link", "name": "Logout"}
    ITEM_NUMBER  = "input#ItemNumber"         # hidden input — use get_attribute('value')
    ITEM_STATUS  = "span:has-text('Status:') + label"  # visible label after Status span
