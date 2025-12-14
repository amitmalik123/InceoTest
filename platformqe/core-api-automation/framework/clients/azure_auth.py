"""
Azure Authentication Utilities
Provides functions for Azure AD authentication including access token generation.

Best Practices:
- Uses Azure CLI for local development authentication
- Supports DefaultAzureCredential pattern for production (Managed Identity)
- Token caching to reduce Azure CLI calls
- Configuration-driven resource URLs
"""
import subprocess
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class AzureAuthManager:
    """
    Manages Azure AD authentication and token generation.
    
    Follows Azure best practices:
    - Configuration-driven resource URLs
    - Token caching for performance
    - Proper error handling and logging
    - Support for multiple Azure services
    """
    
    # Default Azure AD resources (fallback if config not provided)
    DEFAULT_RESOURCES = {
        'postgresql': 'https://ossrdbms-aad.database.windows.net',
        'mysql': 'https://ossrdbms-aad.database.windows.net',
        'mssql': 'https://database.windows.net/',
        'resource_manager': 'https://management.azure.com/',
        'key_vault': 'https://vault.azure.net',
        'storage': 'https://storage.azure.com/',
        'default_database': 'https://ossrdbms-aad.database.windows.net'
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Azure Auth Manager.
        
        Args:
            config: Configuration dictionary containing azure_ad.resources section
        
        Best Practice: Accept config to avoid hardcoded values
        """
        self.config = config or {}
        self._token_cache = {}
        
        # Load Azure AD resources from config or use defaults
        azure_ad_config = self.config.get('azure_ad', {})
        self.resources = azure_ad_config.get('resources', self.DEFAULT_RESOURCES.copy())
        
        logger.info("Azure Auth Manager initialized with config-driven resources")
    
    def get_resource_url(self, resource_type: str) -> str:
        """
        Get Azure AD resource URL by type from configuration.
        
        Args:
            resource_type: Type of resource (postgresql, mssql, resource_manager, etc.)
        
        Returns:
            Resource URL string
        
        Best Practice: Centralize resource URL management
        """
        resource_url = self.resources.get(resource_type)
        
        if not resource_url:
            logger.warning(
                f"Resource type '{resource_type}' not found in config, "
                f"using default: {self.DEFAULT_RESOURCES.get(resource_type)}"
            )
            resource_url = self.DEFAULT_RESOURCES.get(
                resource_type,
                self.DEFAULT_RESOURCES['default_database']
            )
        
        return resource_url
    
    def get_azure_access_token(
        self,
        resource: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> str:
        """
        Generate Azure access token using Azure CLI.
        
        Best Practices Applied:
        - Configuration-driven resource URLs
        - Token caching to reduce API calls
        - Proper error handling with context
        - Support for both resource type and direct URL
        
        Args:
            resource: Direct Azure resource URL (e.g., "https://ossrdbms-aad.database.windows.net")
            resource_type: Resource type key from config (e.g., "postgresql", "mssql")
                          Takes precedence over resource parameter
        
        Returns:
            str: The access token
        
        Raises:
            RuntimeError: If token generation fails
            FileNotFoundError: If Azure CLI is not installed
        
        Example:
            >>> auth_mgr = AzureAuthManager(config)
            >>> # Using resource type (recommended - uses config)
            >>> token = auth_mgr.get_azure_access_token(resource_type='postgresql')
            >>> # Using direct resource URL (backward compatible)
            >>> token = auth_mgr.get_azure_access_token(
            ...     resource='https://ossrdbms-aad.database.windows.net'
            ... )
        
        Note:
            For production deployments, consider using Azure SDK's DefaultAzureCredential
            which supports Managed Identity, Service Principal, and Azure CLI in order.
        """
        # Determine the resource URL from config or parameter
        if resource_type:
            resource_url = self.get_resource_url(resource_type)
            logger.info(f"Getting token for resource type '{resource_type}': {resource_url}")
        elif resource:
            resource_url = resource
            logger.info(f"Getting token for direct resource URL: {resource_url}")
        else:
            # Use default from config
            resource_url = self.get_resource_url('default_database')
            logger.info(f"No resource specified, using default: {resource_url}")
        
        # Check cache to reduce Azure CLI calls (Best Practice)
        if resource_url in self._token_cache:
            logger.debug(f"Returning cached token for: {resource_url}")
            return self._token_cache[resource_url]
        
        try:
            # Use Azure CLI for token generation
            # Best Practice: Separate command construction for better testability
            command = f'az account get-access-token --resource {resource_url}'
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                timeout=30  # Best Practice: Add timeout to prevent hanging
            )
            
            token_data = json.loads(result.stdout)
            access_token = token_data.get('accessToken')
            
            if not access_token:
                raise ValueError("Access token not found in Azure CLI response")
            
            # Strip any whitespace from token (important for Azure PostgreSQL)
            access_token = access_token.strip()
            
            # Cache the token (Best Practice: Reduce API calls)
            self._token_cache[resource_url] = access_token
            logger.info(f"Successfully obtained and cached Azure AD token for: {resource_url}")
            
            return access_token
            
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"Azure CLI error: {e.stderr}\n"
                f"Troubleshooting:\n"
                f"1. Run 'az login' to authenticate\n"
                f"2. Verify you have access to the resource: {resource_url}\n"
                f"3. Check your Azure subscription is active"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Azure CLI response: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        except FileNotFoundError as e:
            error_msg = (
                "Azure CLI not found. Please install:\n"
                "Windows: https://aka.ms/installazurecliwindows\n"
                "Or run: winget install -e --id Microsoft.AzureCLI"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg) from e
        
        except subprocess.TimeoutExpired as e:
            error_msg = f"Azure CLI command timed out after 30 seconds: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def clear_token_cache(self, resource: Optional[str] = None):
        """
        Clear cached tokens.
        
        Args:
            resource: Specific resource to clear, or None to clear all
        
        Best Practice: Provide cache management for token refresh scenarios
        """
        if resource:
            self._token_cache.pop(resource, None)
            logger.info(f"Cleared token cache for: {resource}")
        else:
            self._token_cache.clear()
            logger.info("Cleared all cached tokens")
    
    def check_azure_login(self) -> bool:
        """
        Check if user is logged in to Azure CLI.
        
        Returns:
            bool: True if logged in, False otherwise
        
        Best Practice: Verify authentication before attempting operations
        """
        try:
            result = subprocess.run(
                'az account show',
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                timeout=10
            )
            is_logged_in = result.returncode == 0
            
            if is_logged_in:
                logger.info("Azure CLI login verified")
            else:
                logger.warning("Not logged in to Azure CLI. Run 'az login'")
            
            return is_logged_in
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Azure CLI not available or not logged in")
            return False
    
    def get_current_subscription(self) -> Optional[dict]:
        """
        Get current Azure subscription details.
        
        Returns:
            dict: Subscription information including id, name, and tenantId
            None: If not logged in or error occurs
        
        Best Practice: Provide context about current Azure environment
        """
        try:
            result = subprocess.run(
                'az account show',
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                timeout=10
            )
            subscription = json.loads(result.stdout)
            logger.info(
                f"Current subscription: {subscription.get('name')} "
                f"({subscription.get('id')})"
            )
            return subscription
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, 
                FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to get subscription info: {e}")
            return None


# Singleton instance for backward compatibility
_global_auth_manager: Optional[AzureAuthManager] = None


def _get_auth_manager(config: Optional[Dict] = None) -> AzureAuthManager:
    """
    Get or create global auth manager instance.
    
    Best Practice: Use singleton pattern to share token cache
    """
    global _global_auth_manager
    if _global_auth_manager is None or config is not None:
        _global_auth_manager = AzureAuthManager(config)
    return _global_auth_manager


# Backward compatible wrapper functions
def get_azure_access_token(
    resource: Optional[str] = None,
    resource_type: Optional[str] = None,
    config: Optional[Dict] = None
) -> str:
    """
    Generate Azure access token using Azure CLI (backward compatible function).
    
    Best Practice: Maintain backward compatibility while encouraging new pattern
    
    Args:
        resource: The Azure resource URL (deprecated - use resource_type)
        resource_type: Resource type from config (recommended)
        config: Optional configuration dictionary
    
    Returns:
        str: The access token
    
    Raises:
        RuntimeError: If token generation fails
        FileNotFoundError: If Azure CLI is not installed
    
    Migration Guide:
        Old: token = get_azure_access_token("https://ossrdbms-aad.database.windows.net")
        New: token = get_azure_access_token(resource_type='postgresql', config=config)
    """
    auth_mgr = _get_auth_manager(config)
    
    # If no resource_type provided, use resource or default
    if not resource_type:
        if resource:
            return auth_mgr.get_azure_access_token(resource=resource)
        else:
            # Use default from config
            return auth_mgr.get_azure_access_token(resource_type='default_database')
    
    return auth_mgr.get_azure_access_token(resource_type=resource_type)


def check_azure_login() -> bool:
    """
    Check if user is logged in to Azure CLI (backward compatible function).
    
    Returns:
        bool: True if logged in, False otherwise
    """
    auth_mgr = _get_auth_manager()
    return auth_mgr.check_azure_login()


def get_current_subscription() -> Optional[dict]:
    """
    Get current Azure subscription details (backward compatible function).
    
    Returns:
        dict: Subscription information including id, name, and tenantId
        None: If not logged in or error occurs
    """
    auth_mgr = _get_auth_manager()
    return auth_mgr.get_current_subscription()