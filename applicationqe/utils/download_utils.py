"""
Download File Validation Utilities

Provides utilities for handling and validating file downloads.
"""

import hashlib
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, List, Optional

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

    def trigger_download(self, action: Callable, timeout: float = 30.0) -> Download:
        """
        Trigger download and wait for it to start.

        Args:
            action: Action that triggers download (e.g., lambda: page.click("#btn"))
            timeout: Timeout in seconds

        Returns:
            Download object

        Example:
            download = manager.trigger_download(lambda: page.click("#download"))
        """
        with self.page.expect_download(timeout=timeout * 1000) as download_info:
            action()

        download = download_info.value
        logger.info(f"Download started: {download.suggested_filename}")
        return download

    def extract_hrc_number_from_pdf(self, pdf_text: str, keyword: str, pdf_page_count: int = 0) -> str:
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
            after_keyword = search_text[index + len(keyword):].strip()
            match = re.search(r'\b\d{7}\b', after_keyword)
            if match:
                keyword_candidates.append(match.group())
            search_text = search_text[index + len(keyword):]

        # Strategy 2: Also collect all 7-digit numbers from entire PDF
        all_seven_digit = re.findall(r'\b\d{7}\b', pdf_text)

        # Decide which candidates to use
        if keyword_candidates:
            logger.info(f"HRC candidates after '{keyword}' ({len(keyword_candidates)} occurrences): {keyword_candidates}")
            most_common = Counter(keyword_candidates).most_common(1)[0][0]
        elif all_seven_digit:
            logger.info(f"Keyword '{keyword}' not found. Scanning entire PDF text.")
            logger.info(f"All 7-digit numbers in PDF ({len(all_seven_digit)} total): {all_seven_digit}")
            most_common = Counter(all_seven_digit).most_common(1)[0][0]
        else:
            raise RuntimeError(f"No valid 7-digit HRC number found in PDF (keyword='{keyword}').")

        # Count how many times the HRC appears in the full PDF
        hrc_count = all_seven_digit.count(most_common)
        logger.info(f"HRC number '{most_common}' appears {hrc_count} times in PDF")

        # Validate against page count if provided
        if pdf_page_count > 0:
            if hrc_count == pdf_page_count:
                logger.info(f"HRC count matches page count ({pdf_page_count} pages, {hrc_count} occurrences)")
            else:
                logger.warning(
                    f"HRC count mismatch: HRC '{most_common}' appears {hrc_count} times "
                    f"but PDF has {pdf_page_count} pages. Proceeding with most frequent number."
                )

        logger.info(f"HRC number extracted: {most_common}")
        return most_common

    def snapshot_downloaded_pdfs(self) -> set[str]:
        """Take a snapshot of current PDF filenames in download directory."""
        return {pdf.name for pdf in self.download_dir.glob("*.pdf")}

    def _is_file_stable(self, path: Path, stable_seconds: float = 1.0) -> bool:
        """Check file size is stable and non-zero."""
        if not path.exists() or path.suffix.lower() != ".pdf":
            return False

        first_size = path.stat().st_size
        if first_size <= 0:
            return False

        time.sleep(stable_seconds)
        second_size = path.stat().st_size
        return first_size == second_size and second_size > 0

    def wait_for_downloaded_pdf(
        self,
        preferred_filename: str,
        existing_pdf_names: Optional[set[str]] = None,
        timeout_seconds: int = 15,
    ) -> Path:
        """Wait for preferred PDF download, with fallback to any new PDF file."""
        existing_pdf_names = existing_pdf_names or set()
        preferred_path = self.download_dir / preferred_filename
        end_time = time.time() + timeout_seconds

        while time.time() < end_time:
            if preferred_path.exists() and self._is_file_stable(preferred_path):
                return preferred_path

            current_pdfs = sorted(
                self.download_dir.glob("*.pdf"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            new_pdfs = [pdf for pdf in current_pdfs if pdf.name not in existing_pdf_names]

            for pdf in new_pdfs:
                if self._is_file_stable(pdf):
                    return pdf

            time.sleep(1)

        raise RuntimeError(
            f"PDF file not found within {timeout_seconds}s in {self.download_dir}. "
            f"Expected '{preferred_filename}' or any new PDF."
        )

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

    def delete_pdf_file(self, pdf_name: str, test_case_id: str) -> None:
        """
        Copy archive + delete original PDF.
        Mirrors Selenium deletePDFFile(pdfName, testCaseId).
        """
        source_file = self.download_dir / f"{pdf_name}.pdf"
        self.copy_and_delete_pdf(source_file=source_file, pdf_name=pdf_name, test_case_id=test_case_id)

    def copy_and_delete_pdf(self, source_file: Path, pdf_name: str, test_case_id: str) -> None:
        """Copy selected PDFs to archive folder, delete original, and clean old archive files."""
        copy_folder = Path.cwd() / "CopyDocumentFolder"
        copy_folder.mkdir(parents=True, exist_ok=True)

        name_lower = pdf_name.lower()
        should_copy = pdf_name in {"DownloadSeparateDocument", "eSigPDFDownload"} or "toain" in name_lower

        if source_file.exists() and should_copy:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            destination = copy_folder / f"{pdf_name}_{test_case_id}_{timestamp}.pdf"
            shutil.copy2(source_file, destination)
            logger.info(f"Copied PDF to archive: {destination}")

        if source_file.exists():
            source_file.unlink()
            logger.info(f"Deleted original PDF: {source_file}")

        cutoff_time = datetime.now() - timedelta(days=2)
        for archived in copy_folder.glob("*.pdf"):
            modified_at = datetime.fromtimestamp(archived.stat().st_mtime)
            if modified_at < cutoff_time:
                archived.unlink(missing_ok=True)
                logger.info(f"Deleted old archived PDF: {archived.name}")

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

    def wait_for_file(
        self, filename: str, timeout: float = 30.0, poll_interval: float = 0.5
    ) -> Path:
        """
        Wait for file to appear in download directory.

        Args:
            filename: Filename to wait for
            timeout: Timeout in seconds
            poll_interval: Polling interval

        Returns:
            Path to file
        """
        filepath = self.download_dir / filename
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if filepath.exists():
                logger.info(f"File found: {filepath}")
                return filepath
            time.sleep(poll_interval)

        raise TimeoutError(f"File not found within {timeout}s: {filename}")

    def get_file_hash(self, filepath: Path, algorithm: str = "md5") -> str:
        """
        Calculate file hash.

        Args:
            filepath: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)

        Returns:
            File hash as hex string
        """
        hash_obj = hashlib.new(algorithm)

        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)

        file_hash = hash_obj.hexdigest()
        logger.debug(f"{algorithm.upper()} hash: {file_hash}")
        return file_hash

    def validate_file_hash(
        self, filepath: Path, expected_hash: str, algorithm: str = "md5"
    ) -> bool:
        """
        Validate file hash.

        Args:
            filepath: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm

        Returns:
            True if hash matches
        """
        actual_hash = self.get_file_hash(filepath, algorithm)
        assert (
            actual_hash == expected_hash
        ), f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
        logger.info(f"✓ File hash validated ({algorithm})")
        return True

    def read_file_content(self, filepath: Path, encoding: str = "utf-8") -> str:
        """
        Read text file content.

        Args:
            filepath: Path to file
            encoding: Text encoding

        Returns:
            File content as string
        """
        with open(filepath, "r", encoding=encoding) as f:
            content = f.read()
        logger.debug(f"Read {len(content)} characters from {filepath.name}")
        return content

    def read_file_lines(self, filepath: Path, encoding: str = "utf-8") -> List[str]:
        """Read file lines as list"""
        with open(filepath, "r", encoding=encoding) as f:
            lines = f.readlines()
        logger.debug(f"Read {len(lines)} lines from {filepath.name}")
        return lines

    def validate_csv_content(
        self,
        filepath: Path,
        expected_columns: Optional[List[str]] = None,
        min_rows: Optional[int] = None,
        max_rows: Optional[int] = None,
    ) -> bool:
        """
        Validate CSV file content.

        Args:
            filepath: Path to CSV file
            expected_columns: Expected column headers
            min_rows: Minimum number of rows
            max_rows: Maximum number of rows

        Returns:
            True if validation passes
        """
        import csv

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate columns
            if expected_columns:
                actual_columns = reader.fieldnames
                assert set(actual_columns) == set(
                    expected_columns
                ), f"Column mismatch: expected {expected_columns}, got {actual_columns}"
                logger.debug(f"✓ CSV columns match")

            # Count rows
            rows = list(reader)
            row_count = len(rows)

            # Validate row count
            if min_rows:
                assert row_count >= min_rows, f"Too few rows: {row_count} < {min_rows}"
                logger.debug(f"✓ Row count >= {min_rows}")

            if max_rows:
                assert row_count <= max_rows, f"Too many rows: {row_count} > {max_rows}"
                logger.debug(f"✓ Row count <= {max_rows}")

            logger.info(f"✓ CSV validated: {row_count} rows")

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

<<<<<<< HEAD
=======
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

>>>>>>> 7a228f8045f20942a4490c9ac3f8553bb22255bd
    def get_file_size_mb(self, filepath: Path) -> float:
        """Get file size in MB"""
        size_bytes = filepath.stat().st_size
        return size_bytes / (1024 * 1024)

    def validate_json_content(self, filepath: Path, schema: Optional[dict] = None) -> dict:
        """
        Validate JSON file content.

        Args:
            filepath: Path to JSON file
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON content
        """
        import json

        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)

        if schema:
            # Optional: JSON schema validation
            # Requires jsonschema library
            try:
                import jsonschema

                jsonschema.validate(instance=content, schema=schema)
<<<<<<< HEAD
                logger.debug("[OK] JSON schema validated")
            except ImportError:
                logger.warning("jsonschema library not installed, skipping schema validation")

        logger.info(f"[OK] JSON file validated: {filepath.name}")
=======
                logger.debug("✓ JSON schema validated")
            except ImportError:
                logger.warning("jsonschema library not installed, skipping schema validation")

        logger.info(f"✓ JSON file validated: {filepath.name}")
>>>>>>> 7a228f8045f20942a4490c9ac3f8553bb22255bd
        return content
