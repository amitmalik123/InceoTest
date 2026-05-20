"""
Download File Validation Utilities

Provides utilities for handling and validating file downloads.
"""

import hashlib
import logging
import time
from pathlib import Path
from typing import Callable, List, Optional

from playwright.sync_api import Download, Page

logger = logging.getLogger(__name__)


class DownloadManager:
    """
    Manage file downloads and validation.

    Example:
        manager = DownloadManager(page, download_dir="downloads")
        download = manager.trigger_download(lambda: page.click("#download-btn"))
        manager.validate_download(download, expected_extension=".pdf")
    """

    def __init__(self, page: Page, download_dir: str = "downloads"):
        self.page = page
        self.download_dir = Path(download_dir)
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
            logger.debug(f"[OK] Filename matches: {expected_filename}")

        # Validate extension
        if expected_extension:
            actual_extension = Path(download.suggested_filename).suffix
            if not expected_extension.startswith("."):
                expected_extension = f".{expected_extension}"
            assert (
                actual_extension == expected_extension
            ), f"Extension mismatch: expected '{expected_extension}', got '{actual_extension}'"
            logger.debug(f"[OK] Extension matches: {expected_extension}")

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
                logger.debug("✓ JSON schema validated")
            except ImportError:
                logger.warning("jsonschema library not installed, skipping schema validation")

        logger.info(f"✓ JSON file validated: {filepath.name}")
        return content
