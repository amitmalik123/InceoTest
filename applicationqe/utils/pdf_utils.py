"""
PDF Testing Utilities

Provides utilities for PDF file validation and content extraction.
Requires: PyPDF2 or pypdf library
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFValidator:
    """
    PDF file validation and content extraction.

    Prerequisites:
        pip install PyPDF2
        # or
        pip install pypdf

    Example:
        validator = PDFValidator("document.pdf")
        validator.validate_page_count(min_pages=5)
        text = validator.extract_text()
        validator.assert_text_contains("Invoice")
    """

    def __init__(self, pdf_path: Path):
        """
        Initialize PDF validator.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        self.reader: Optional[PdfReader] = None
        self._initialize_reader()

    def _initialize_reader(self):
        """Initialize PDF reader"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        try:
            # Try PyPDF2 first
            from PyPDF2 import PdfReader

            self.reader = PdfReader(str(self.pdf_path))
            logger.debug(f"PDF loaded with PyPDF2: {self.pdf_path.name}")
        except ImportError:
            try:
                # Fallback to pypdf
                from pypdf import PdfReader

                self.reader = PdfReader(str(self.pdf_path))
                logger.debug(f"PDF loaded with pypdf: {self.pdf_path.name}")
            except ImportError:
                raise ImportError("PDF library not found. Install with: pip install PyPDF2")

    def get_page_count(self) -> int:
        """Get number of pages in PDF"""
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        count = len(self.reader.pages)
        logger.debug(f"PDF has {count} pages")
        return count

    def validate_page_count(
        self,
        expected_count: Optional[int] = None,
        min_pages: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> bool:
        """
        Validate PDF page count.

        Args:
            expected_count: Exact page count
            min_pages: Minimum pages
            max_pages: Maximum pages

        Returns:
            True if validation passes
        """
        actual_count = self.get_page_count()

        if expected_count is not None:
            assert (
                actual_count == expected_count
            ), f"Page count mismatch: expected {expected_count}, got {actual_count}"
            logger.info(f"[OK] Page count matches: {expected_count}")

        if min_pages is not None:
            assert actual_count >= min_pages, f"Too few pages: {actual_count} < {min_pages}"
            logger.debug(f"[OK] Page count >= {min_pages}")

        if max_pages is not None:
            assert actual_count <= max_pages, f"Too many pages: {actual_count} > {max_pages}"
            logger.debug(f"[OK] Page count <= {max_pages}")

        return True

    def extract_text(self, page_num: Optional[int] = None) -> str:
        """
        Extract text from PDF.

        Args:
            page_num: Specific page number (0-indexed), None for all pages

        Returns:
            Extracted text
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        if page_num is not None:
            # Extract from specific page
            if page_num < 0 or page_num >= len(self.reader.pages):
                raise ValueError(f"Invalid page number: {page_num}")

            text = self.reader.pages[page_num].extract_text()
            logger.debug(f"Extracted {len(text)} characters from page {page_num}")
            return text
        else:
            # Extract from all pages
            text = ""
            for page in self.reader.pages:
                text += page.extract_text() + "\n"

            logger.debug(f"Extracted {len(text)} characters from all pages")
            return text

    def extract_text_from_pages(self, start_page: int = 0, end_page: Optional[int] = None) -> str:
        """
        Extract text from page range.

        Args:
            start_page: Start page (0-indexed)
            end_page: End page (exclusive), None for last page

        Returns:
            Extracted text
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        if end_page is None:
            end_page = len(self.reader.pages)

        text = ""
        for page_num in range(start_page, end_page):
            if page_num < len(self.reader.pages):
                text += self.reader.pages[page_num].extract_text() + "\n"

        logger.debug(f"Extracted text from pages {start_page}-{end_page}")
        return text

    def assert_text_contains(
        self, expected_text: str, page_num: Optional[int] = None, case_sensitive: bool = True
    ) -> bool:
        """
        Assert PDF contains specific text.

        Args:
            expected_text: Text to search for
            page_num: Specific page to search (None for all)
            case_sensitive: Case-sensitive search

        Returns:
            True if text found
        """
        actual_text = self.extract_text(page_num)

        if not case_sensitive:
            expected_text = expected_text.lower()
            actual_text = actual_text.lower()

        assert expected_text in actual_text, f"Text '{expected_text}' not found in PDF"

        logger.info(f"[OK] PDF contains text: '{expected_text}'")
        return True

    def assert_text_not_contains(
        self, unwanted_text: str, page_num: Optional[int] = None, case_sensitive: bool = True
    ) -> bool:
        """Assert PDF does not contain specific text"""
        actual_text = self.extract_text(page_num)

        if not case_sensitive:
            unwanted_text = unwanted_text.lower()
            actual_text = actual_text.lower()

        assert unwanted_text not in actual_text, f"Unwanted text '{unwanted_text}' found in PDF"

        logger.info(f"[OK] PDF does not contain: '{unwanted_text}'")
        return True

    def search_text(self, search_text: str, case_sensitive: bool = False) -> List[int]:
        """
        Search for text and return page numbers where found.

        Args:
            search_text: Text to search for
            case_sensitive: Case-sensitive search

        Returns:
            List of page numbers containing text
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        found_pages = []

        for page_num, page in enumerate(self.reader.pages):
            page_text = page.extract_text()

            if not case_sensitive:
                search_text = search_text.lower()
                page_text = page_text.lower()

            if search_text in page_text:
                found_pages.append(page_num)

        logger.debug(f"Text '{search_text}' found on pages: {found_pages}")
        return found_pages

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get PDF metadata.

        Returns:
            Dictionary of metadata
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        metadata = {}

        if hasattr(self.reader, "metadata") and self.reader.metadata:
            for key, value in self.reader.metadata.items():
                metadata[key] = value

        logger.debug(f"PDF metadata: {metadata}")
        return metadata

    def validate_metadata(
        self,
        expected_title: Optional[str] = None,
        expected_author: Optional[str] = None,
        expected_creator: Optional[str] = None,
    ) -> bool:
        """
        Validate PDF metadata.

        Args:
            expected_title: Expected title
            expected_author: Expected author
            expected_creator: Expected creator

        Returns:
            True if validation passes
        """
        metadata = self.get_metadata()

        if expected_title:
            actual_title = metadata.get("/Title") or metadata.get("title", "")
            assert expected_title in str(
                actual_title
            ), f"Title mismatch: expected '{expected_title}', got '{actual_title}'"
            logger.debug(f"[OK] PDF title matches")

        if expected_author:
            actual_author = metadata.get("/Author") or metadata.get("author", "")
            assert expected_author in str(
                actual_author
            ), f"Author mismatch: expected '{expected_author}', got '{actual_author}'"
            logger.debug(f"[OK] PDF author matches")

        if expected_creator:
            actual_creator = metadata.get("/Creator") or metadata.get("creator", "")
            assert expected_creator in str(
                actual_creator
            ), f"Creator mismatch: expected '{expected_creator}', got '{actual_creator}'"
            logger.debug(f"[OK] PDF creator matches")

        return True

    def is_encrypted(self) -> bool:
        """Check if PDF is encrypted/password-protected"""
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        is_enc = self.reader.is_encrypted
        logger.debug(f"PDF encrypted: {is_enc}")
        return is_enc

    def extract_links(self, page_num: Optional[int] = None) -> List[str]:
        """
        Extract hyperlinks from PDF.

        Args:
            page_num: Specific page (None for all)

        Returns:
            List of URLs
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")
        links = []

        pages_to_check = (
            [self.reader.pages[page_num]] if page_num is not None else self.reader.pages
        )

        for page in pages_to_check:
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annotation in annotations:
                    obj = annotation.get_object()
                    if "/A" in obj and "/URI" in obj["/A"]:
                        links.append(obj["/A"]["/URI"])

        logger.debug(f"Extracted {len(links)} links from PDF")
        return links

    def get_file_size_mb(self) -> float:
        """Get PDF file size in MB"""
        size_bytes = self.pdf_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        logger.debug(f"PDF size: {size_mb:.2f} MB")
        return size_mb

    def validate_file_size(
        self, max_size_mb: Optional[float] = None, min_size_mb: Optional[float] = None
    ) -> bool:
        """
        Validate PDF file size.

        Args:
            max_size_mb: Maximum size in MB
            min_size_mb: Minimum size in MB

        Returns:
            True if validation passes
        """
        actual_size = self.get_file_size_mb()

        if max_size_mb is not None:
            assert (
                actual_size <= max_size_mb
            ), f"PDF too large: {actual_size:.2f}MB > {max_size_mb}MB"
            logger.debug(f"[OK] PDF size <= {max_size_mb}MB")

        if min_size_mb is not None:
            assert (
                actual_size >= min_size_mb
            ), f"PDF too small: {actual_size:.2f}MB < {min_size_mb}MB"
            logger.debug(f"[OK] PDF size >= {min_size_mb}MB")

        return True

    def generate_report(self) -> str:
        """Generate PDF validation report"""
        metadata = self.get_metadata()

        report = f"""
ΓòöΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòù
Γòæ                        PDF VALIDATION REPORT                             Γòæ
ΓòÜΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓò¥

File: {self.pdf_path.name}
Path: {self.pdf_path}
Size: {self.get_file_size_mb():.2f} MB
Pages: {self.get_page_count()}
Encrypted: {self.is_encrypted()}

METADATA:
  Title: {metadata.get('/Title', 'N/A')}
  Author: {metadata.get('/Author', 'N/A')}
  Creator: {metadata.get('/Creator', 'N/A')}
  Producer: {metadata.get('/Producer', 'N/A')}

ΓòÜΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓò¥
"""
        return report
