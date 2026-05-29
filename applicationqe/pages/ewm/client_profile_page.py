from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)

class ClientProfilePage(BasePage):
    PAGE_PATH = "DNeWM/NBT/Profile/Profile.aspx"
    donor_advisor_name: str = ""  # Store donor advisor name for later use

    def __init__(self, page: Page):
        super().__init__(page)
        # Automatically detect active root at runtime based on iframe presence
        self.profile_frame = self.active_root()
        self.client_type_dropdown: Locator = self.profile_frame.locator('#ctl00_cphContentArea_ddlClientType')
        self.clientType_Personal: Locator = self.profile_frame.locator('option[value="3400"]')
        self.clientType_Corporate: Locator = self.profile_frame.locator('option[value="3401"]')
        self.clientType_JointFamily: Locator = self.profile_frame.locator('option[value="3402"]')
        self.clientType_DonorAdvisedFund: Locator = self.profile_frame.locator('option[value="3403"]')
        self.first_name_input: Locator = self.profile_frame.locator('#ctl00_cphContentArea_txtFirstName')
        self.last_name_input: Locator = self.profile_frame.locator('#ctl00_cphContentArea_txtLastName')
        self.client_name_input: Locator = self.profile_frame.locator('#ctl00_cphContentArea_txtClientName')
        self.risk_low: Locator = self.profile_frame.locator("[id=\"336\"]")
        self.risk_moderate: Locator = self.profile_frame.locator("[id=\"337\"]")
        self.risk_high: Locator = self.profile_frame.locator("[id=\"338\"]")
        self.risk_very_high: Locator = self.profile_frame.locator("[id=\"339\"]")
        self.horizon_2yrs_or_less: Locator = self.profile_frame.locator("[id=\"340\"]")
        self.horizon_3to5yrs: Locator = self.profile_frame.locator("[id=\"341\"]")
        self.horizon_6to10yrs: Locator = self.profile_frame.locator("[id=\"342\"]")
        self.horizon_10yrs_or_more: Locator = self.profile_frame.locator("[id=\"343\"]")
        self.percentage_over75: Locator = self.profile_frame.locator("[id=\"344\"]")
        self.percentage_50to75: Locator = self.profile_frame.locator("[id=\"345\"]")
        self.percentage_25to50: Locator = self.profile_frame.locator("[id=\"346\"]")
        self.percentage_under25: Locator = self.profile_frame.locator("[id=\"347\"]")
        self.investment_conservative: Locator = self.profile_frame.get_by_role("radio", name="-Conservative")
        self.investment_moderateConservative: Locator = self.profile_frame.get_by_role("radio", name="-Moderate Conservative")
        self.investment_moderate: Locator = self.profile_frame.get_by_role("radio", name="3-Moderate")
        self.investment_moderateGrowth: Locator = self.profile_frame.get_by_role("radio", name="-Moderate Growth")
        self.investment_growth: Locator = self.profile_frame.get_by_role("radio", name="-Growth")
        self.investment_maximum_growth: Locator = self.profile_frame.get_by_role("radio", name="-Maximum Growth")
        self.fiduciary_role_label: Locator = self.profile_frame.locator("#ctl00_cphContentArea_lblFuduciaryRole")
        self.next_button: Locator = self.profile_frame.get_by_role("button", name="Next")
    def _get_fiduciary_role_option_label(self, role: str) -> Locator:
        return self.profile_frame.locator(f"//label[text()='{role}']")

    def _select_radio_with_verification(self, radio: Locator, label: str) -> None:
        """Click radio and verify state change for custom-wired controls."""
        self.click(radio)
        if not radio.is_checked():
            raise RuntimeError(f"Radio state did not change for '{label}'")


       
    def client_Type(self, client_type: str) -> None:
        """Select client type from dropdown by visible text (Personal, Corporate, Joint/Family, Donor Advised Fund)"""
        logger.info(f"Selecting client type: {client_type}")
        self.client_type_dropdown.wait_for(state="visible", timeout=10000)
        value_map = {
            "Personal": "3400",
            "Corporate": "3401",
            "Joint/Family": "3402",
            "Donor Advised Fund": "3403",
        }

        self.close_chat_popups()
        value = value_map.get(client_type)
        if value is None:
            raise ValueError(f"Unknown client type: {client_type}")
        self.client_type_dropdown.select_option(value)
        logger.info(f"Client type selected: {client_type}")

    def fill_client_full_name(self, client_type_data: str, step_name: str) -> str:
        """
        Fill in the client's full name fields based on client type.
        
        Args:
            client_type_data: Type of client (Personal, Corporate, Joint/Family, Donor Advised Fund)
            step_name: Name of the step for logging
            
        Returns:
            str: The generated or filled name
        """
        name_data = f"Test_{self.generate_random_data(5)}"
        surname_data = f"Test_{self.generate_random_data(5)}"
        logger.info(f"Generated User Name: {name_data}")

        # Enter full client name
        if client_type_data.lower().strip() == "personal":
            logger.info(f"{step_name}")
            self.first_name_input.wait_for(state="visible", timeout=10000)
            self.first_name_input.fill(name_data)
            logger.info(f"Filled First Name: {name_data} for {step_name}")
            
            self.last_name_input.wait_for(state="visible", timeout=10000)
            self.last_name_input.fill(surname_data)
            logger.info(f"Filled Last Name: {surname_data} for {step_name}")
            logger.info(f"name is {surname_data} {name_data}")
            return f"{surname_data}, {name_data}"
            
        elif "donor advised" in client_type_data.lower().strip():
            logger.info(f"{step_name}")
            self.client_name_input.wait_for(state="visible", timeout=10000)
            self.client_name_input.fill(name_data)
            logger.info(f"Filled Client Name: {name_data} for {step_name}")
            logger.info(f"name is {name_data}")
            # Store donor advisor name for later use
            ClientProfilePage.donor_advisor_name = name_data
            return name_data
            
        else:
            logger.info(f"{step_name}")
            self.client_name_input.wait_for(state="visible", timeout=10000)
            self.client_name_input.fill(name_data)
            logger.info(f"Filled Client Name: {name_data} for {step_name}")
            logger.info(f"name is {name_data}")
            return name_data

    def select_client_risk_tolerance(self, client_type_data: str, risk_tolerance_data: str, log_message: str) -> None:
        """
        Select client risk tolerance based on client type and risk tolerance value.
        This method is skipped for "Donor Advised Fund" client type.
        
        Args:
            client_type_data: Type of client (Personal, Corporate, Joint/Family, Donor Advised Fund)
            risk_tolerance_data: Risk tolerance level (low, moderate, high, very high)
            log_message: Message to log
        """
        if client_type_data.lower().strip() != "donor advised fund":
            risk_level = risk_tolerance_data.lower().strip()
            
            if risk_level == "low":
                logger.info(f"{log_message} : {client_type_data}")
                self.risk_low.wait_for(state="visible", timeout=5000)
                self.risk_low.click()
                logger.info(f"Selected risk tolerance: {risk_tolerance_data}")
            elif risk_level == "moderate":
                logger.info(f"{log_message} : {client_type_data}")
                self.risk_moderate.wait_for(state="visible", timeout=5000)
                self.risk_moderate.click()
                logger.info(f"Selected risk tolerance: {risk_tolerance_data}")
            elif risk_level == "high":
                logger.info(f"{log_message} : {client_type_data}")
                self.risk_high.wait_for(state="visible", timeout=5000)
                self.risk_high.click()
                logger.info(f"Selected risk tolerance: {risk_tolerance_data}")
            elif risk_level == "very high":
                logger.info(f"{log_message} : {client_type_data}")
                self.risk_very_high.wait_for(state="visible", timeout=5000)
                self.risk_very_high.click()
                logger.info(f"Selected risk tolerance: {risk_tolerance_data}")
            else:
                logger.warning(f"Unknown risk tolerance level: {risk_tolerance_data}")
        else:
            logger.info(f"Skipping risk tolerance selection for {client_type_data}")

    def select_client_investment_horizon(self, investment_horizon_data: str, step_name: str) -> None:
        """
        Select client investment horizon based on investment horizon value.
        
        Args:
            investment_horizon_data: Investment horizon (up to 2 years, 3 to 5 years, 6 to 9 years, 10 and more)
            step_name: Name of the step for logging
        """
        logger.info(f"{step_name}")
        horizon_level = investment_horizon_data.strip().lower()
        
        if horizon_level == "up to 2 years":
            self.horizon_2yrs_or_less.wait_for(state="visible", timeout=5000)
            self.horizon_2yrs_or_less.click()
            logger.info(f"Selected investment horizon: {investment_horizon_data}")
            
        elif horizon_level == "3 to 5 years":
            self.horizon_3to5yrs.wait_for(state="visible", timeout=5000)
            self.horizon_3to5yrs.click()
            logger.info(f"Selected investment horizon: {investment_horizon_data}")
            
        elif horizon_level == "6 to 9 years":
            self.horizon_6to10yrs.wait_for(state="visible", timeout=5000)
            self.horizon_6to10yrs.click()
            logger.info(f"Selected investment horizon: {investment_horizon_data}")
            
        elif horizon_level == "10 and more":
            self.horizon_10yrs_or_more.wait_for(state="visible", timeout=5000)
            self.horizon_10yrs_or_more.click()
            logger.info(f"Selected investment horizon: {investment_horizon_data}")
        else:
            logger.warning(f"Unknown investment horizon level: {investment_horizon_data}")

    def select_client_total_net_worth(self, percent_of_client_net_worth: str, step_name: str) -> None:
        """
        Select client total net worth based on percentage of client net worth.
        
        Args:
            percent_of_client_net_worth: Percentage of client net worth (<25, 25to50, 50to75, >75)
            step_name: Name of the step for logging
        """
        logger.info(f"{step_name}")
        percent_level = percent_of_client_net_worth.strip()
        
        if percent_level == "<25":
            self.percentage_under25.wait_for(state="visible", timeout=5000)
            self.percentage_under25.click()
            logger.info(f"Selected net worth percentage: {percent_of_client_net_worth}")
            
        elif percent_level == "25to50":
            self.percentage_25to50.wait_for(state="visible", timeout=5000)
            self.percentage_25to50.click()
            logger.info(f"Selected net worth percentage: {percent_of_client_net_worth}")
            
        elif percent_level == "50to75":
            self.percentage_50to75.wait_for(state="visible", timeout=5000)
            self.percentage_50to75.click()
            logger.info(f"Selected net worth percentage: {percent_of_client_net_worth}")
            
        elif percent_level == ">75":
            self.percentage_over75.wait_for(state="visible", timeout=5000)
            self.percentage_over75.click()
            logger.info(f"Selected net worth percentage: {percent_of_client_net_worth}")
        else:
            logger.warning(f"Unknown net worth percentage level: {percent_of_client_net_worth}")

    def select_client_risk_profile(self, risk_return_profile_data: str, step_name: str) -> None:
        """
        Select client risk/return profile based on risk profile value.
        
        Args:
            risk_return_profile_data: Risk/return profile (Conservative, Moderate Conservative, Moderate, Moderate Growth, Growth, Maximum Growth)
            step_name: Name of the step for logging
        """
        logger.info(f"{step_name}")
        profile_level = risk_return_profile_data.strip()
    
        if profile_level == "Conservative":
            self._select_radio_with_verification(self.investment_conservative, "Conservative")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
            
        elif profile_level == "Moderate Conservative":
            self._select_radio_with_verification(self.investment_moderateConservative, "Moderate Conservative")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
            
        elif profile_level == "Moderate":
            self._select_radio_with_verification(self.investment_moderate, "Moderate")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
            
        elif profile_level == "Moderate Growth":
            self._select_radio_with_verification(self.investment_moderateGrowth, "Moderate Growth")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
            
        elif profile_level == "Growth":
            self._select_radio_with_verification(self.investment_growth, "Growth")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
            
        elif profile_level == "Maximum Growth":
            self._select_radio_with_verification(self.investment_maximum_growth, "Maximum Growth")
            logger.info(f"Selected risk profile: {risk_return_profile_data}")
        else:
            logger.warning(f"Unknown risk profile level: {risk_return_profile_data}")

    def select_fiduciary_role(self, role: str, step_name: str = "Fiduciary Role: ", log_message: str = "select fiduciary role") -> None:
        """
        Select fiduciary role if visible on the page.
        
        Args:
            role: The fiduciary role to select (e.g., "Fiduciary", "Non-Fiduciary")
            step_name: Name of the step for logging
            log_message: Log message to display
        """
        try:
            # Check if the fiduciary role label element is visible
            if self.fiduciary_role_label.is_visible(timeout=1000):
                logger.info(f"{step_name} : {log_message}")
                
                # Click on the label with matching text for the role
                role_label = self._get_fiduciary_role_option_label(role)
                role_label.wait_for(state="visible", timeout=5000)
                role_label.click()
                
                logger.info(f"Select fiduciary role: {role}")
                logger.info(f"Successfully selected fiduciary role: {role}")
            else:
                logger.info("Fiduciary role element not visible, skipping fiduciary role selection")
        except Exception as e:
            logger.warning(f"Could not select fiduciary role '{role}': {str(e).splitlines()[0]}")
            # Continue execution even if fiduciary role selection fails

    def click_next_button(self) -> None:
        """
        Click the next button on the client profile page to proceed to the next step.
        """
        logger.info("Clicking next button on client profile page")
        self.click(self.next_button)
        logger.info("Next button clicked successfully")