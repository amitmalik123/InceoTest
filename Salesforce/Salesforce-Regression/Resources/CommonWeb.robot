*** Settings ***
Library        Browser
Variables      ../PageObjects/Locators.py



**** Keywords ***
Start Salesoforce Testing Session
    New Browser    ${Browser}    headless=True    args=["--start-maximized"]        
    New Context    ignoreHTTPSErrors=True    viewport=None
    New Page       about:blank
    

End Salesoforce Testing Session
    Close Browser