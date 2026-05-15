import os
import time
import allure
from pathlib import Path
from pytest_bdd import parsers, then, when
from utils.logger import setup_logger
from tests.conftest import DOWNLOAD_PATH

logger = setup_logger(__name__)


@then(parsers.parse('User should verify PDF is displayed as "{pdf_name}"'))
def verify_pdf_is_displayed(pdf_name: str, test_context: dict):
    """Verify that the PDF file is displayed/downloaded"""
    with allure.step(f"Verify PDF is displayed as {pdf_name}"):
        logger.info("\n")
        
        # Reuse the same DOWNLOAD_PATH constant used when saving the file
        file_path = Path(DOWNLOAD_PATH) / f"{pdf_name}.pdf"
        
        logger.info(f"Looking for PDF at: {file_path}")
        
        # Wait for file to exist with retry mechanism (up to 10 attempts)
        attempts = 0
        max_attempts = 10
        
        while not file_path.exists() and attempts < max_attempts:
            logger.info(f"Waiting for PDF to download... Attempt {attempts + 1}/{max_attempts}")
            time.sleep(1)
            attempts += 1
        
        if file_path.exists():
            logger.info("[OK] Selected document(s) are available and downloaded")
            
            assert file_path.exists(), "PDF should be displayed"
            logger.info(f"[OK] PDF file verified: {pdf_name}.pdf")
            
            # Get file size for reporting
            file_size = file_path.stat().st_size
            logger.info(f"PDF file size: {file_size} bytes")
            
            allure.attach(
                f"PDF file '{pdf_name}.pdf' is available at: {file_path}\nFile size: {file_size} bytes",
                name="PDF Verification Details",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            error_msg = f"PDF should be displayed. File not found after {max_attempts} attempts: {pdf_name}.pdf"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        
        logger.info("\n")


@then(parsers.parse('User should delete PDF displayed as "{pdf_name}"'))
def delete_downloaded_pdf(pdf_name: str, test_context: dict):
    """Delete the downloaded PDF file"""
    with allure.step(f"Delete PDF displayed as {pdf_name}"):
        logger.info("\n")
        
        # Reuse the same DOWNLOAD_PATH constant used when saving the file
        file_path = Path(DOWNLOAD_PATH) / f"{pdf_name}.pdf"
        
        logger.info(f"Looking for PDF at: {file_path}")
        
        # Check if the file exists
        if file_path.exists():
            logger.info("Selected document(s) are available and downloaded")
            logger.info("[OK] Selected document(s) are available and downloaded")
            
            # Delete the file
            try:
                file_path.unlink()
                logger.info("Downloaded file has been deleted")
                logger.info(f"[OK] Successfully deleted PDF: {pdf_name}.pdf")
                
                allure.attach(
                    f"PDF file '{pdf_name}.pdf' was successfully deleted from: {file_path}",
                    name="PDF Deletion Details",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                raise AssertionError(f"Failed to delete PDF file: {pdf_name}.pdf. Error: {e}")
        else:
            logger.warning(f"PDF file not found at: {file_path}")
            logger.warning(f"File does not exist: {pdf_name}.pdf")
            
            allure.attach(
                f"PDF file '{pdf_name}.pdf' was not found at: {file_path}",
                name="PDF Not Found",
                attachment_type=allure.attachment_type.TEXT
            )
        
        logger.info("\n")
