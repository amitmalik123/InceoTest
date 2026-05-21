import os
import requests
from playwright.sync_api import Page
from pages.stp.shared.base_page import BasePage
from pages.stp.shared.locators.item_details_locators import ItemDetailsLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ItemDetailsPage(BasePage):
    """Page object for Item Details Page"""
    
    def __init__(self, page: Page, page_verification: bool = True):
        super().__init__(page)
        loc = ItemDetailsLocators
        
        self.page_label = page.locator(loc.PAGE_LABEL)
        self.description = page.locator(loc.DESCRIPTION)
        self.item_number = page.locator(loc.ITEM_NUMBER)
        self.name = page.locator(loc.NAME)
        self.status = page.locator(loc.STATUS)
        self.closed_on_date = page.locator(loc.CLOSED_ON_DATE)
        self.status_label = page.locator(loc.STATUS_LABEL)
        self.description_label = page.locator(loc.DESCRIPTION_LABEL)
        
        self.description_info = page.locator(loc.DESCRIPTION_INFO)
        self.description_notes = page.locator(loc.DESCRIPTION_NOTES)
        self.created_by = page.locator(loc.DESCRIPTION_NOTES)
        self.time_stamps = page.locator(loc.TIME_STAMPS)
        
        # Item details locators (for validation)
        self.item_details_t11 = page.locator(loc.ITEM_DETAILS_T11)
        
        self.tracking_center_tab = page.locator(loc.TRACKING_CENTER_TAB)
        
        # View Documents elements
        self.view_button = page.locator(loc.VIEW_BUTTON)
        self.view_documents_header_popup = page.locator(loc.VIEW_DOCUMENTS_HEADER)
        self.view_documents_pdf_list_table = page.locator(loc.VIEW_DOCUMENTS_PDF_LIST)
        self.view_documents_file_links = page.locator(loc.VIEW_DOCUMENTS_FILE_LINKS)
        self.close_button = page.locator(loc.CLOSE_BUTTON)
        
        if page_verification:
            self._verify_page_loaded()
    
    def _verify_page_loaded(self):
        """Verify the item details page has loaded"""
        page_name = "Item Details Page"
        try:
            self.page.wait_for_load_state('networkidle', timeout=45000)
            self.page.wait_for_timeout(2000)
            
            is_visible = self.page_label.is_visible(timeout=20000)
            
            if is_visible:
                logger.info(f"{page_name} verification: PASSED")
            else:
                logger.warning(f"{page_name} verification: FAILED")
        except Exception as e:
            logger.error(f"{page_name} verification failed with error: {e}")
    
    def get_item_number(self) -> str:
        """Get the item number"""
        logger.info("Getting item number")
        item_num = self.item_number.inner_text()
        logger.info(f"Item number: {item_num}")
        return item_num
    
    def get_description(self) -> str:
        """Get the description"""
        logger.info("Getting description")
        desc = self.description.inner_text()
        logger.info(f"Description: {desc}")
        return desc
    
    def get_account_name(self) -> str:
        """Get the account name"""
        logger.info("Getting account name")
        name = self.name.inner_text()
        logger.info(f"Account name: {name}")
        return name
    
    def get_status(self) -> str:
        """Get the status"""
        logger.info("Getting status")
        status = self.status.inner_text()
        logger.info(f"Status: {status}")
        return status
    
    def get_closed_on_date(self) -> str:
        """Get the Closed On date from item details page"""
        logger.info("Getting Closed On date")
        self.closed_on_date.wait_for(state="visible", timeout=10000)
        closed_date = self.closed_on_date.inner_text()
        logger.info(f"Closed On Date: {closed_date}")
        return closed_date
    
    def get_status_label(self) -> str:
        """Get the Status label from item details page"""
        logger.info("Getting Status label")
        status_text = self.status_label.inner_text()
        logger.info(f"Status: {status_text}")
        return status_text
    
    def get_description_label(self) -> str:
        """Get the Description label from item details page"""
        logger.info("Getting Description label")
        desc_text = self.description_label.inner_text()
        logger.info(f"Description: {desc_text}")
        return desc_text
    
    def get_first_distribution_notes(self) -> str:
        """Get the first distribution notes from tracking center"""
        logger.info("Getting first distribution notes")
        
        elements = self.description_info.all()
        size = len(elements)
        logger.info(f"Found {size} description info elements")
        
        if size > 0:
            notes = elements[-1].inner_text()
            logger.info(f"First distribution notes: {notes}")
            return notes
        
        return ""
    
    def get_created_by_from_notes_section(self) -> str:
    
        logger.info("Getting created by from notes section")
        created_by_text = self.created_by.inner_text()
        logger.info(f"Created by text: {created_by_text}")
        return created_by_text
    
    def get_email_notification_for_method(self, method: str) -> str:
        
        logger.info(f"Getting email notification for method: {method}")
        notification_text = ""
        
        if method == "AddACH NoEsign":
            # Refresh page up to 8 times until notification is found
            for attempt in range(8):
                logger.info(f"Refresh attempt {attempt + 1}/8 for AddACH NoEsign")
                self.page.reload()
                self.page.wait_for_timeout(3000)
                
                notification_element = self.page.locator(
                    "table#TrackingCenterItemDetailNotesGrid tr td:has-text('An email notification regarding')"
                ).first
                
                try:
                    if notification_element.is_visible(timeout=5000):
                        break
                except:
                    continue
            
            # Wait for and get the notification text
            notification_element = self.page.locator(
                "table#TrackingCenterItemDetailNotesGrid tr td:has-text('An email notification regarding')"
            ).first
            notification_element.wait_for(state="visible", timeout=30000)
            notification_text = notification_element.text_content()
            
        elif method == "IRA":
            # Refresh and wait for notification
            for attempt in range(4):
                logger.info(f"Refresh attempt {attempt + 1}/4 for IRA")
                self.page.reload()
                notification_element = self.page.locator(
                    "table#TrackingCenterItemDetailNotesGrid tr td:has-text('An email notification regarding')"
                ).first
                
                try:
                    if notification_element.is_visible(timeout=3000):
                        break
                except:
                    continue
            
            notification_element.wait_for(state="visible", timeout=10000)
            notification_text = notification_element.text_content()
            
        elif method == "NON-IRA":
            # Get note from specific position for NON-IRA
            for attempt in range(4):
                logger.info(f"Refresh attempt {attempt + 1}/4 for NON-IRA")
                self.page.reload()
                self.page.wait_for_timeout(500)
                
                descriptions = self.description_info.all()
                if len(descriptions) >= 7:
                    break
            
            descriptions = self.description_info.all()
            size = len(descriptions)
            if size >= 7:
                notification_text = descriptions[size - 5].text_content()
            else:
                notification_text = descriptions[size - 4].text_content()
                
        elif method in ["Roth Conversions Online", "SWP Establish"]:
            # Wait for notification with specific text
            for attempt in range(4):
                logger.info(f"Refresh attempt {attempt + 1}/4 for {method}")
                self.page.reload()
                notification_element = self.page.locator(
                    "td:has-text('An email notification regarding')"
                ).first
                
                try:
                    if notification_element.is_visible(timeout=3000):
                        break
                except:
                    self.page.wait_for_timeout(5000)
                    continue
            
            notification_text = self.page.locator(
                "td:has-text('An email notification regarding')"
            ).first.text_content()
            
        elif method == "AddACH":
            # Keep refreshing until notification is found
            max_attempts = 20
            for attempt in range(max_attempts):
                logger.info(f"Refresh attempt {attempt + 1}/{max_attempts} for AddACH")
                notification_element = self.page.locator(
                    "table#TrackingCenterItemDetailNotesGrid tr td:has-text('An email notification regarding')"
                ).first
                
                try:
                    if notification_element.is_visible(timeout=2000):
                        break
                except:
                    self.page.reload()
                    continue
            
            notification_element = self.page.locator(
                "table#TrackingCenterItemDetailNotesGrid tr td:has-text('An email notification regarding')"
            ).first
            notification_element.wait_for(state="visible")
            notification_text = notification_element.text_content()
            
        elif method == "Admin_Esignature":
            # Admin esignature specific notification
            for attempt in range(4):
                logger.info(f"Refresh attempt {attempt + 1}/4 for Admin_Esignature")
                self.page.reload()
                notification_element = self.page.locator(
                    "td:has-text('An email notification regarding receipt of this request has been sent')"
                ).first
                
                try:
                    if notification_element.is_visible(timeout=3000):
                        break
                except:
                    self.page.wait_for_timeout(5000)
                    continue
            
            notification_text = self.page.locator(
                "td:has-text('An email notification regarding receipt of this request has been sent')"
            ).first.text_content()
        
        logger.info(f"Email notification retrieved: {notification_text}")
        return notification_text
    
    def click_tracking_center_tab(self):
        """Click on Tracking Center tab"""
        logger.info("Clicking Tracking Center tab")
        self.tracking_center_tab.click()
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Tracking Center tab clicked")
    
    def get_item_details_1(self, agent_id: str) -> list:
        """Get item details list 1 based on agent ID"""
        logger.info(f"Getting item details 1 for agent ID: {agent_id}")
        locator = self.page.locator(f"//li[contains(text(),'{agent_id}')]/ancestor::div[contains(@id,'Container')]/descendant::div[contains(@id,'tracking-center-snapshot-container')]/descendant::div/label")
        locator.first.wait_for(state="visible", timeout=10000)
        elements = locator.all()
        texts = [elem.inner_text() for elem in elements]
        logger.info(f"Item details 1: {texts}")
        return texts
    
    def get_item_details_2(self, agent_id: str) -> list:
        """Get item details list 2 based on agent ID"""
        logger.info(f"Getting item details 2 for agent ID: {agent_id}")
        locator = self.page.locator(f"//span[contains(text(),'{agent_id}')]/parent::div/following-sibling::div[2]/child::span")
        locator.first.wait_for(state="visible", timeout=10000)
        elements = locator.all()
        texts = [elem.inner_text() for elem in elements]
        logger.info(f"Item details 2: {texts}")
        return texts

    def get_item_details_1_prod(self) -> list:
        """PROD: Get item details list 1 by reading labeled fields directly.

        Returns a list matching the expected index positions:
            [0] item_number, [1] account_name, [2] status, [3] closed_on
        """
        logger.info("[PROD] Getting item details list 1")
        item_num = self.item_number.inner_text().strip()
        acct_name = self.name.inner_text().strip()
        status_val = self.page.locator("//span[contains(text(),'Status:')]/following-sibling::label").inner_text().strip()
        closed_locator = self.page.locator("//span[contains(text(),'Closed On:')]/following-sibling::label")
        closed = closed_locator.inner_text().strip() if closed_locator.count() > 0 else ""
        result = [item_num, acct_name, status_val, closed]
        logger.info(f"[PROD] Item details 1: {result}")
        return result

    def get_item_details_2_prod(self) -> list:
        """PROD: Get item details list 2 by reading labeled fields directly.

        Returns a list matching the expected index positions:
            [0] created_on, [1] closed_on, [2] managed_account_number, [3] description
        """
        logger.info("[PROD] Getting item details list 2")
        created = self.page.locator("//span[contains(text(),'Created On:')]/following-sibling::label").inner_text().strip()
        closed_locator = self.page.locator("//span[contains(text(),'Closed On:')]/following-sibling::label")
        closed = closed_locator.inner_text().strip() if closed_locator.count() > 0 else ""
        managed_acct = self.page.locator("//span[contains(text(),'Managed Account Number:')]/following-sibling::label").inner_text().strip()
        desc = self.page.locator("//span[contains(text(),'Description:')]/following-sibling::label").inner_text().strip()
        result = [created, closed, managed_acct, desc]
        logger.info(f"[PROD] Item details 2: {result}")
        return result
    
    def get_item_details_t11(self) -> list:
        """Get item details for test11 environment"""
        logger.info("Getting item details for test11")
        self.item_details_t11.first.wait_for(state="visible", timeout=10000)
        elements = self.item_details_t11.all()
        texts = [elem.inner_text() for elem in elements]
        logger.info(f"Item details t11: {texts}")
        return texts
    
    def fetch_b_item_number(self) -> str:
        """Fetch B item number by refreshing and waiting for description"""
        logger.info("Fetching B item number")
        for attempt in range(60):
            self.page.reload()
            size = self.description_info.count()
            value = self.page.locator("//td[contains(text(),'Your document has been submitted to Operations for review and processing')]").count() > 0
            if size >= 3 and value:
                break
            self.page.wait_for_timeout(5000)
        
        b_number_statement = self.page.locator("//td[contains(text(),'Your document has been submitted to Operations for review and processing')]").inner_text()
        b_item_number = b_number_statement.split("number")[1]
        b_item_number = b_item_number.replace(".", "").strip()
        logger.info(f"B Item Number: {b_item_number}")
        return b_item_number
    
    def get_time_stamps(self) -> list:
       
        logger.info("Getting timestamps from tracking center")
        self.time_stamps.first.wait_for(state="visible", timeout=10000)
        time_stamp_elements = self.time_stamps.all()
        timestamps = [element.inner_text() for element in time_stamp_elements]
        logger.info(f"Found {len(timestamps)} timestamps")
        return timestamps
    
    def click_view_button(self):
        """Click the View button and wait for View Documents popup"""
        logger.info("Clicking View button on Item Details page")
        
        # Wait for view button to be visible and clickable
        self.view_button.wait_for(state="visible", timeout=10000)
        self.page.wait_for_timeout(500)
        
        # Click the view button
        self.view_button.click()
        logger.info("Clicked on View Button")
        
        # Wait for the View Documents popup to appear
        self.view_documents_header_popup.wait_for(state="visible", timeout=5000)
        logger.info("View Documents popup header is visible")
        
        # Wait for the PDF list table to appear
        self.view_documents_pdf_list_table.wait_for(state="visible", timeout=2000)
        logger.info("View Documents PDF list table is visible")
        
        self.page.wait_for_timeout(1000)
    
    def is_view_documents_popup_displayed(self) -> bool:
        """Check if View Documents popup is displayed"""
        logger.info("Checking if View Documents popup is displayed")
        
        try:
            header_displayed = self.view_documents_header_popup.is_visible(timeout=5000)
            pdf_table_displayed = self.view_documents_pdf_list_table.is_visible(timeout=2000)
            
            is_displayed = header_displayed and pdf_table_displayed
            logger.info(f"View Documents popup displayed: {is_displayed}")
            logger.info(f"Header displayed: {header_displayed}, PDF table displayed: {pdf_table_displayed}")
            
            return is_displayed
        except Exception as e:
            logger.error(f"Error checking View Documents popup: {e}")
            return False
    
    def get_amount_of_documents_in_view_popup(self) -> int:
        """Get the count of PDF documents in the View Documents popup"""
        logger.info("Getting amount of documents in View Documents popup")
        
        try:
            # Wait a moment for documents to load
            self.page.wait_for_timeout(1000)
            
            # Count the number of PDF links
            size = self.view_documents_file_links.count()
            logger.info(f"Number of PDF documents found: {size}")
            
            return size
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def click_first_document_in_view_popup(self):
        """Click on the first PDF document link in View Documents popup"""
        logger.info("Clicking on btn - PDF link")
        
        self.view_documents_file_links.first.click()
        logger.info("[OK] Clicking on Btn - PDF link")
        
        self.page.wait_for_timeout(2000)
    
    def click_and_download_pdf_via_api(self, download_path: str):
        """Click PDF link, switch to new window, capture URL, and download via API"""
        import re as _re
        logger.info("Clicking on PDF link and preparing to download via API")

        context = self.page.context
        new_page = None
        pdf_url = None

        # Attach a context-level request listener BEFORE clicking so we never miss
        # the navigation request that fires when the new window opens.
        # In headless Chromium the browser intercepts PDF responses and the page URL
        # stays ":" — but the outgoing request URL is always correct.
        captured_request_urls: list = []

        def _on_request(req):
            if req.url.startswith("http") and req.resource_type == "document":
                captured_request_urls.append(req.url)
                logger.info(f"Captured navigation request URL: {req.url}")

        context.on("request", _on_request)

        try:
            with context.expect_page(timeout=10000) as page_info:
                self.view_documents_file_links.first.click()
                logger.info("[OK] Clicked on PDF link")
            new_page = page_info.value
            logger.info("New window captured via expect_page")

            # Give the page a moment in case the request hasn't fired yet
            if not captured_request_urls:
                new_page.wait_for_timeout(5000)

            # Try page URL first (works in headed/local mode)
            try:
                new_page.wait_for_url(_re.compile(r"^https?://"), timeout=5000)
                pdf_url = new_page.url
                logger.info(f"Captured PDF URL via page URL: {pdf_url}")
            except Exception:
                if captured_request_urls:
                    pdf_url = captured_request_urls[-1]
                    logger.info(f"Captured PDF URL via request event: {pdf_url}")
                else:
                    pdf_url = new_page.url
                    logger.warning(f"No request captured, falling back to page URL: {pdf_url}")

            new_page.close()
            logger.info("Closed new window")

        except Exception as e:
            logger.warning(f"expect_page failed ({e}) — falling back to current tab URL")
            self.page.wait_for_timeout(2000)
            pdf_url = captured_request_urls[-1] if captured_request_urls else self.page.url
        finally:
            # Always remove the context listener to avoid leaking across tests
            context.remove_listener("request", _on_request)

        logger.info(f"Final PDF URL: {pdf_url}")

        # Guard: if URL is not a valid http(s) address, fail early with a clear message
        if not pdf_url or not pdf_url.startswith("http"):
            return {
                "success": False,
                "error": f"Could not capture a valid PDF URL (got: '{pdf_url}'). "
                         "The PDF link may not have opened a new window.",
                "url": pdf_url,
            }
        
        try:
            logger.info(f"Downloading PDF from URL via API: {pdf_url}")
            
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            response = requests.get(pdf_url, cookies=cookies, verify=False, timeout=30)
            response.raise_for_status()
            
            filename = "eSigPDFDownload.pdf"
            if "filename=" in pdf_url:
                filename = pdf_url.split("filename=")[-1].split("&")[0]
            elif pdf_url.endswith(".pdf"):
                filename = pdf_url.split("/")[-1]
            
            os.makedirs(download_path, exist_ok=True)
            
            file_path = os.path.join(download_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"[OK] PDF downloaded successfully via API to: {file_path}")
            logger.info(f"File size: {len(response.content)} bytes")
            
            return {
                "success": True,
                "file_path": file_path,
                "filename": filename,
                "url": pdf_url,
                "size": len(response.content)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download PDF via API: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": pdf_url
            }
        except Exception as e:
            logger.error(f"Unexpected error during PDF download: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": pdf_url
            }
