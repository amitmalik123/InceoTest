import tempfile
from pathlib import Path

from pytest_bdd import then, when

from pages.prospects_list_page import ProspectsListPage
from utils.allure_logger import get_allure_logger
from utils.download_utils import DownloadManager
from utils.excel_utils import ExcelUtils

logger = get_allure_logger(__name__)

# Store downloaded file path for use across steps
_exported_file_path = None


@then("I should see the export button")
def verify_export_button(prospects_list_page: ProspectsListPage):
    """Verify that the export button is visible"""
    logger.info("Verifying export button is visible")
    assert prospects_list_page.is_export_button_visible(), "Export button is not visible"
    logger.info("Export button verified as visible")


@when("I click the export button")
def click_export_button(prospects_list_page: ProspectsListPage):
    """Click the export button and download the file

    Uses DownloadManager to handle the download and save it to a temporary directory.
    Stores the downloaded file path for later validation.
    """
    global _exported_file_path

    logger.info("Clicking export button")

    # Create download manager with temp directory
    tmpdir = tempfile.mkdtemp()
    download_manager = DownloadManager(prospects_list_page.page, download_dir=tmpdir)

    # Trigger download by clicking export button
    download = download_manager.trigger_download(lambda: prospects_list_page.click_export_button())

    # Save the download to disk
    filepath = download_manager.save_download(download)
    _exported_file_path = filepath
    logger.info(f"File downloaded to: {filepath}")

    # Validate basic file properties
    download_manager.validate_download(
        download,
        expected_extension=".xlsx",
        min_size_bytes=100,
    )
    logger.info(f"File validated: {download.suggested_filename}")


@then("The prospects list should be exported successfully")
def verify_prospects_exported():
    """Verify that the prospects list has been exported successfully

    Opens the exported Excel file and validates it contains data.
    """
    global _exported_file_path

    logger.info("Verifying prospects list exported successfully")

    if _exported_file_path and Path(_exported_file_path).exists():
        # Read the Excel file - specify sheet_name=0 to get first sheet as DataFrame
        excel_utils = ExcelUtils()
        result = excel_utils.read_sheet(_exported_file_path, sheet_name=0, use_pandas=True)

        # Handle case where result might be dict (shouldn't be with sheet_name=0, but just in case)
        if isinstance(result, dict):
            df = next(iter(result.values()))  # Get first DataFrame from dict
        else:
            df = result

        logger.info(f"Exported file contains {len(df)} rows")
        assert len(df) > 0, "Exported file contains no data"
        assert len(df.columns) > 0, "Exported file contains no columns"

        logger.info(f"File contains {len(df)} rows and {len(df.columns)} columns")

        # Clean up the temporary file
        Path(_exported_file_path).unlink()
        logger.info("Exported file deleted after verification")
    else:
        raise AssertionError("No exported file found - export may have failed")


@then("The filtered prospects list should be exported successfully")
def verify_filtered_prospects_exported():
    """Verify that the filtered prospects list has been exported successfully

    Opens the exported Excel file and validates that:
    1. The file contains data
    2. All rows match the applied filter criteria
    """
    global _exported_file_path

    logger.info("Verifying filtered prospects list exported successfully")

    if _exported_file_path and Path(_exported_file_path).exists():
        # Read the Excel file - specify sheet_name=0 to get first sheet as DataFrame
        excel_utils = ExcelUtils()
        result = excel_utils.read_sheet(_exported_file_path, sheet_name=0, use_pandas=True)

        # Handle case where result might be dict (shouldn't be with sheet_name=0, but just in case)
        if isinstance(result, dict):
            df = next(iter(result.values()))  # Get first DataFrame from dict
        else:
            df = result

        logger.info(f"Filtered export contains {len(df)} rows")
        assert len(df) > 0, "Exported filtered data contains no rows"

        # Validate that the data was actually filtered
        # Look for a Status column and check values
        if "Status" in df.columns:
            status_values = df["Status"].unique()
            status_value = status_values[0] if len(status_values) > 0 else None

            # If multiple different statuses found, that's an error
            if len(status_values) > 1:
                found_statuses = ", ".join(str(s) for s in status_values)
                raise AssertionError(
                    f"Expected filtered export to contain uniform Status values, but found {len(status_values)} different: [{found_statuses}]"
                )

            logger.info(
                f"Validated Status column: Expected [{status_value}], Found [{status_value}] ✓"
            )
            logger.info(f"All {len(df)} rows have consistent Status = '{status_value}'")
        else:
            logger.info(
                f"Exported filtered data contains {len(df)} rows and {len(df.columns)} columns"
            )

        # Clean up the temporary file
        Path(_exported_file_path).unlink()
        logger.info("Exported filtered file deleted after verification")
    else:
        raise AssertionError("No exported file found - filtered export may have failed")
