"""
Data variations for proposal testing.
Converted from TypeScript: proposalVariations.ts

Provides helper functions for selecting custodians and registration types
across different proposal scenarios.
"""

import logging
from random import choice

logger = logging.getLogger(__name__)


def select_custodian(page_object):
    """
    Select a custodian from the dropdown, works for Portfolio Engine and New Account Wizard

    Args:
        page_object: The current page object with custodian locators

    Returns:
        None - performs the selection as a side effect
    """
    logger.debug("Clicking custodian dropdown")
    
    # Wait for dropdown to be fully interactive
    page_object.select_custodian_dropdown.wait_for(state="visible", timeout=10000)
    page_object.page.wait_for_timeout(300)  # Extra pause for dropdown animation
    
    # Define valid custodians (excludes "Select" placeholder)
    custodians = [
        page_object.fidelity_text,
        page_object.assetmark_text,
        page_object.schwab_text,
        page_object.pershing_advisor_solutions_text,
    ]

    # Wait for custodian options to be visible in the dropdown list
    page_object.page.wait_for_timeout(500)  # Allow dropdown to open and populate
    
    # Filter to only visible custodians (in case some flows don't have all options)
    visible_custodians = []
    for custodian in custodians:
        try:
            if custodian.is_visible():
                visible_custodians.append(custodian)
                logger.debug(f"Found visible custodian: {custodian}")
        except Exception as e:
            logger.debug(f"Custodian check failed: {str(e)}")

    # Select random visible custodian or default to AssetMark
    if visible_custodians:
        selected_custodian = choice(visible_custodians)
        logger.debug(f"Selecting random custodian from {len(visible_custodians)} options")
        selected_custodian.click()
        page_object.page.wait_for_timeout(500)  # Wait after selection
    else:
        logger.debug("No visible custodians - attempting AssetMark default")
        try:
            page_object.assetmark_text.click()
            page_object.page.wait_for_timeout(500)
        except Exception as e:
            logger.warning(f"Failed to select default AssetMark custodian: {str(e)}")
