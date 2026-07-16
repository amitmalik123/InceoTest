"""View Documents Step Definitions for BDD tests"""

from pathlib import Path

import requests
from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest_bdd import parsers, then, when

from pages.ewm.docusign_page import DocuSignPage
from pages.ewm.view_documents_page import ViewDocumentsPage
from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.download_utils import _DEFAULT_DOWNLOAD_DIR, DownloadManager
from utils.pdf_utils import PDFValidator

logger = get_allure_logger(__name__)


def _get_separate_documents_button(root) -> Locator:
    return root.get_by_role("button", name="Separate Documents")


def _get_account_establishment_link(root) -> Locator:
    return root.get_by_text("Account Establishment")


def _get_close_modal_button(root) -> Locator:
    return root.get_by_role("button", name="Close")


class ViewDocumentsStep:
    """Helper class for view documents step methods"""

    hrc_number = ""

    def __init__(self, test_context: dict, view_documents_page: ViewDocumentsPage):
        """
        Initialize ViewDocumentsStep

        Args:
            test_context: Test context containing test data
            view_documents_page: ViewDocumentsPage instance
        """
        self.test_context = test_context
        self.view_documents_page = view_documents_page
        self.test_data = test_context.get("test_data", {})
        self.reg_type = None
        self.custodian = None
        self.client_account_type = None
        self.is_esignature_required = None

    def get_reg_type_and_custodian(self):
        """Extract registration type, custodian, and other required data from test data"""
        reg_types = self.test_data.get("RegistrationType", "").split(",")
        if len(reg_types) <= 1:
            self.reg_type = reg_types[0].strip()
        else:
            self.reg_type = reg_types[1].strip()

        self.custodian = self.test_data.get("Custodian", "")
        self.client_account_type = self.test_data.get("ClientAccountType", "")
        self.is_esignature_required = self.test_data.get("ESignatureOption", "")

        logger.info(f"Registration Type: {self.reg_type}, Custodian: {self.custodian}")
        logger.info(
            f"Client Account Type: {self.client_account_type}, eSignature: {self.is_esignature_required}"
        )

    def perform_esignature(self, option: str) -> None:
        self.get_reg_type_and_custodian()

        if "yes" == (self.is_esignature_required or "").strip().lower():
            esignature_eligible = ConstructPortfolioStep.is_esignature_eligible
            advisory_type = ConstructPortfolioStep.is_sub_advisory

            if esignature_eligible:
                option_value = option.strip()
                with logger.step("Start eSignature process", page=self.view_documents_page.page):
                    self.view_documents_page.e_signature_start(
                        option_value, advisory_type, self.custodian, self.test_data
                    )
                docusign_page = DocuSignPage(self.view_documents_page.page)

                if "in person" in option_value.lower() or "by mail" in option_value.lower():
                    with logger.step("Sign documents as Agent", page=docusign_page.page):
                        docusign_page.e_signature_sign(
                            first_name=self.test_data.get("AccountHolderFirstName", ""),
                            second_name=self.test_data.get("AccountHolderLastName", ""),
                            reg_type=self.reg_type,
                            custodian=self.custodian,
                            client_type=self.test_data.get("ClientType", ""),
                            role="Agent",
                            option=option_value,
                            is_sub_advisory=advisory_type,
                        )
                    with logger.step("Verify eSignature status", page=docusign_page.page):
                        docusign_page.verify_e_signature_status(
                            "Agent", option_value, advisory_type
                        )
                else:
                    logger.info("Unknown eSignature option - skipping DocuSign signing")
            else:
                Assertions.assert_false(
                    esignature_eligible,
                    f"eSignature should be ineligible for {self.custodian} and {self.reg_type}",
                )
        else:
            if not self.is_esignature_required or self.is_esignature_required.strip().lower() in [
                "no",
                "na",
            ]:
                logger.info("Skipping step as eSignature option not enabled in data sheet")

    def perform_internal_admin_esignature(self, option: str) -> None:
        """Internal Admin eSign: checkbox + continue + finalize only (no indexed signing),
        then close modal and fetch N number."""
        self.get_reg_type_and_custodian()

        if "yes" != (self.is_esignature_required or "").strip().lower():
            logger.info("Skipping step as eSignature option not enabled in data sheet")
            return

        esignature_eligible = ConstructPortfolioStep.is_esignature_eligible
        advisory_type = ConstructPortfolioStep.is_sub_advisory

        if not esignature_eligible:
            logger.info(f"eSignature ineligible for {self.custodian}/{self.reg_type} - skipping")
            return

        option_value = option.strip()

        with logger.step("Start Internal Admin eSignature", page=self.view_documents_page.page):
            self.view_documents_page.e_signature_start(
                option_value, advisory_type, self.custodian, self.test_data
            )
            docusign_page = DocuSignPage(self.view_documents_page.page)

        with logger.step(
            "Internal Admin DocuSign: checkbox + continue + finalize", page=docusign_page.page
        ):
            docusign_page.page.wait_for_load_state("domcontentloaded", timeout=30000)
            docusign_page.wait_for_timeout(5000)

            docusign_page._handle_checkbox_and_continue(self.custodian, "Agent")
            docusign_page.wait_for_timeout(5000)

            try:
                docusign_page.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                docusign_page.wait_for_timeout(3000)

            docusign_page._finalize_signature()
            docusign_page.wait_for_timeout(5000)

        with logger.step("Close modal and fetch N number", page=docusign_page.page):
            docusign_page.fetch_n_number()
            logger.info(f"N Number: {docusign_page.nNumber}")
            logger.attach_summary_table(
                {"N Number": docusign_page.nNumber}, name="Agent eSignature - N Number"
            )

    def perform_eSignature_finish_later(self, option: str, action: str) -> None:
        self.get_reg_type_and_custodian()

        if "yes" == (self.is_esignature_required or "").strip().lower():
            esignature_eligible = ConstructPortfolioStep.is_esignature_eligible
            advisory_type = ConstructPortfolioStep.is_sub_advisory

            if esignature_eligible:
                option_value = option.strip()
                with logger.step("Start eSignature process", page=self.view_documents_page.page):
                    self.view_documents_page.e_signature_start(
                        option_value, advisory_type, self.custodian, self.test_data
                    )
                docusign_page = DocuSignPage(self.view_documents_page.page)

                if "in person" in option_value.lower() or "by mail" in option_value.lower():
                    with logger.step(
                        f"Agent selects {action} on DocuSign", page=docusign_page.page
                    ):
                        docusign_page.e_signature_sign_tracking_center(
                            first_name=self.test_data.get("AccountHolderFirstName", ""),
                            second_name=self.test_data.get("AccountHolderLastName", ""),
                            reg_type=self.reg_type,
                            custodian=self.custodian,
                            client_type=self.test_data.get("ClientType", ""),
                            role="Agent",
                            option=option_value,
                            is_sub_advisory=advisory_type,
                            action=action,
                        )
                else:
                    logger.info("Unknown eSignature option - skipping DocuSign signing")
            else:
                Assertions.assert_false(
                    esignature_eligible,
                    f"eSignature should be ineligible for {self.custodian} and {self.reg_type}",
                )
        else:
            if not self.is_esignature_required or self.is_esignature_required.strip().lower() in [
                "no",
                "na",
            ]:
                logger.info("Skipping step as eSignature option not enabled in data sheet")


@when("User perform actions on view documents page and fetch require data")
def step_perform_actions_on_view_documents_page(
    test_context, view_documents_page: ViewDocumentsPage
):
    """
    Verify view documents page, click combined documents button, handle PDF download

    Args:
        test_context: Test context containing test data
        view_documents_page: ViewDocumentsPage fixture
    """
    logger.info("Starting view documents actions")

    step_helper = ViewDocumentsStep(test_context, view_documents_page)
    step_helper.get_reg_type_and_custodian()

    investment_solution = step_helper.test_data.get("InvestmentSolution", "")
    amount = step_helper.test_data.get("Amount", "")

    view_documents_page.verify_view_documents_page(
        reg_type=step_helper.reg_type,
        custodian=step_helper.custodian,
        investment=investment_solution,
        amount=amount,
        client_account_type=step_helper.client_account_type,
        is_esignature_eligible=ConstructPortfolioStep.is_esignature_eligible,
    )

    view_documents_page.click_combined_documents_button(
        "Combined document button:",
        "click on one combined document button on view document page",
    )

    download_manager = DownloadManager(view_documents_page.page)
    download_manager.close_popup_pages()

    logger.info("View documents actions completed successfully")


@when(parsers.parse('User does the agent esignature with "{option}" method'))
def step_user_does_esignature(test_context, view_documents_page: ViewDocumentsPage, option: str):
    with logger.step(
        f"User performs agent eSignature with {option} method", page=view_documents_page.page
    ):
        logger.info("Starting eSignature flow")
        test_context["agent_esignature_option"] = option
        step_helper = ViewDocumentsStep(test_context, view_documents_page)
        step_helper.perform_esignature(option)


@when(parsers.parse('User does the internal admin esignature with "{option}" method'))
def step_user_does_internal_admin_esignature(
    test_context, view_documents_page: ViewDocumentsPage, option: str
):
    with logger.step(
        f"Internal Admin eSignature with {option} method", page=view_documents_page.page
    ):
        logger.info("Starting Internal Admin eSignature flow")
        test_context["agent_esignature_option"] = option
        step_helper = ViewDocumentsStep(test_context, view_documents_page)
        step_helper.perform_internal_admin_esignature(option)


@when("User does the agent esignature from outlook using tracking number")
def step_user_does_agent_esignature_from_outlook(
    test_context, view_documents_page: ViewDocumentsPage
):
    with logger.step(
        "Agent eSignature from Outlook using tracking number", page=view_documents_page.page
    ):
        from pages.ewm.docusign_page import DocuSignPage

        step_helper = ViewDocumentsStep(test_context, view_documents_page)
        step_helper.get_reg_type_and_custodian()
        docusign_page = DocuSignPage(view_documents_page.page)
        docusign_page.agentSignature_internal_admin_flow(
            step_helper.reg_type, step_helper.test_data.get("ClientType", ""), step_helper.custodian
        )


@when(parsers.parse('User does the agent esignature with "{option}" method and selects "{action}"'))
def step_user_does_esignature_with_action(
    test_context, view_documents_page: ViewDocumentsPage, option: str, action: str
):
    with logger.step(
        f"User performs agent eSignature with {option} method and selects {action}",
        page=view_documents_page.page,
    ):
        logger.info(f"Starting eSignature flow with action: {action}")
        test_context["agent_esignature_option"] = option
        step_helper = ViewDocumentsStep(test_context, view_documents_page)
        step_helper.perform_eSignature_finish_later(option, action)


@then("validate eSign button is presented on view documents page")
def step_validate_esign_button_presented(view_documents_page: ViewDocumentsPage):
    logger.info("retainAccount is 'Yes', validating eSign button presence")
    Assertions.assert_visible(
        view_documents_page.esignature_button,
        "eSign button should be visible but is not",
        timeout=60000,
    )
    logger.info("G�� eSign button is present on view documents page")


@when("User clicks on Separate Documents and select Accounts Establishment option")
def step_click_separate_documents_and_select_establishment(
    test_context, view_documents_page: ViewDocumentsPage
):
    with logger.step(
        "Click Separate Documents and select Accounts Establishment", page=view_documents_page.page
    ):
        test_data = test_context.get("test_data", {})
        download_manager = DownloadManager(
            view_documents_page.page, download_dir=_DEFAULT_DOWNLOAD_DIR
        )
        main_page = view_documents_page.page
        form_root = view_documents_page.form_root

        # Step 1: Click Separate Documents button
        separate_documents_button = _get_separate_documents_button(form_root)
        separate_documents_button.wait_for(state="visible", timeout=10000)
        separate_documents_button.click()
        main_page.wait_for_timeout(1000)

        # Step 2: Click Account Establishment link � popup opens PDF URL ? Chrome downloads it
        account_establishment_link = _get_account_establishment_link(form_root).first
        account_establishment_link.wait_for(state="visible", timeout=10000)
        account_establishment_link.scroll_into_view_if_needed()

        pdf_save_path = download_manager.download_dir / "DownloadSeparateDocument.pdf"

        # Click link - may open popup OR trigger a download depending on environment
        popup_page = None
        try:
            with main_page.context.expect_page(timeout=15000) as popup_info:
                account_establishment_link.click()
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded", timeout=15000)
            pdf_url = popup_page.url
            logger.info(f"PDF popup URL: {pdf_url}")

            response = main_page.context.request.get(pdf_url)
            pdf_save_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_save_path.write_bytes(response.body())
            logger.info(f"PDF saved via popup: {pdf_save_path} ({pdf_save_path.stat().st_size} bytes)")
        except Exception as popup_err:
            logger.warning(f"Popup not detected ({str(popup_err).splitlines()[0]}), trying download approach")
            with main_page.expect_download(timeout=30000) as download_info:
                account_establishment_link.click()
            download = download_info.value
            pdf_save_path.parent.mkdir(parents=True, exist_ok=True)
            download.save_as(str(pdf_save_path))
            logger.info(f"PDF saved via download: {pdf_save_path} ({pdf_save_path.stat().st_size} bytes)")

        try:
            if popup_page:
                popup_page.close()
        except Exception:
            pass

        logger.info(
            "Successfully clicked Separate Documents and selected Accounts Establishment option"
        )
        try:
            _get_close_modal_button(form_root).first.click()
        except Exception as e:
            logger.warning(f"Could not close modal: {str(e).splitlines()[0]}")
        main_page.bring_to_front()
        pdf_text, pdf_page_count = download_manager.fetch_pdf_content("DownloadSeparateDocument")
        logger.attach_text(pdf_text, name="PDF Extracted Text")
        logger.info(f"PDF has {pdf_page_count} pages")

        hrc_number = download_manager.extract_hrc_number_from_pdf(
            pdf_text, "NEWACCOUNTAPPLICATION", pdf_page_count
        )
        Assertions.assert_is_not_none(hrc_number, "HRC number extracted from PDF (reportId found)")
        ViewDocumentsStep.hrc_number = hrc_number
        test_context["hrc_number"] = hrc_number

        # Verify expected text is present in PDF based on registration type and agent channel
        step_helper = ViewDocumentsStep(test_context, view_documents_page)
        step_helper.get_reg_type_and_custodian()
        logger.attach_summary_table(
            {
                "Username": test_data.get("UserName") or test_data.get("username", ""),
                "Client Full Name": test_context.get("client_full_name", ""),
                "HRC Number": hrc_number,
                "Registration Type": step_helper.reg_type,
                "Custodian": step_helper.custodian,
                "Client Account Type": step_helper.client_account_type,
                "eSignature": step_helper.is_esignature_required,
                "PDF Pages": pdf_page_count,
            },
            name="Test Execution Summary",
        )
        if "Self-Directed_Brokerage_Account" in step_helper.reg_type:
            agent_channel = ConstructPortfolioStep.agent_channel
            if agent_channel == "ADG":
                for text in ["Client", "Agent"]:
                    Assertions.assert_in(text, pdf_text, f"'{text}' is present in PDF")
                    logger.attach_text(f"'{text}' is present in PDF", name=f"{text} Present in PDF")

            elif agent_channel == "IPG":
                for text in ["random"]:
                    Assertions.assert_not_in(
                        text, pdf_text, f"'{text}' is not present in PDF for IPG"
                    )
                    logger.attach_text(
                        f"'{text}' is not present in PDF", name=f"{text} Not Present in PDF"
                    )
                for text in ["hello"]:
                    Assertions.assert_in(text, pdf_text, f"'{text}' is present in PDF for IPG")
                    logger.attach_text(f"'{text}' is present in PDF", name=f"{text} Present in PDF")


@when("User downloads the Accounts Establishment document")
def step_download_accounts_establishment_document(
    test_context, view_documents_page: ViewDocumentsPage
):
    """
    Download the Accounts Establishment document from the Separate Documents list.

    This step clicks on Separate Documents, then clicks on Account Establishment
    to trigger the download, and saves the file with proper naming.

    Args:
        test_context: Test context containing test data
        view_documents_page: ViewDocumentsPage fixture
    """
    with logger.step("Download Accounts Establishment document", page=view_documents_page.page):
        logger.info("Starting document download process")

        test_data = test_context.get("test_data", {})
        test_case_id = test_data.get("Test Case Id", "Unknown")

        main_page = view_documents_page.page
        context = main_page.context
        download_manager = DownloadManager(view_documents_page.page)

        try:
            # Wait 1 minute before attempting download to ensure page is fully loaded

            logger.info("Wait complete, proceeding with download")

            # Step 1: Click Separate Documents button
            logger.info("Clicking Separate Documents button")
            main_page.get_by_role("button", name="Separate Documents").click()
            main_page.wait_for_timeout(3000)

            # Step 2: Extract the download URL from Account Establishment element
            logger.info("Extracting download URL from Account Establishment element")
            download_url = None

            try:
                # Extract the data-url attribute from the Account Establishment link
                download_url = main_page.evaluate(
                    """
                    () => {
                        const elements = document.querySelectorAll('.document-link, [data-url], a');
                        for (let el of elements) {
                            if (el.textContent.includes('Account Establishment')) {
                                return el.getAttribute('data-url') || el.getAttribute('href');
                            }
                        }
                        return null;
                    }
                """
                )

                if download_url:
                    # Construct full URL if relative
                    if not download_url.startswith("http"):
                        from urllib.parse import urljoin

                        download_url = urljoin(main_page.url, download_url)
                    logger.info(f"G�� Download URL extracted: {download_url}")
                else:
                    logger.warning("Could not extract download URL")
            except Exception as e:
                logger.error(f"Failed to extract download URL: {e}")

            # Step 3: Download file using HTTP request with browser cookies
            if download_url:
                logger.info(f"Downloading file from URL using HTTP request: {download_url}")

                try:
                    # Get cookies from browser context
                    cookies = context.cookies()
                    cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

                    # Make HTTP request to download the file
                    response = requests.get(
                        download_url, cookies=cookie_dict, verify=False, timeout=60
                    )

                    if response.status_code == 200:
                        # Save the file
                        custom_filename = "AccountEstablishment.pdf"
                        download_dir = Path(_DEFAULT_DOWNLOAD_DIR)
                        download_dir.mkdir(parents=True, exist_ok=True)
                        saved_path = download_dir / custom_filename

                        with open(saved_path, "wb") as f:
                            f.write(response.content)

                        logger.info(f"G�� Document downloaded successfully: {saved_path}")
                        logger.info(f"G�� File size: {len(response.content)} bytes")

                        # Store download path in context for later use
                        test_context["downloaded_document_path"] = str(saved_path)
                    else:
                        logger.error(
                            f"G�� HTTP request failed with status code: {response.status_code}"
                        )
                        raise Exception(f"Download failed with status code {response.status_code}")

                except Exception as e:
                    logger.error(f"G�� Failed to download using HTTP request: {e}")
                    raise
            else:
                logger.error("No download URL available")
                raise Exception("Could not extract download URL from Account Establishment link")

            # Step 4: Close any popup windows and cleanup (best-effort, browser may already be closed)
            try:
                all_pages = context.pages
                if len(all_pages) > 1:
                    for page in all_pages[1:]:
                        try:
                            page.close()
                            logger.info("Closed popup window")
                        except Exception:
                            pass

                # Close the Separate Documents modal
                main_page.get_by_role("button", name="Close").click()
                logger.info("Closed Separate Documents modal")
            except Exception:
                logger.info(
                    "Browser cleanup skipped - connection already closed (download succeeded via HTTP)"
                )

            logger.info("G�� Document download process completed successfully")

        except Exception as e:
            logger.error(f"G�� Failed to download document: {e}")
            raise


@when("User download the combined document")
def step_download_combined_document(test_context, view_documents_page: ViewDocumentsPage):

    with logger.step("Download combined document", page=view_documents_page.page):
        logger.info("Starting document download process")

        test_data = test_context.get("test_data", {})
        main_page = view_documents_page.page
        context = main_page.context

        try:
            logger.info("Proceeding with combined document download")
            custom_filename = "DownloadCombinedDocuments.pdf"
            download_dir = Path("reports/downloads")
            download_dir.mkdir(parents=True, exist_ok=True)
            saved_path = download_dir / custom_filename
            combined_document_button = main_page.get_by_role("button", name="One Combined Document")

            # Click One Combined Document button and handle a real browser download first.
            logger.info("Clicking One Combined Document button")
            existing_pages = set(context.pages)
            try:
                with main_page.expect_download(timeout=10000) as download_info:
                    combined_document_button.click()

                download = download_info.value
                download.save_as(saved_path)
            except PlaywrightTimeoutError:
                logger.info("No download event; trying popup/direct fetch approach")
                popup_page = None
                new_pages = [page for page in context.pages if page not in existing_pages]

                if new_pages:
                    popup_page = new_pages[-1]

                # Try to get URL from popup if it navigated
                pdf_url = popup_page.url if popup_page else ""
                if not pdf_url or pdf_url.startswith("about:"):
                    # Build the full URL from the button's form (includes hidden inputs as query params)
                    pdf_url = main_page.evaluate("""
                        () => {
                            const btn = document.querySelector('button.combined-button, button[data-url*="CombinedDocuments"]');
                            if (!btn) return null;
                            const form = btn.closest('form');
                            if (form) {
                                // Get form action or button data-url as base
                                let baseUrl = form.action || btn.getAttribute('data-url') || '';
                                // Collect all hidden inputs as query params
                                const inputs = form.querySelectorAll('input[type="hidden"]');
                                const params = new URLSearchParams();
                                inputs.forEach(input => {
                                    if (input.name && input.value) params.append(input.name, input.value);
                                });
                                const paramStr = params.toString();
                                if (paramStr) {
                                    return baseUrl + (baseUrl.includes('?') ? '&' : '?') + paramStr;
                                }
                                return baseUrl;
                            }
                            // No form — just use data-url
                            return btn.getAttribute('data-url') || null;
                        }
                    """)
                    if pdf_url:
                        from urllib.parse import urljoin
                        if not pdf_url.startswith("http"):
                            pdf_url = urljoin(main_page.url, pdf_url)
                        logger.info(f"Built PDF URL from form: {pdf_url}")
                    else:
                        raise RuntimeError("Could not determine download URL from button/form")

                response = context.request.get(pdf_url)
                if response.status != 200:
                    raise RuntimeError(f"PDF request failed with status {response.status}: {pdf_url}")

                saved_path.write_bytes(response.body())
                logger.info(f"PDF saved via direct fetch: {saved_path} ({saved_path.stat().st_size} bytes)")
                try:
                    if popup_page:
                        popup_page.close()
                except Exception:
                    logger.warning("Could not close combined document popup tab")

            logger.info(f"Document downloaded successfully: {saved_path}")
            logger.info(f"File size: {saved_path.stat().st_size} bytes")

            # Verify the file is actually a PDF
            with open(saved_path, "rb") as f:
                header = f.read(10)
            if not header.startswith(b"%PDF"):
                raw_text = saved_path.read_text(encoding="utf-8", errors="replace")[:500]
                logger.error(f"Downloaded file is NOT a valid PDF! Content preview:\n{raw_text}")
                raise RuntimeError(
                    f"Download produced invalid PDF (header: {header!r}). Likely an auth redirect or error page."
                )

            # Store download path in context for later use
            test_context["downloaded_document_path"] = str(saved_path)

            logger.info("Document download process completed successfully")

        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            raise


@then("Validate form bundle documents in downloaded document")
def validate_downloaded_pdf(test_context: dict):
    """Validate expected documents and account number in the downloaded PDF."""
    from config.naw.document_constants import GNW_DOCUMENTS, PRS_DOCUMENTS, get_expected_documents

    retain_account_value = test_context.get("retain_existing_account_boolean", "")
    is_retain = retain_account_value.strip().lower() == "yes"
    custodian = test_context.get("test_data", {}).get("Custodian", "")
    account_number = test_context.get("custodian_account_number")

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    downloaded_document_path = test_context.get("downloaded_document_path")
    if downloaded_document_path:
        pdf_path = Path(downloaded_document_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Downloaded PDF not found: {pdf_path.resolve()}")
    else:
        pyproject = Path("pyproject.toml")
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)
        download_dir = (
            config.get("tool", {}).get("downloads", {}).get("download_dir", "reports/downloads")
        )
        copy_folder = Path(download_dir)
        pdf_files = sorted(copy_folder.glob("*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)

        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {copy_folder.resolve()}")

        pdf_path = pdf_files[0]
        logger.warning(
            "downloaded_document_path missing from context; using latest PDF from download folder"
        )

    logger.info(f"Reading PDF: {pdf_path.name}")
    logger.info(f"File size: {pdf_path.stat().st_size} bytes")

    # Validate file is actually a PDF
    with open(pdf_path, "rb") as f:
        header = f.read(10)
    if not header.startswith(b"%PDF"):
        # Save first 500 chars for debugging
        raw_text = pdf_path.read_text(encoding="utf-8", errors="replace")[:500]
        logger.error(f"Downloaded file is NOT a valid PDF. First 500 chars:\n{raw_text}")
        raise ValueError(
            f"Downloaded file is not a PDF (starts with: {header!r}). Likely an HTML error/login page."
        )

    validator = PDFValidator(pdf_path)
    page_count = validator.get_page_count()
    logger.info(f"PDF has {page_count} page(s)")

    full_text = ""
    for page_num in range(page_count):
        full_text += validator.extract_text(page_num=page_num) + "\n"

    # Save extracted PDF text to file for debugging
    # pdf_text_file = Path("reports/downloads") / f"{pdf_path.stem}_extracted_text.txt"
    # pdf_text_file.parent.mkdir(parents=True, exist_ok=True)
    # pdf_text_file.write_text(full_text, encoding="utf-8")
    # logger.info(f"PDF text saved to: {pdf_text_file}")

    normalized_text = " ".join(full_text.split())

    # Validate expected document names are present in PDF
    expected_documents = list(get_expected_documents(custodian, is_retain))
    custodian_key = custodian.strip().lower()
    if custodian_key in ("gnw", "assetmark trust", "assetmark trust company"):
        expected_documents = list(dict.fromkeys([*expected_documents, *GNW_DOCUMENTS]))
    elif custodian_key in ("prs", "psr", "pershing"):
        expected_documents = list(dict.fromkeys([*expected_documents, *PRS_DOCUMENTS]))

    logger.info(
        f"Validating {len(expected_documents)} expected documents for custodian='{custodian}', retain={is_retain}"
    )

    missing_documents = []
    for doc_name in expected_documents:
        if doc_name not in normalized_text:
            missing_documents.append(doc_name)
            logger.error(f"MISSING: '{doc_name}'")
        else:
            logger.info(f"Found: '{doc_name}'")

    if missing_documents:
        error_msg = (
            f"Missing {len(missing_documents)}/{len(expected_documents)} documents in PDF: {missing_documents}. "
            f"PDF: {pdf_path.name} ({page_count} pages)"
        )
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.info("All expected documents found in PDF")

    # Validate account number if retain account
    if is_retain:
        if not account_number:
            raise ValueError("custodian_account_number not found in test_context")

        logger.info(f"Searching for account number '{account_number}' in PDF")
        Assertions.assert_in(
            account_number,
            normalized_text,
            f"Account number '{account_number}' NOT found in downloaded PDF. "
            f"PDF: {pdf_path.name} ({page_count} pages)",
        )
        logger.info(f"Account number '{account_number}' found in PDF")
