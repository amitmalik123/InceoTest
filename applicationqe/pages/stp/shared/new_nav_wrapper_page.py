"""
NewNavWrapperPage - Handles new navigation UI and iframe context

This page is responsible ONLY for:
1. Handling the outer new navigation UI elements
2. Providing iframe context to reuse existing page classes

Used exclusively for the manage_bene scenario where UI A is inside an iframe.
"""

from playwright.sync_api import Page, FrameLocator
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class NewNavWrapperPage:
    """
    Wrapper page for new navigation UI with iframe.
    
    Responsibilities:
    - Navigate new nav bar menu items
    - Wait for iframe to be ready
    - Provide iframe context for reusing existing page classes
    """
    
    def __init__(self, page: Page):
        self.page = page
        self._iframe_context = None
        
    def get_iframe_context(self) -> FrameLocator:
        """
        Get the iframe context for reusing existing page classes.
        
        Returns:
            FrameLocator: Context that can be passed to page class constructors
        """
        if self._iframe_context is None:
            logger.info("Waiting for iframe #iframeWrapper to be available")
            self.page.wait_for_selector("#iframeWrapper", state="attached", timeout=10000)
            self._iframe_context = self.page.frame_locator("#iframeWrapper")
            logger.info("Iframe context initialized successfully")
        return self._iframe_context
