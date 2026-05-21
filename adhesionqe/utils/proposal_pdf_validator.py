"""
Proposal-specific PDF validation utilities.

Extends PDFValidator with helpers for validating Adhesion proposal PDFs,
specifically around Table of Contents page-number extraction.
"""

import logging
import re
from typing import Optional

from utils.pdf_utils import PDFValidator

logger = logging.getLogger(__name__)


class ProposalPDFValidator(PDFValidator):
    """PDFValidator extended with proposal-specific validation helpers."""

    def get_last_toc_page_number(self, toc_page_index: int = 1) -> Optional[int]:
        """Return the page number listed for the last entry in the Table of Contents.

        TOC entries are typically formatted as one of:
            Section Title .............. 12
            Section Title  12

        The method scans the specified page (default: index 1, the second page,
        which is the TOC after the Cover Page) and extracts all trailing integers.
        The largest value is the start page of the final section — a reliable
        minimum page-count floor that adapts to any allocation's data volume.

        Args:
            toc_page_index: 0-based index of the TOC page (default 1).

        Returns:
            The largest page number found in the TOC, or None if none could be parsed.
        """
        if self.reader is None:
            raise ValueError("PDF reader not initialized")

        total_pages = len(self.reader.pages)
        if toc_page_index >= total_pages:
            logger.warning(
                f"TOC page index {toc_page_index} is out of range ({total_pages} pages total)"
            )
            return None

        toc_text = self.reader.pages[toc_page_index].extract_text() or ""
        logger.debug(f"TOC page text (page index {toc_page_index}):\n{toc_text}")

        # Known report titles that appear in TOC entries
        # Used to validate that a number is actually a TOC page reference, not a date/year
        known_report_titles = [
            "Cover Page",
            "Table of Contents",
            "Proposal Summary",
            "Projected Fees Report",
            "Manager Performance Review",
            "Manager Transition Summary",
            "Fee Detail Report",
            "Strategy Performance Review",
            "Proposal Agreement",
            "Holdings Transition Report",
        ]

        # Match lines that look like actual TOC entries:
        # Pattern: meaningful text (at least 3+ chars) + dots/spaces + 1-3 digit page number
        # Examples that should match:
        #   "Proposal Summary ........................ 5"
        #   "Fee Detail Report  12"
        #
        # Regex breakdown:
        #   ^[\s]*           - Start of line + optional whitespace
        #   [A-Za-z][A-Za-z0-9\s:()&,/\-]*  - Starts with letter, contains letters/numbers/punctuation
        #   [.\s]+           - Separator (dots or spaces)
        #   (\d{1,3})        - Capture 1-3 digit page number
        #   \s*$             - Trailing space + end of line
        toc_entries = re.findall(
            r"^[\s]*[A-Za-z][A-Za-z0-9\s:()&,/\-]*[.\s]+(\d{1,3})\s*$", toc_text, re.MULTILINE
        )
        page_numbers = [int(m) for m in toc_entries]

        if not page_numbers:
            logger.warning(
                "TOC pattern found no entries; trying fallback with report title matching"
            )
            # Fallback: search for lines ending in 1-3 digit numbers,
            # but only accept if the text before matches a known report title
            lines = toc_text.split("\n")
            for line in lines:
                match = re.search(r"(\d{1,3})\s*$", line)
                if match:
                    num = int(match.group(1))
                    text_part = line[: match.start()].strip()
                    # Only accept if text matches a known report title (case-insensitive, partial match)
                    if any(title.lower() in text_part.lower() for title in known_report_titles):
                        page_numbers.append(num)
                        logger.debug(f"Fallback match: '{text_part}' -> page {num}")

        if not page_numbers:
            logger.warning("Could not extract any page numbers from TOC")
            return None

        last_page = max(page_numbers)
        logger.info(f"Last TOC section starts on page {last_page}")
        return last_page
