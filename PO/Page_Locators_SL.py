# Locators for Test Cases Page
URL = "https://dev13.ewealthmanager.com/ewmLogin/account/login"
URL1 = "https://dev13.ewealthmanager.com/NavPageDemo/"
BROWSER = "chrome"
USERNAME = "ssoabralc"
PASSWORD = "QAAdminUser_33a"
USER = "AG1634"

# Locators of CommonWeb Page
UserName_TextBox = "xpath://input[@name='username']"
Password_TextBox = "xpath://input[@name='password']"
Sign_Button = "xpath://input[@value='SIGN IN']"
Search_User_Inputbox = "xpath://span[text()='LookUp UserID']//following::input[1]"
Find_Button = "xpath://input[@value='Find']"
Iframe = "xpath://iframe[@title='Home Content']"
SSO_Link = "xpath://td/a[contains(text(),'sampleagentlogin')]"
Footer = "xpath://div[@class='footer']"

# Locators of Homepage Page
My_Practice_NavOption = "xpath://a[text()='My Practice']"

# Locators of MyClients Page
Iframe_MyClients = "xpath://iframe[@title='My Tracking Items Content']"
Client_List_Breadcrum = "xpath://a[text()='Client List']"
Client_List_Link = "xpath://span[text()='Client List']//parent::li"
My_Clients_NavOption = "xpath://span[contains(text(),'My Clients')]//parent::a"
Client_List_Table = "xpath://table[@id='ClientListGrid']"
Client_Grid_Expand = "xpath://td[text()='TBBK Test 32']//preceding::td[1]/a"
Client_expand_arrow = "xpath://td[text()='Kinecta - Combined Portfolio']//preceding::td/a"
Client_Acct_Regis = "xpath://td[text()='N8U865902']//preceding::a[text()='Kinecta - JW']"
Holding_Tab = "xpath://span[text()='Holdings']//parent::li"
Holdings_By_Asset_Class_Link = "xpath://a[text()='Holdings by Asset Class']"
Activity_Tab = "xpath://span[text()='Activity']//parent::li"
Performance_Tab = "xpath://span[text()='Performance']//parent::li"
GainLoss_Tab = "xpath://span[text()='Gain/Loss']//parent::li"
InvHistory_Tab = "xpath://span[text()='Investment History']//parent::li"
AcctInfo_Tab = "xpath://span[text()='Account Information']//parent::li"
Fees_Tab = "xpath://span[text()='Fees']//parent::li"
OndemandReport_Tab = "xpath://span[text()='On-Demand Report']//parent::li"
