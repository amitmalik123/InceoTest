"""
PDF Utilities for proposal document validation and download handling.
Full conversion of pdfUtils.ts with exact functionality preservation.

Provides:
- PDF structure validation (header, trailer, page count)
- PDF text content validation (sections, snippets, TOC)
- Safe PDF download from page with multiple fallback mechanisms
- Comprehensive error handling and logging
"""

import logging
import os
import pathlib
import re
import shutil
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProposalSectionSnippetRule:
    """Rule for validating specific text snippets within a proposal section."""

    section: str
    must_contain_all: Optional[list[str]] = None
    must_contain_any: Optional[list[str]] = None
    forbid: Optional[list[str]] = None


@dataclass
class ProposalTextValidationOptions:
    """Options for validating proposal text content."""

    included_sections: list[str]
    excluded_sections: Optional[list[str]] = None
    include_table_of_contents: bool = False
    toc_sections: Optional[list[str]] = None
    section_snippet_rules: Optional[list[ProposalSectionSnippetRule]] = None


def cleanup_downloads() -> None:
    """Remove all files in the downloads directory."""
    download_dir = pathlib.Path(__file__).parent.parent / "downloads"

    if not download_dir.exists():
        return

    try:
        for file_path in download_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
                logger.debug(f"Deleted: {file_path}")
    except Exception as e:
        logger.warning(f"Error during cleanup_downloads: {e}")


def _extract_pdf_page_count(pdf_buffer: bytes) -> Optional[int]:
    """
    Extract page count from PDF buffer by parsing /Count fields.
    Prefers page-tree counts (/Type /Pages with /Count <n>) over generic /Count fields.
    This logic was carefully tuned after troubleshooting various PDF formats.
    """
    pdf_text = pdf_buffer.decode("latin1", errors="ignore")

    # Prefer page-tree counts: /Type /Pages with /Count <n>
    page_tree_pattern = r"/Type\s*/Pages[\s\S]{0,500}?/Count\s+(\d+)"
    page_tree_matches = re.findall(page_tree_pattern, pdf_text)

    if page_tree_matches:
        counts = [int(m) for m in page_tree_matches if int(m) > 0]
        if counts:
            return max(counts)

    # Fallback for files where the above pattern is not found
    generic_pattern = r"/Count\s+(\d+)"
    generic_matches = re.findall(generic_pattern, pdf_text)

    if generic_matches:
        counts = [int(m) for m in generic_matches if int(m) > 0]
        if counts:
            return max(counts)

    return None


def _has_pdf_trailer(pdf_buffer: bytes) -> bool:
    """Check if PDF buffer has proper trailer (%%EOF marker) at the end."""
    start = max(0, len(pdf_buffer) - 1024)
    tail = pdf_buffer[start:].decode("latin1", errors="ignore")
    return "%%EOF" in tail


def _is_likely_pdf_buffer(buffer: bytes) -> bool:
    """Quick check if buffer starts with PDF magic bytes (%PDF-)."""
    if len(buffer) < 5:
        return False
    return buffer[:5].decode("latin1", errors="ignore") == "%PDF-"


def _normalize_text_for_match(value: str) -> str:
    """
    Normalize text for content matching.
    Handles PyPDF2's spaced-out text extraction (e.g., "p u r s u e").
    - Lowercase
    - Replace non-alphanumeric (except %, $) with spaces
    - Remove ALL spaces (to handle spaced-out PDF text)
    - Trim
    """
    normalized = value.lower()
    # Replace non-alphanumeric (except %, $) with spaces
    normalized = re.sub(r"[^a-z0-9%$\s]+", " ", normalized)
    # Remove ALL spaces to match spaced-out PDF text (p u r s u e -> pursue)
    normalized = re.sub(r"\s+", "", normalized)
    return normalized.strip()


def _summarize_list(items: list[str], limit: int = 8) -> str:
    """Create a summary string of list items, truncating if too long."""
    if not items:
        return "(none)"

    displayed = items[:limit]
    suffix = f" (+{len(items) - limit} more)" if len(items) > limit else ""
    return f"{', '.join(displayed)}{suffix}"


def _is_pdf_complete(pdf_path: str, expected_page_count: int) -> bool:
    """
    Quick validation check: file exists, has content, valid header, trailer, and expected page count.
    Returns False on any check failure (fast existence check for polling loops).
    """
    if not os.path.exists(pdf_path):
        return False

    try:
        pdf_buffer = open(pdf_path, "rb").read()
    except Exception:
        return False

    # Reject empty or partial files
    if len(pdf_buffer) <= 1000:
        return False

    # Validate PDF header
    try:
        pdf_header = pdf_buffer[:4].decode("ascii")
    except Exception:
        return False

    if pdf_header != "%PDF":
        return False

    # Require PDF trailer
    if not _has_pdf_trailer(pdf_buffer):
        return False

    # Confirm expected page count
    actual_page_count = _extract_pdf_page_count(pdf_buffer)
    return actual_page_count is not None and actual_page_count >= expected_page_count


def validate_pdf_content(pdf_path: str, expected_page_count: int) -> None:
    """
    Validate that a PDF file exists, has proper structure, and expected page count.

    Args:
        pdf_path: Path to the PDF file.
        expected_page_count: Minimum expected number of pages.

    Raises:
        FileNotFoundError: If PDF file doesn't exist.
        ValueError: If PDF is invalid or has insufficient pages.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    try:
        pdf_buffer = open(pdf_path, "rb").read()
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {e}")

    # Guard against zero-byte or partial files
    if len(pdf_buffer) <= 1000:
        raise ValueError(
            f"PDF file too small ({len(pdf_buffer)} bytes) - likely empty or invalid"
        )

    # Confirm PDF header is present
    try:
        pdf_header = pdf_buffer[:4].decode("ascii")
    except Exception:
        raise ValueError("Unable to read PDF header")

    if pdf_header != "%PDF":
        raise ValueError(f"Invalid PDF header. Expected '%PDF' but got '{pdf_header}'")

    # Require PDF trailer
    if not _has_pdf_trailer(pdf_buffer):
        raise ValueError("PDF file missing trailer (%%EOF) - possibly incomplete")

    # Extract and verify page count
    actual_page_count = _extract_pdf_page_count(pdf_buffer)
    if actual_page_count is None:
        raise ValueError(f"Unable to determine PDF page count for: {pdf_path}")

    if actual_page_count < expected_page_count:
        raise ValueError(
            f"Expected at least {expected_page_count} pages but only found {actual_page_count} in PDF: {pdf_path}"
        )

    logger.debug(
        f"PDF validation passed: {pdf_path} ({len(pdf_buffer)} bytes, {actual_page_count} pages)"
    )


def validate_proposal_pdf_text(
    pdf_path: str, text_validation: ProposalTextValidationOptions
) -> None:
    """
    Extract text from PDF and validate against sections, excluded sections, and snippet rules.

    Uses PyPDF2 to extract text content. Normalizes and validates:
    - Included sections must be present
    - Excluded sections must be absent
    - Snippet rules (mustContainAll, mustContainAny, forbid)
    - Table of contents (if requested)

    Args:
        pdf_path: Path to the PDF file.
        text_validation: Validation options (sections, rules, TOC).

    Raises:
        ValueError: If validation fails.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    try:
        import pypdf
    except ImportError:
        try:
            import PyPDF2 as pypdf  # type: ignore[no-redef]  # PyPDF2 3.x has the same API
        except ImportError:
            import pytest
            pytest.skip(
                "pypdf is not installed — PDF text validation skipped. "
                "Add 'pypdf>=3.0.0' to project dependencies to enable this check."
            )

    try:
        with open(pdf_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            raw_text = ""
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
    except Exception as e:
        raise ValueError(f"Unable to extract text from PDF: {e}")

    if not raw_text.strip():
        raise ValueError(f"Unable to extract text from proposal PDF: {pdf_path}")

    # Log extracted text for debugging
    logger.debug(f"PDF text extraction successful: {len(raw_text)} characters")
    logger.debug(f"First 500 chars of extracted text: {raw_text[:500]}")
    logger.debug(f"Validation options - Included sections: {text_validation.included_sections}")

    normalized_doc = _normalize_text_for_match(raw_text)
    logger.debug(f"Normalized document (first 500 chars): {normalized_doc[:500]}")

    # Validate included sections are present
    normalized_included = [
        {"original": section, "normalized": _normalize_text_for_match(section)}
        for section in text_validation.included_sections
    ]

    found_included = [
        s["original"] for s in normalized_included if s["normalized"] in normalized_doc
    ]
    missing_included = [
        s["original"] for s in normalized_included if s["normalized"] not in normalized_doc
    ]

    # Log which sections were found/missing before raising error
    logger.debug(f"Found included sections: {found_included}")
    logger.debug(f"Missing included sections: {missing_included}")
    
    for section in missing_included:
        normalized_section = _normalize_text_for_match(section)
        logger.debug(f"  Looking for: '{normalized_section}'")
        # Show a snippet of where similar text might be
        if len(normalized_section) > 10:
            snippet = normalized_section[:10]
            if snippet in normalized_doc:
                logger.debug(f"    Partial match found for first 10 chars: '{snippet}'")
            else:
                logger.debug(f"    No partial match found for: '{snippet}'")

    if missing_included:
        raise ValueError(
            f"Proposal section validation failed. "
            f"Expected included sections: {_summarize_list(text_validation.included_sections)}. "
            f"Found included sections: {_summarize_list(found_included)}. "
            f"Missing sections: {_summarize_list(missing_included)}"
        )

    # Validate excluded sections are absent
    normalized_excluded = [
        {"original": section, "normalized": _normalize_text_for_match(section)}
        for section in (text_validation.excluded_sections or [])
    ]

    present_excluded = [
        s["original"]
        for s in normalized_excluded
        if s["normalized"] and s["normalized"] in normalized_doc
    ]

    if present_excluded:
        raise ValueError(
            f"Proposal excluded-section validation failed. "
            f"Expected excluded sections not present: "
            f"{_summarize_list([s['original'] for s in normalized_excluded])}. "
            f"Found excluded sections in document: {_summarize_list(present_excluded)}"
        )

    # Validate snippet rules
    if text_validation.section_snippet_rules:
        for rule in text_validation.section_snippet_rules:
            # Verify the section this rule refers to is in the included list
            normalized_section_name = _normalize_text_for_match(rule.section)
            section_is_included = any(
                s["normalized"] == normalized_section_name for s in normalized_included
            )

            if not section_is_included:
                # Skip rules for sections that aren't included in this proposal
                continue

            # Check mustContainAll snippets
            must_contain_all = [_normalize_text_for_match(s) for s in (rule.must_contain_all or [])]
            missing_all = [s for s in must_contain_all if s and s not in normalized_doc]

            if missing_all:
                found_required = [
                    s
                    for s in (rule.must_contain_all or [])
                    if _normalize_text_for_match(s) in normalized_doc
                ]
                raise ValueError(
                    f"Proposal snippet validation failed for section '{rule.section}'. "
                    f"Expected required snippets: {_summarize_list(rule.must_contain_all or [])}. "
                    f"Found required snippets: {_summarize_list(found_required)}. "
                    f"Missing required snippets: {_summarize_list([s for s in (rule.must_contain_all or []) if _normalize_text_for_match(s) in missing_all])}"
                )

            # Check mustContainAny snippets
            must_contain_any = [_normalize_text_for_match(s) for s in (rule.must_contain_any or [])]
            any_candidates = [s for s in must_contain_any if s]

            if any_candidates and not any(s in normalized_doc for s in any_candidates):
                found_any = [
                    s
                    for s in (rule.must_contain_any or [])
                    if _normalize_text_for_match(s) in normalized_doc
                ]
                raise ValueError(
                    f"Proposal any-of snippet validation failed for section '{rule.section}'. "
                    f"Expected one of: {_summarize_list(rule.must_contain_any or [])}. "
                    f"Found matches: {_summarize_list(found_any)}"
                )

            # Check forbid snippets
            forbid = [_normalize_text_for_match(s) for s in (rule.forbid or [])]
            forbidden_hits = [s for s in forbid if s and s in normalized_doc]

            if forbidden_hits:
                raise ValueError(
                    f"Proposal forbidden-snippet validation failed for section '{rule.section}'. "
                    f"Expected forbidden snippets absent: {_summarize_list(rule.forbid or [])}. "
                    f"Found forbidden snippets: {_summarize_list([s for s in (rule.forbid or []) if _normalize_text_for_match(s) in forbidden_hits])}"
                )

    # Validate TOC if requested
    if text_validation.include_table_of_contents:
        raw_pages = raw_text.split("\f")
        normalized_pages = [_normalize_text_for_match(page) for page in raw_pages]
        toc_marker = _normalize_text_for_match("Table of Contents")
        toc_page_index = next(
            (i for i, page in enumerate(normalized_pages) if toc_marker in page), -1
        )

        if toc_page_index == -1:
            raise ValueError(
                "Expected a table of contents page but it was not found in the proposal PDF"
            )

        toc_sections = [
            {
                "original": section,
                "normalized": _normalize_text_for_match(section),
            }
            for section in (
                text_validation.toc_sections or text_validation.included_sections
            )
        ]

        toc_page = normalized_pages[toc_page_index]
        missing_from_toc = [
            s["original"] for s in toc_sections if s["normalized"] not in toc_page
        ]

        if missing_from_toc:
            found_in_toc = [s["original"] for s in toc_sections if s["normalized"] in toc_page]
            raise ValueError(
                f"TOC validation failed. "
                f"Expected TOC sections: {_summarize_list([s['original'] for s in toc_sections])}. "
                f"Found TOC sections: {_summarize_list(found_in_toc)}. "
                f"Missing TOC sections: {_summarize_list(missing_from_toc)}"
            )

    logger.debug(f"Proposal text validation passed for {pdf_path}")


def download_and_validate_pdf(
    download_callback: Callable[[], str],
    validation_options: dict,
) -> str:
    """
    Execute download callback and validate the resulting PDF.

    Args:
        download_callback: Function that returns path to downloaded PDF.
        validation_options: Dict with keys:
            - expectedPageCount: int (required)
            - validateContent: bool (optional, default: True)
            - proposalTextValidation: ProposalTextValidationOptions (optional)

    Returns:
        Path to the downloaded and validated PDF file.

    Raises:
        Exception: If download fails or validation fails.
    """
    options = {
        "validateContent": True,
        **validation_options,
    }

    try:
        pdf_path = download_callback()
        logger.debug(f"PDF downloaded successfully to: {pdf_path}")

        if options.get("validateContent"):
            validate_pdf_content(pdf_path, options["expectedPageCount"])

        if options.get("proposalTextValidation"):
            validate_proposal_pdf_text(pdf_path, options["proposalTextValidation"])

        return pdf_path

    except Exception as err:
        logger.error(f"Failed to download or validate PDF: {err}")
        raise


def download_and_validate_pdf_from_click(
    page,
    click_download: Callable[[], None],
    options: dict,
) -> str:
    """
    Click an element that triggers a PDF download, saves it, and validates content.

    Handles multiple concurrent event paths:
    - Captures browser download event on current page
    - Falls back to handling new page/popup with PDF response capture
    - Falls back to direct file polling in downloads folder
    - Validates file stability before considering download complete

    Args:
        page: Playwright Page object (sync API).
        click_download: Callback that triggers the download (e.g., page.click()).
        options: Dict with keys:
            - expectedPageCount: int (required)
            - validateContent: bool (optional, default: True)
            - filenamePrefix: str (optional, default: "download")
            - expectedBrowserFilename: str (required) - filename browser will use
            - proposalTextValidation: ProposalTextValidationOptions (optional)

    Returns:
        Path to the downloaded and validated PDF file.

    Raises:
        TimeoutError: If download times out.
        ValueError: If PDF validation fails.
    """
    settings = {
        "validateContent": True,
        "filenamePrefix": "download",
        **options,
    }

    download_dir = pathlib.Path(__file__).parent.parent / "downloads"
    system_downloads_dir = pathlib.Path.home() / "Downloads"
    download_timeout_ms = 300000  # Changed from 60000 to 300000 (5 minutes)
    stability_delay_ms = 500
    stability_checks_required = 3
    complete_checks_required = 2

    download_dir.mkdir(parents=True, exist_ok=True)

    expected_stem = pathlib.Path(settings["expectedBrowserFilename"]).stem.lower()

    def is_pdf_response(response) -> bool:
        """Check if response has PDF content-type."""
        content_type = response.headers.get("content-type", "").lower()
        return "application/pdf" in content_type


    def is_likely_pdf_buffer(buffer: bytes) -> bool:
        """Quick check if buffer starts with PDF magic bytes (%PDF-)."""
        if len(buffer) < 5:
            return False
        return buffer[:5] == b"%PDF-"

    def save_pdf_buffer(buffer: bytes, source: str) -> str:
        """Save PDF buffer to temp file and return path."""
        temp_path = download_dir / f"temp-{uuid.uuid4()}.pdf"
        temp_path.write_bytes(buffer)
        logger.debug(f"PDF saved from {source}: {temp_path} ({len(buffer)} bytes)")
        return str(temp_path)

    def fetch_and_save_pdf_from_response(response, request_context) -> str:
        """Try to fetch PDF directly from response URL using GET/POST."""
        response_url = response.url

        # Prefer the captured response body when it is actual PDF bytes
        try:
            captured_buffer = response.body()
            if is_likely_pdf_buffer(captured_buffer):
                return save_pdf_buffer(captured_buffer, "captured response")
        except Exception:
            pass

        # Try to re-fetch from the URL with original method
        original_request = response.request
        original_method = original_request.method
        original_data = original_request.post_data
        methods_to_try = [original_method, "POST" if original_method == "GET" else "GET"]
        attempted_statuses = []

        for method in methods_to_try:
            logger.debug(f"Fetching PDF directly from URL using {method}: {response_url}")

            try:
                refetch = request_context.fetch(
                    response_url,
                    method=method,
                    data=original_data if method != "GET" else None,
                    fail_on_status_code=False,
                )

                status_text = f"{refetch.status} {refetch.status_text}"
                attempted_statuses.append(f"{method}={status_text}")

                if refetch.ok:
                    refetch_buffer = refetch.body()
                    if is_likely_pdf_buffer(refetch_buffer):
                        return save_pdf_buffer(refetch_buffer, f"direct fetch ({method})")
            except Exception as e:
                logger.debug(f"Error fetching with {method}: {e}")
                attempted_statuses.append(f"{method}=error")
                continue

        raise TimeoutError(
            f"Failed to fetch valid PDF from {response_url}. Attempts: {', '.join(attempted_statuses)}"
        )

    def find_latest_expected_pdf(min_mtime: float) -> Optional[str]:
        """Find latest PDF in download folders matching expected stem."""
        candidate_dirs = [download_dir, system_downloads_dir]
        candidates = []

        for dir_path in candidate_dirs:
            if not dir_path.exists():
                continue

            for file_path in dir_path.glob("*.pdf"):
                file_stem = file_path.stem.lower()
                if expected_stem not in file_stem:
                    continue

                try:
                    stat = file_path.stat()
                    if stat.st_mtime < min_mtime or stat.st_size <= 1000:
                        continue

                    candidates.append(
                        {"path": file_path, "mtime": stat.st_mtime, "size": stat.st_size}
                    )
                except Exception:
                    continue

        if not candidates:
            return None

        candidates.sort(key=lambda c: (-c["mtime"], -c["size"]))
        return str(candidates[0]["path"])

    def wait_for_complete_expected_pdf(min_mtime: float) -> str:
        """Poll for complete PDF file matching expected filename."""
        deadline = time.time() + (download_timeout_ms / 1000)
        last_path = ""
        last_size = -1
        stable_count = 0
        complete_count = 0

        while time.time() < deadline:
            candidate_path = find_latest_expected_pdf(min_mtime)

            if not candidate_path:
                time.sleep(stability_delay_ms / 1000)
                continue

            temp_path = f"{candidate_path}.crdownload"
            if os.path.exists(temp_path):
                logger.debug(f"Found temp download file, waiting: {temp_path}")
                time.sleep(stability_delay_ms / 1000)
                continue

            try:
                current_size = os.path.getsize(candidate_path)
            except Exception:
                time.sleep(stability_delay_ms / 1000)
                continue

            logger.debug(
                f"Candidate PDF: {candidate_path} ({current_size} bytes, previous: {last_size})"
            )

            if (
                candidate_path == last_path
                and current_size == last_size
                and current_size > 1000
            ):
                stable_count += 1
                if stable_count >= stability_checks_required:
                    if _is_pdf_complete(candidate_path, settings["expectedPageCount"]):
                        complete_count += 1
                    else:
                        complete_count = 0

                    if complete_count >= complete_checks_required:
                        return candidate_path
            else:
                stable_count = 0
                complete_count = 0

            last_path = candidate_path
            last_size = current_size
            time.sleep(stability_delay_ms / 1000)

        raise TimeoutError(
            f"Expected PDF did not appear as a complete file for stem '{expected_stem}' "
            f"in {download_dir} or {system_downloads_dir} after {download_timeout_ms}ms"
        )

    def finalize_download(matched_path: str) -> str:
        """Rename/copy downloaded file to final location."""
        filename = f"{settings['filenamePrefix']}-{uuid.uuid4()}.pdf"
        download_path = download_dir / filename

        try:
            matched_abs_path = pathlib.Path(matched_path).resolve()
            logger.debug(f"Finalize: matched_path={matched_path}, resolved={matched_abs_path}, exists={matched_abs_path.exists()}")
            
            if not matched_abs_path.exists():
                raise FileNotFoundError(f"Matched path does not exist: {matched_abs_path}")
            
            # Use resolve() to normalize both paths before comparison
            matched_parent = matched_abs_path.parent.resolve()
            download_dir_resolved = download_dir.resolve()
            
            if matched_parent == download_dir_resolved:
                os.rename(matched_abs_path, download_path)
            else:
                shutil.copy2(matched_abs_path, download_path)
        except Exception as e:
            logger.error(f"Error finalizing download: {e}")
            logger.error(f"  matched_path: {matched_path}")
            logger.error(f"  download_path: {download_path}")
            logger.error(f"  download_dir exists: {download_dir.exists()}")
            logger.error(f"  Files in download_dir: {list(download_dir.glob('*')) if download_dir.exists() else 'N/A'}")
            raise

        logger.debug(f"Downloaded file renamed to: {download_path}")
        return str(download_path)

    # Record start time for fallback file polling
    click_started_at = time.time()

    # Get browser context
    context = page.context
    
    # Log button state before clicking
    logger.debug(f"Current page URL before click: {page.url}")
    logger.debug(f"Page title before click: {page.title()}")

    pdf_path = None
    fetched_path = None
    download = None
    download_events: list = []
    pdf_response_events: list = []
    new_page_events: list = []
    popup_events: list = []

    def _on_pdf_response(r) -> None:
        """Capture any PDF response from any page."""
        try:
            if "application/pdf" in r.headers.get("content-type", "").lower():
                pdf_response_events.append(r)
                logger.debug(f"PDF response captured: {r.url}")
        except Exception:
            pass

    def _on_new_page_download(dl) -> None:
        download_events.append(dl)
        logger.debug("Download captured on new page")

    def _setup_new_page_listeners(pg) -> None:
        """Register download listener on a new page/popup.
        Response capture is handled at the context level so it covers the popup
        regardless of when on_popup fires relative to the PDF response.
        """
        pg.on("download", _on_new_page_download)

    def on_popup(pg) -> None:
        popup_events.append(pg)
        _setup_new_page_listeners(pg)
        logger.debug(f"Popup detected: {pg.url}")
        # Wait for popup to actually load content (may start as about:blank)
        try:
            pg.wait_for_load_state("load", timeout=10000)
            logger.debug(f"Popup loaded: {pg.url}")
        except Exception as e:
            logger.debug(f"Popup load wait failed: {e}")

    def on_page(pg) -> None:
        new_page_events.append(pg)
        _setup_new_page_listeners(pg)
        logger.debug(f"New page detected: {pg.url}")

    def on_download(dl) -> None:
        download_events.append(dl)
        logger.debug("Download captured on current page")

    # Register ALL event handlers BEFORE clicking.
    # context.on("response") fires for every response in the context (all pages),
    # so it catches the popup's PDF response even before on_popup can attach a
    # page-level listener — no timing race.
    page.on("download", on_download)
    page.on("popup", on_popup)
    context.on("response", _on_pdf_response)  # catches responses from ALL pages (including popup)
    context.on("page", on_page)

    # Configure CDP on the current page BEFORE clicking (required for headless mode —
    # in headless, no popup is opened; CDP forces the PDF to download directly).
    logger.debug("Setting up CDP session for download behavior...")
    try:
        client = context.new_cdp_session(page)
        client.send("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(download_dir),
        })
        logger.debug(f"Download behavior configured for: {download_dir}")
    except Exception as e:
        logger.warning(f"CDP setup failed (downloads may open in viewer): {e}")

    logger.debug("Event handlers registered, triggering PDF download action...")
    
    # Capture page URL before click to detect navigation
    url_before = page.url
    logger.debug(f"Page URL before click: {url_before}")
    
    click_download()
    logger.debug("Download button clicked, waiting for events to fire...")
    
    # Wait a moment for navigation
    time.sleep(2)
    
    # Log page state immediately after click
    url_after = page.url
    logger.debug(f"Page URL after click: {url_after}")
    logger.debug(f"Page title after click: {page.title()}")
    
    # HEADLESS MODE DETECTION: Check if button navigated to PDF directly
    if url_before != url_after:
        logger.debug(f"URL CHANGED: {url_before} -> {url_after}")
        if ".pdf" in url_after.lower():
            logger.debug("HEADLESS MODE: Detected direct PDF navigation (not a download event)")
            logger.debug(f"Fetching PDF directly from navigated URL: {url_after}")
            try:
                # In headless, the browser navigates to the PDF URL instead of downloading
                # Fetch it directly
                pdf_response = page.request.fetch(url_after, fail_on_status_code=False)
                if pdf_response.ok:
                    pdf_buffer = pdf_response.body()
                    if is_likely_pdf_buffer(pdf_buffer):
                        fetched_path = save_pdf_buffer(pdf_buffer, "headless direct fetch")
                        pdf_path = finalize_download(fetched_path)
                        logger.info(f"Successfully downloaded PDF in headless mode from navigation: {pdf_path}")
                        return pdf_path
            except Exception as e:
                logger.debug(f"Failed to fetch PDF from navigated URL: {e}")
    
    # Wait remaining time for events (increased from 5s to 10s to allow popup to fully load)
    time.sleep(8)

    logger.debug(f"=== POST-CLICK EVENT SUMMARY ===")
    logger.debug(f"  Download events captured: {len(download_events)}")
    logger.debug(f"  PDF response events captured: {len(pdf_response_events)}")
    logger.debug(f"  Popup events: {len(popup_events)} -> URLs: {[p.url for p in popup_events]}")
    logger.debug(f"  New page events: {len(new_page_events)} -> URLs: {[p.url for p in new_page_events]}")

    # PATH 1: Download event on current page
    if download_events:
        download = download_events[0]
        logger.debug("PATH 1: Download captured on current page")

    # PATH 2: Popup or new page
    if not download and (popup_events or new_page_events):
        target_page = popup_events[0] if popup_events else new_page_events[0]
        logger.debug(f"PATH 2: New window captured: {target_page.url}")

        # Configure CDP on new window (belt-and-suspenders alongside event-based capture)
        logger.debug("Setting up CDP on new window...")
        try:
            new_client = context.new_cdp_session(target_page)
            new_client.send("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": str(download_dir),
            })
            logger.debug("CDP configured on new window")
        except Exception as e:
            logger.debug(f"CDP on new window failed: {e}")

        # PATH 2a: If no PDF response was captured via event handler yet, wait for one (10s)
        if not pdf_response_events:
            logger.debug("PATH 2a: Waiting for PDF response on new window...")
            try:
                r = target_page.wait_for_response(
                    lambda r: is_pdf_response(r), timeout=10000
                )
                pdf_response_events.append(r)
                logger.debug(f"PDF response detected: {r.url}")
            except Exception as e:
                logger.debug(f"No PDF response on new window: {e}")

        # PATH 2b: If still nothing, wait for download event on new window (60s)
        if not pdf_response_events and not download_events:
            logger.debug("PATH 2b: Waiting for download on new window...")
            try:
                dl = target_page.wait_for_event("download", timeout=60000)
                download_events.append(dl)
                logger.debug("Download event on new window")
            except Exception as e:
                logger.debug(f"No download on new window: {e}")

        download = download_events[0] if download_events else None

    # Finalization
    if not download:
        logger.debug(f"=== FINALIZATION: No download event captured ===")
        if not pdf_response_events:
            # Last resort: wait for PDF response on current page (5s)
            logger.debug("Attempting PDF response on current page (fallback)...")
            try:
                r = page.wait_for_response(lambda r: is_pdf_response(r), timeout=5000)
                pdf_response_events.append(r)
                logger.debug(f"PDF response on current page: {r.url}")
            except Exception as e:
                logger.debug(f"No PDF response on current page: {e}")

        if pdf_response_events:
            logger.debug(f"=== USING PDF RESPONSE PATH: {pdf_response_events[0].url} ===")
            req_ctx = (
                popup_events[0].request if popup_events
                else new_page_events[0].request if new_page_events
                else page.request
            )
            try:
                fetched_path = fetch_and_save_pdf_from_response(pdf_response_events[0], req_ctx)
                pdf_path = finalize_download(fetched_path)
                logger.debug(f"PDF finalized from response: {pdf_path}")
            except Exception as e:
                logger.debug(f"Failed to save PDF from response, falling back: {e}")

        if not pdf_path:
            logger.debug("=== FALLING BACK TO FILENAME POLLING ===")
            try:
                matched_path = wait_for_complete_expected_pdf(click_started_at - 2)
                pdf_path = finalize_download(matched_path)
                logger.debug(f"PDF found via filename polling: {pdf_path}")
            except TimeoutError as e:
                raise TimeoutError(
                    f"Failed to capture PDF via all methods: {e}"
                )
    else:
        # Download event captured (PATH 1 or 2b)
        logger.debug(f"=== USING DOWNLOAD EVENT PATH ===")
        # Wait for download to complete, then save to our downloads folder
        failure = download.failure()
        if failure:
            raise RuntimeError(f"Download failed: {failure}")
        
        logger.debug(f"Download event captured: {download.suggested_filename}")
        
        # download.path() blocks until file is written
        try:
            temp_path = download.path()
            logger.debug(f"Download temp path: {temp_path}")
            
            # Resolve short filename (8.3 format) to full path
            temp_path_obj = pathlib.Path(temp_path).resolve()
            logger.debug(f"Resolved path: {temp_path_obj}")
            
            # Verify the file exists and is not empty
            if temp_path_obj.exists():
                file_size = temp_path_obj.stat().st_size
                logger.debug(f"Temp file size: {file_size} bytes")
                
                if file_size > 0:
                    # Copy to our downloads folder
                    filename = f"{settings['filenamePrefix']}-{uuid.uuid4()}.pdf"
                    download_path = download_dir / filename
                    
                    shutil.copy2(str(temp_path_obj), str(download_path))
                    final_size = download_path.stat().st_size
                    logger.debug(f"Downloaded file copied to: {download_path} ({final_size} bytes)")
                    pdf_path = str(download_path)
                else:
                    logger.warning(f"Temp file is empty (0 bytes), falling back to polling")
                    matched_path = wait_for_complete_expected_pdf(click_started_at - 2)
                    pdf_path = finalize_download(matched_path)
            else:
                logger.warning(f"Temp file not found at resolved path: {temp_path_obj}, falling back to polling")
                matched_path = wait_for_complete_expected_pdf(click_started_at - 2)
                pdf_path = finalize_download(matched_path)
        except Exception as e:
            logger.debug(f"Could not get download path: {e}, falling back to polling")
            matched_path = wait_for_complete_expected_pdf(click_started_at - 2)
            pdf_path = finalize_download(matched_path)

    # Remove context-level listeners so they don't accumulate if this function
    # is called more than once within the same browser context.
    try:
        context.remove_listener("response", _on_pdf_response)
        context.remove_listener("page", on_page)
        page.remove_listener("download", on_download)
        page.remove_listener("popup", on_popup)
    except Exception:
        pass

    # Validate the downloaded PDF
    return download_and_validate_pdf(
        lambda: pdf_path,
        {
            "expectedPageCount": settings["expectedPageCount"],
            "validateContent": settings.get("validateContent"),
            "proposalTextValidation": settings.get("proposalTextValidation"),
        },
    )
