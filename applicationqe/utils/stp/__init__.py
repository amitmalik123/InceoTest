"""
STP-specific utility modules.

Clean copies of core utils from the ES2PlaywrightPython branch, with STP-specific
fixes applied (azure_sql config key, ActiveDirectoryIntegrated auth support, etc.).

These modules can be imported directly:
    from utils.stp.database import get_azure_db_connection
    from utils.wait_utils import wait_for_element_stable
"""
