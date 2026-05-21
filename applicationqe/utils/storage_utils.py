"""
Browser Storage Management Utilities

Provides utilities for managing localStorage, sessionStorage, and cookies.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from playwright.sync_api import BrowserContext, Page

logger = logging.getLogger(__name__)


class LocalStorageManager:
    """
    Manage browser localStorage.

    Example:
        storage = LocalStorageManager(page)
        storage.set_item("user", "john_doe")
        storage.get_item("user")
        storage.clear()
    """

    def __init__(self, page: Page):
        self.page = page

    def set_item(self, key: str, value: Union[str, dict, list]) -> None:
        """
        Set localStorage item.

        Args:
            key: Storage key
            value: Value (will be JSON serialized if dict/list)
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        self.page.evaluate(f"window.localStorage.setItem('{key}', '{value}')")
        logger.debug(f"localStorage.setItem('{key}', ...)")

    def get_item(self, key: str) -> Optional[str]:
        """
        Get localStorage item.

        Args:
            key: Storage key

        Returns:
            Value or None if not found
        """
        value = self.page.evaluate(f"window.localStorage.getItem('{key}')")
        logger.debug(f"localStorage.getItem('{key}') = {value}")
        return value

    def get_item_as_json(self, key: str) -> Optional[Union[dict, list]]:
        """
        Get localStorage item and parse as JSON.

        Args:
            key: Storage key

        Returns:
            Parsed JSON or None
        """
        value = self.get_item(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse localStorage['{key}'] as JSON")
                return value
        return None

    def remove_item(self, key: str) -> None:
        """Remove localStorage item"""
        self.page.evaluate(f"window.localStorage.removeItem('{key}')")
        logger.debug(f"localStorage.removeItem('{key}')")

    def clear(self) -> None:
        """Clear all localStorage"""
        self.page.evaluate("window.localStorage.clear()")
        logger.info("localStorage cleared")

    def get_all_items(self) -> Dict[str, str]:
        """
        Get all localStorage items.

        Returns:
            Dictionary of all key-value pairs
        """
        items = self.page.evaluate(
            """
            () => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }
        """
        )
        return items

    def get_length(self) -> int:
        """Get number of localStorage items"""
        return self.page.evaluate("window.localStorage.length")

    def has_item(self, key: str) -> bool:
        """Check if localStorage has key"""
        return self.get_item(key) is not None

    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save localStorage to JSON file"""
        items = self.get_all_items()
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(items, f, indent=2)

        logger.info(f"localStorage saved to: {filepath}")

    def load_from_file(self, filepath: Union[str, Path]) -> None:
        """Load localStorage from JSON file"""
        filepath = Path(filepath)

        with open(filepath, "r") as f:
            items = json.load(f)

        for key, value in items.items():
            self.set_item(key, value)

        logger.info(f"localStorage loaded from: {filepath}")


class SessionStorageManager:
    """
    Manage browser sessionStorage.

    Similar to LocalStorageManager but for sessionStorage.
    """

    def __init__(self, page: Page):
        self.page = page

    def set_item(self, key: str, value: Union[str, dict, list]) -> None:
        """Set sessionStorage item"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        self.page.evaluate(f"window.sessionStorage.setItem('{key}', '{value}')")
        logger.debug(f"sessionStorage.setItem('{key}', ...)")

    def get_item(self, key: str) -> Optional[str]:
        """Get sessionStorage item"""
        value = self.page.evaluate(f"window.sessionStorage.getItem('{key}')")
        logger.debug(f"sessionStorage.getItem('{key}') = {value}")
        return value

    def get_item_as_json(self, key: str) -> Optional[Union[dict, list]]:
        """Get sessionStorage item and parse as JSON"""
        value = self.get_item(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse sessionStorage['{key}'] as JSON")
                return value
        return None

    def remove_item(self, key: str) -> None:
        """Remove sessionStorage item"""
        self.page.evaluate(f"window.sessionStorage.removeItem('{key}')")
        logger.debug(f"sessionStorage.removeItem('{key}')")

    def clear(self) -> None:
        """Clear all sessionStorage"""
        self.page.evaluate("window.sessionStorage.clear()")
        logger.info("sessionStorage cleared")

    def get_all_items(self) -> Dict[str, str]:
        """Get all sessionStorage items"""
        items = self.page.evaluate(
            """
            () => {
                const items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            }
        """
        )
        return items


class CookieManager:
    """
    Manage browser cookies.

    Example:
        cookies = CookieManager(context)
        cookies.set_cookie("session_id", "abc123")
        cookies.get_cookie("session_id")
        cookies.delete_cookie("session_id")
    """

    def __init__(self, context: BrowserContext):
        self.context = context

    def get_all_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        cookies = self.context.cookies()
        logger.debug(f"Retrieved {len(cookies)} cookies")
        return cookies

    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get cookie by name.

        Args:
            name: Cookie name

        Returns:
            Cookie dict or None
        """
        cookies = self.get_all_cookies()
        for cookie in cookies:
            if cookie["name"] == name:
                return cookie
        return None

    def get_cookie_value(self, name: str) -> Optional[str]:
        """Get cookie value by name"""
        cookie = self.get_cookie(name)
        return cookie["value"] if cookie else None

    def set_cookie(
        self,
        name: str,
        value: str,
        domain: Optional[str] = None,
        path: str = "/",
        expires: Optional[Union[int, datetime]] = None,
        http_only: bool = False,
        secure: bool = False,
        same_site: str = "Lax",
    ) -> None:
        """
        Set a cookie.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Cookie domain
            path: Cookie path
            expires: Expiration (timestamp or datetime)
            http_only: HttpOnly flag
            secure: Secure flag
            same_site: SameSite attribute
        """
        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "httpOnly": http_only,
            "secure": secure,
            "sameSite": same_site,
        }

        if domain:
            cookie["domain"] = domain

        if expires:
            if isinstance(expires, datetime):
                expires = int(expires.timestamp())
            cookie["expires"] = expires

        self.context.add_cookies([cookie])
        logger.debug(f"Cookie set: {name}={value}")

    def delete_cookie(self, name: str) -> None:
        """Delete cookie by name"""
        cookies = [c for c in self.get_all_cookies() if c["name"] != name]
        self.context.clear_cookies()
        if cookies:
            self.context.add_cookies(cookies)
        logger.debug(f"Cookie deleted: {name}")

    def clear_all_cookies(self) -> None:
        """Clear all cookies"""
        self.context.clear_cookies()
        logger.info("All cookies cleared")

    def has_cookie(self, name: str) -> bool:
        """Check if cookie exists"""
        return self.get_cookie(name) is not None

    def save_cookies_to_file(self, filepath: Union[str, Path]) -> None:
        """Save cookies to JSON file"""
        cookies = self.get_all_cookies()
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"Cookies saved to: {filepath}")

    def load_cookies_from_file(self, filepath: Union[str, Path]) -> None:
        """Load cookies from JSON file"""
        filepath = Path(filepath)

        with open(filepath, "r") as f:
            cookies = json.load(f)

        self.context.add_cookies(cookies)
        logger.info(f"Cookies loaded from: {filepath}")

    def get_cookies_as_dict(self) -> Dict[str, str]:
        """Get cookies as simple name:value dictionary"""
        cookies = self.get_all_cookies()
        return {c["name"]: c["value"] for c in cookies}

    def set_session_cookie(self, name: str, value: str, domain: Optional[str] = None):
        """Set a session cookie (no expiration)"""
        self.set_cookie(name, value, domain=domain, expires=None)

    def set_persistent_cookie(
        self, name: str, value: str, days: int = 30, domain: Optional[str] = None
    ):
        """Set a persistent cookie with expiration"""
        expires = datetime.now() + timedelta(days=days)
        self.set_cookie(name, value, domain=domain, expires=expires)


class StorageState:
    """
    Manage complete storage state (localStorage, sessionStorage, cookies).

    Example:
        storage_state = StorageState(page, context)
        storage_state.save_state("user_session.json")
        storage_state.load_state("user_session.json")
    """

    def __init__(self, page: Page, context: BrowserContext):
        self.page = page
        self.context = context
        self.local_storage = LocalStorageManager(page)
        self.session_storage = SessionStorageManager(page)
        self.cookies = CookieManager(context)

    def save_state(self, filepath: Union[str, Path]) -> None:
        """
        Save complete storage state to file.

        Args:
            filepath: Path to save state
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "localStorage": self.local_storage.get_all_items(),
            "sessionStorage": self.session_storage.get_all_items(),
            "cookies": self.cookies.get_all_cookies(),
            "url": self.page.url,
            "timestamp": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Storage state saved to: {filepath}")

    def load_state(self, filepath: Union[str, Path]) -> None:
        """
        Load complete storage state from file.

        Args:
            filepath: Path to load state from
        """
        filepath = Path(filepath)

        with open(filepath, "r") as f:
            state = json.load(f)

        # Load cookies first
        if "cookies" in state:
            self.context.add_cookies(state["cookies"])

        # Navigate to saved URL if present
        if "url" in state:
            self.page.goto(state["url"])

        # Load localStorage
        if "localStorage" in state:
            for key, value in state["localStorage"].items():
                self.local_storage.set_item(key, value)

        # Load sessionStorage
        if "sessionStorage" in state:
            for key, value in state["sessionStorage"].items():
                self.session_storage.set_item(key, value)

        logger.info(f"Storage state loaded from: {filepath}")

    def clear_all(self) -> None:
        """Clear all storage (localStorage, sessionStorage, cookies)"""
        self.local_storage.clear()
        self.session_storage.clear()
        self.cookies.clear_all_cookies()
        logger.info("All storage cleared")
