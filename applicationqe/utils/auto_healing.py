"""
Auto-Healing Engine for Playwright Test Automation

This module provides self-healing capabilities for locators when elements cannot be found.
It uses multiple strategies to locate elements and learns from successful attempts.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class HealingStrategy:
    """Base class for healing strategies"""

    def __init__(self, name: str):
        self.name = name

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """
        Attempt to find element using this strategy.

        Args:
            page: Playwright page object
            original_selector: Original selector that failed

        Returns:
            Locator if found, None otherwise
        """
        raise NotImplementedError


class TextContentStrategy(HealingStrategy):
    """Find element by text content"""

    def __init__(self):
        super().__init__("text_content")

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """Find by visible text"""
        try:
            # Extract text from original selector if it's a text-based selector
            if "text=" in original_selector or ">>" in original_selector:
                text = original_selector.split("text=")[-1].strip("'\"")
                locator = page.get_by_text(text, exact=False)
                if locator.count() > 0:
                    logger.info(f"Found element using text: {text}")
                    return locator.first
        except Exception as e:
            logger.debug(f"TextContentStrategy failed: {e}")
        return None


class RoleStrategy(HealingStrategy):
    """Find element by ARIA role"""

    def __init__(self):
        super().__init__("role")

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """Find by role attributes"""
        try:
            # Try common roles
            roles = ["button", "link", "textbox", "checkbox", "radio", "heading"]
            for role in roles:
                locators = page.get_by_role(role)  # type: ignore[arg-type]
                if locators.count() > 0:
                    # Try to match by comparing with original selector
                    for i in range(min(5, locators.count())):  # Check first 5
                        locator = locators.nth(i)
                        if self._matches_context(locator, original_selector):
                            logger.info(f"Found element using role: {role}")
                            return locator
        except Exception as e:
            logger.debug(f"RoleStrategy failed: {e}")
        return None

    def _matches_context(self, locator: Locator, original_selector: str) -> bool:
        """Check if locator matches context from original selector"""
        try:
            # Simple heuristic: check if any part of original selector matches
            element_text = locator.text_content() or ""
            return any(
                part.strip("'\"") in element_text
                for part in original_selector.split()
                if len(part) > 2
            )
        except Exception:
            return False


class PlaceholderStrategy(HealingStrategy):
    """Find element by placeholder text"""

    def __init__(self):
        super().__init__("placeholder")

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """Find by placeholder attribute"""
        try:
            # Extract potential placeholder text
            if "placeholder" in original_selector.lower():
                placeholder = original_selector.split("placeholder")[-1].strip("='\"[]")
                locator = page.get_by_placeholder(placeholder)
                if locator.count() > 0:
                    logger.info(f"Found element using placeholder: {placeholder}")
                    return locator.first
        except Exception as e:
            logger.debug(f"PlaceholderStrategy failed: {e}")
        return None


class LabelStrategy(HealingStrategy):
    """Find element by associated label"""

    def __init__(self):
        super().__init__("label")

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """Find by label text"""
        try:
            # Try to find by label
            locator = page.get_by_label(original_selector, exact=False)
            if locator.count() > 0:
                logger.info("Found element using label")
                return locator.first
        except Exception as e:
            logger.debug(f"LabelStrategy failed: {e}")
        return None


class TestIdStrategy(HealingStrategy):
    """Find element by test ID attribute"""

    def __init__(self):
        super().__init__("test_id")

    def find_element(self, page: Page, original_selector: str) -> Optional[Locator]:
        """Find by data-testid or similar attributes"""
        try:
            # Extract test ID from selector
            if "data-testid" in original_selector or "test-id" in original_selector:
                test_id = original_selector.split("=")[-1].strip("'\"[]")
                locator = page.get_by_test_id(test_id)
                if locator.count() > 0:
                    logger.info(f"Found element using test-id: {test_id}")
                    return locator.first
        except Exception as e:
            logger.debug(f"TestIdStrategy failed: {e}")
        return None


class XPathToCSS:
    """Convert XPath selectors to CSS"""

    @staticmethod
    def convert(xpath: str) -> Optional[str]:
        """
        Convert simple XPath to CSS selector.

        Args:
            xpath: XPath selector

        Returns:
            CSS selector or None if conversion not possible
        """
        try:
            # Simple conversions
            css = xpath.replace("//", "").replace("/", " > ")

            # Handle attributes
            if "[@" in css:
                css = css.replace("[@", "[").replace("]", "]")

            # Handle text()
            if "text()" in css:
                return None  # Text queries need different handling

            return css
        except Exception:
            return None


class AutoHealingEngine:
    """
    Main auto-healing engine that manages healing strategies and locator storage.
    """

    def __init__(self, storage_path: str = "locator_storage.json"):
        """
        Initialize auto-healing engine.

        Args:
            storage_path: Path to store learned locators
        """
        self.storage_path = Path(storage_path)
        self.strategies = [
            TestIdStrategy(),
            LabelStrategy(),
            PlaceholderStrategy(),
            RoleStrategy(),
            TextContentStrategy(),
        ]
        self.locator_storage = self._load_storage()
        self.healing_stats = {"total_heals": 0, "successful_heals": 0, "failed_heals": 0}

    def _load_storage(self) -> Dict:
        """Load locator storage from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load locator storage: {e}")
        return {}

    def _save_storage(self):
        """Save locator storage to file"""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.locator_storage, indent=2, fp=f)
        except Exception as e:
            logger.error(f"Failed to save locator storage: {e}")

    def _get_locator_key(self, selector: str, page_url: str = "") -> str:
        """Generate unique key for locator"""
        key_str = f"{page_url}::{selector}"
        return hashlib.md5(key_str.encode(), usedforsecurity=False).hexdigest()

    def find_element(  # noqa: C901
        self, page: Page, selector: str, max_retries: int = 3
    ) -> Tuple[Optional[Locator], bool]:
        """
        Find element with auto-healing capabilities.

        Args:
            page: Playwright page object
            selector: Original selector
            max_retries: Maximum healing attempts

        Returns:
            Tuple of (Locator, was_healed)
        """
        # Try original selector first
        try:
            locator = page.locator(selector)
            if locator.count() > 0:
                return locator.first, False
        except Exception as e:
            logger.debug(f"Original selector failed: {e}")

        # Check if we have a stored alternative
        page_url = page.url
        locator_key = self._get_locator_key(selector, page_url)

        if locator_key in self.locator_storage:
            stored_selector = self.locator_storage[locator_key]["selector"]
            try:
                locator = page.locator(stored_selector)
                if locator.count() > 0:
                    logger.info(f"Using stored alternative selector: {stored_selector}")
                    return locator.first, True
            except Exception:
                logger.debug("Stored selector also failed")

        # Try healing strategies
        logger.warning(f"Attempting to heal selector: {selector}")
        self.healing_stats["total_heals"] += 1

        for strategy in self.strategies:
            try:
                healed_locator = strategy.find_element(page, selector)
                if healed_locator and healed_locator.count() > 0:
                    # Store successful alternative
                    new_selector = self._extract_selector(healed_locator)
                    if new_selector:
                        self._store_alternative(locator_key, selector, new_selector, strategy.name)
                        self.healing_stats["successful_heals"] += 1
                        logger.info(f"Successfully healed using {strategy.name}: {new_selector}")
                        return healed_locator, True
            except Exception as e:
                logger.debug(f"Strategy {strategy.name} failed: {e}")
                continue

        self.healing_stats["failed_heals"] += 1
        logger.error(f"All healing strategies failed for selector: {selector}")
        return None, False

    def _extract_selector(self, locator: Locator) -> Optional[str]:
        """Extract selector from locator (simplified)"""
        try:
            # This is a simplified version - in practice, you'd want more robust extraction
            return str(locator)
        except Exception:
            return None

    def _store_alternative(self, key: str, original: str, alternative: str, strategy: str):
        """Store alternative selector"""
        self.locator_storage[key] = {
            "original": original,
            "selector": alternative,
            "strategy": strategy,
            "timestamp": time.time(),
            "success_count": self.locator_storage.get(key, {}).get("success_count", 0) + 1,
        }
        self._save_storage()

    def get_stats(self) -> Dict:
        """Get healing statistics"""
        return {
            **self.healing_stats,
            "success_rate": (
                self.healing_stats["successful_heals"] / self.healing_stats["total_heals"]
                if self.healing_stats["total_heals"] > 0
                else 0
            ),
            "stored_alternatives": len(self.locator_storage),
        }

    def reset_stats(self):
        """Reset healing statistics"""
        self.healing_stats = {"total_heals": 0, "successful_heals": 0, "failed_heals": 0}

    def clear_storage(self):
        """Clear all stored locators"""
        self.locator_storage = {}
        self._save_storage()
        logger.info("Locator storage cleared")
