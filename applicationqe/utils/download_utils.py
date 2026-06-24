"""
Download File Validation Utilities

Provides utilities for handling and validating file downloads.
"""

import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Callable, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from playwright.sync_api import Download, Page

logger = logging.getLogger(__name__)

# Worker-isolated default download directory
_WORKER_ID = os.environ.get("PYTEST_XDIST_WORKER", "master")
_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _get_default_download_dir() -> str:
    """Load download directory from pyproject.toml [tool.downloads]."""
    try:
        with open(_PYPROJECT_PATH, "rb") as f:
            config = tomllib.load(f)
        return config.get("tool", {}).get("downloads", {}).get("download_dir", "reports/downloads")
    except Exception:
        return "reports/downloads"


_DEFAULT_DOWNLOAD_DIR = f"{_get_default_download_dir()}/{_WORKER_ID}"


class DownloadManager:
    """
    Manage file downloads and validation.

    Example:
        manager = DownloadManager(page, download_dir="downloads")
        download = manager.trigger_download(lambda: page.click("#download-btn"))
        manager.validate_download(download, expected_extension=".pdf")
    """

    def __init__(self, page: Page, download_dir: str = _DEFAULT_DOWNLOAD_DIR):
        self.page = page
        # Resolve to absolute path so it matches the browser launch downloads_path
        # regardless of which directory pytest is invoked from (local, headed, pipeline)
        self.download_dir = Path(download_dir).resolve()
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def extract_hrc_number_from_pdf(
        self, pdf_text: str, keyword: str, pdf_page_count: int = 0
    ) -> str:
        """
        Extract 7-digit HRC number from PDF text.
        The HRC number appears on every page, so if a PDF has 20 pages,
        the HRC should appear 20 times as the most frequent 7-digit number.

        Strategy:
        1. Find all keyword occurrences and extract 7-digit numbers after each.
        2. If keyword not found, fall back to the most frequent 7-digit number in entire PDF.
        3. Validate that the HRC count matches page count (if provided).
        """
        from collections import Counter

        # Strategy 1: Extract 7-digit numbers after each keyword occurrence
        keyword_candidates: list[str] = []
        search_text = pdf_text
        while True:
            index = search_text.find(keyword)
            if index == -1:
                break
            after_keyword = search_text[index + len(keyword) :].strip()
            match = re.search(r"\b\d{7}\b", after_keyword)
            if match:
                keyword_candidates.append(match.group())
            search_text = search_text[index + len(keyword) :]

        # Strategy 2: Also collect all 7-digit numbers from entire PDF
        all_seven_digit = re.findall(r"\b\d{7}\b", pdf_text)

        # Decide which candidates to use
        if keyword_candidates:
            logger.info(
                f"HRC candidates after '{keyword}' ({len(keyword_candidates)} occurrences): {keyword_candidates}"
            )
            most_common = Counter(keyword_candidates).most_common(1)[0][0]
        elif all_seven_digit:
            logger.info(f"Keyword '{keyword}' not found. Scanning entire PDF text.")
            logger.info(
                f"All 7-digit numbers in PDF ({len(all_seven_digit)} total): {all_seven_digit}"
            )
            most_common = Counter(all_seven_digit).most_common(1)[0][0]
        else:
            raise RuntimeError(f"No valid 7-digit HRC number found in PDF (keyword='{keyword}').")

        # Count how many times the HRC appears in the full PDF
        hrc_count = all_seven_digit.count(most_common)
        logger.info(f"HRC number '{most_common}' appears {hrc_count} times in PDF")

        # Validate against page count if provided
        if pdf_page_count > 0:
            if hrc_count == pdf_page_count:
                logger.info(
                    f"HRC count matches page count ({pdf_page_count} pages, {hrc_count} occurrences)"
                )
            else:
                logger.warning(
                    f"HRC count mismatch: HRC '{most_common}' appears {hrc_count} times "
                    f"but PDF has {pdf_page_count} pages. Proceeding with most frequent number."
                )

        logger.info(f"HRC number extracted: {most_common}")
        return most_common

    def fetch_pdf_content(self, pdf_name: str, timeout_seconds: int = 15) -> tuple[str, int]:
        """
        Wait for pdf_name.pdf in download directory, extract and return full text and page count.
        Mirrors Selenium fetchPdfContent(pdfName).

        Returns:
            Tuple of (pdf_text, page_count)
        """
        from utils.pdf_utils import PDFValidator

        filepath = self.download_dir / f"{pdf_name}.pdf"
        attempts = 0
        while not filepath.exists() and attempts < timeout_seconds:
            time.sleep(1)
            attempts += 1

        if not filepath.exists():
            raise RuntimeError(f"PDF file not found: {filepath}")

        assert filepath.exists(), "PDF should be displayed"
        validator = PDFValidator(filepath)
        pdf_text = validator.extract_text()
        page_count = validator.get_page_count()
        logger.info(f"PDF content fetched from: {filepath.name} ({page_count} pages)")
        return pdf_text, page_count

    def save_download(
        self, download: Download, filename: Optional[str] = None, overwrite: bool = True
    ) -> Path:
        """
        Save download to disk.

        Args:
            download: Download object
            filename: Optional custom filename
            overwrite: Overwrite if exists

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = download.suggested_filename

        filepath = self.download_dir / filename

        if filepath.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}")

        download.save_as(filepath)
        logger.info(f"Download saved to: {filepath}")
        return filepath

    def get_download_path(self, download: Download) -> Path:
        """Get expected download path"""
        return self.download_dir / download.suggested_filename

    def validate_download(
        self,
        download: Download,
        expected_filename: Optional[str] = None,
        expected_extension: Optional[str] = None,
        min_size_bytes: Optional[int] = None,
        max_size_bytes: Optional[int] = None,
        save: bool = True,
    ) -> bool:
        """
        Validate downloaded file.

        Args:
            download: Download object
            expected_filename: Expected filename
            expected_extension: Expected file extension
            min_size_bytes: Minimum file size
            max_size_bytes: Maximum file size
            save: Save file to disk

        Returns:
            True if validation passes

        Raises:
            AssertionError: If validation fails
        """
        # Save download
        if save:
            filepath = self.save_download(download)
        else:
            filepath = self.get_download_path(download)

        # Validate filename
        if expected_filename:
            actual_filename = download.suggested_filename
            assert (
                actual_filename == expected_filename
            ), f"Filename mismatch: expected '{expected_filename}', got '{actual_filename}'"
            logger.debug(f"✓ Filename matches: {expected_filename}")

        # Validate extension
        if expected_extension:
            actual_extension = Path(download.suggested_filename).suffix
            if not expected_extension.startswith("."):
                expected_extension = f".{expected_extension}"
            assert (
                actual_extension == expected_extension
            ), f"Extension mismatch: expected '{expected_extension}', got '{actual_extension}'"
            logger.debug(f"✓ Extension matches: {expected_extension}")

        # Validate file size
        if save and filepath.exists():
            file_size = filepath.stat().st_size

            if min_size_bytes:
                assert (
                    file_size >= min_size_bytes
                ), f"File too small: {file_size} bytes < {min_size_bytes} bytes"
                logger.debug(f"✓ File size >= {min_size_bytes} bytes")

            if max_size_bytes:
                assert (
                    file_size <= max_size_bytes
                ), f"File too large: {file_size} bytes > {max_size_bytes} bytes"
                logger.debug(f"✓ File size <= {max_size_bytes} bytes")

            logger.info(f"✓ Download validated: {filepath.name} ({file_size} bytes)")

        return True

    def cleanup_downloads(self, older_than_seconds: Optional[float] = None) -> int:
        """
        Clean up download directory.

        Args:
            older_than_seconds: Delete files older than this (None = delete all)

        Returns:
            Number of files deleted
        """
        count = 0
        current_time = time.time()

        for filepath in self.download_dir.iterdir():
            if filepath.is_file():
                if older_than_seconds is None:
                    filepath.unlink()
                    count += 1
                else:
                    file_age = current_time - filepath.stat().st_mtime
                    if file_age > older_than_seconds:
                        filepath.unlink()
                        count += 1

        logger.info(f"Cleaned up {count} files from {self.download_dir}")
        return count

    def close_popup_pages(self, keep_index: int = 0) -> None:
        """
        Close popup pages and return focus to the main page.

        Args:
            keep_index: Index of the page to keep open (default is 0)
        """
        try:
            pages = self.page.context.pages
            if len(pages) <= 1:
                logger.info("No popup pages found")
                return

            for idx, page in enumerate(list(pages)):
                if idx != keep_index:
                    page.close()
                    logger.info(f"Closed popup page: {page.url}")

            pages[keep_index].bring_to_front()
        except Exception as e:
            logger.warning(f"Error closing popup pages: {str(e).splitlines()[0]}")

    def get_file_size_mb(self, filepath: Path) -> float:
        """Get file size in MB"""
        size_bytes = filepath.stat().st_size
        return size_bytes / (1024 * 1024)
