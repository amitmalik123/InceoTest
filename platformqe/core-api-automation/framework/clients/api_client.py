"""
Enhanced API Client Module
Supports multiple API endpoints with centralized configuration management
"""

import sys
import os
import requests
from typing import Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config, substitute_env_vars

logger = get_logger(__name__)

# Import Azure authentication utilities
try:
    from framework.clients.azure_auth import get_azure_access_token, check_azure_login
    AZURE_AUTH_AVAILABLE = True
except ImportError:
    AZURE_AUTH_AVAILABLE = False
    logger.warning("Azure authentication utilities not available.")


class ApiClient:
    """Enhanced API Client with support for authentication, retries, and timeouts"""
    
    def __init__(self, base_url, auth_token=None, custom_headers=None, verify=False, timeout=30, retry_count=3):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.custom_headers = custom_headers or {}
        self.verify = verify
        self.timeout = timeout
        self.retry_count = retry_count

    def request(self, method, endpoint, **kwargs):
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative or absolute URL)
            **kwargs: Additional arguments passed to requests.request()
                     headers: Additional headers to merge with defaults
        
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}" if not endpoint.startswith('http') else endpoint
        
        # Merge headers: start with custom headers from config, then provided headers, then add auth
        import uuid as _uuid
        _generated = {}
        headers = {}
        for k, v in self.custom_headers.items():
            if v == 'DYNAMIC_UUID4':
                val = str(_uuid.uuid4())
                _generated[k] = val
            else:
                val = v
            headers[k] = val
        # Store generated header values so extract_values can capture them (e.g. for AC4/AC5 replay)
        self.last_generated_headers = _generated
        headers.update(kwargs.pop('headers', {}))
        # Remove headers with None value — allows test cases to explicitly omit a config header via null
        headers = {k: v for k, v in headers.items() if v is not None}
        
        # Add authentication token if available
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        # Remove Content-Type for GET requests
        if method.upper() == 'GET':
            if 'Content-Type' in headers:
                headers.pop('Content-Type')
            kwargs.pop('json', None)
            kwargs.pop('data', None)
        
        # Set timeout
        kwargs.setdefault('timeout', self.timeout)
        
        logger.info(f"REST Request: {method} {url}")
        logger.debug(f"REST Request Headers: {headers}")
        
        # Pretty print request payload
        if 'json' in kwargs:
            try:
                import json
                pretty_payload = json.dumps(kwargs['json'], indent=2)
                logger.debug(f"REST Request Body:\n{pretty_payload}")
            except:
                logger.debug(f"REST Request Body: {kwargs['json']}")
        elif 'data' in kwargs:
            logger.debug(f"REST Request Body: {kwargs['data']}")
        
        # Retry logic
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                response = requests.request(method, url, headers=headers, verify=self.verify, **kwargs)
                logger.info(f"REST Response Status: {response.status_code}")
                
                # Pretty print response body
                try:
                    import json
                    response_json = response.json()
                    pretty_response = json.dumps(response_json, indent=2)
                    logger.debug(f"REST Response Body:\n{pretty_response}")
                except:
                    # Not JSON or empty response
                    if response.text:
                        logger.debug(f"REST Response Body: {response.text[:500]}")
                
                if response.status_code >= 200 and response.status_code < 300:
                    return response
                elif attempt < self.retry_count - 1:
                    logger.warning(f"Request failed with status {response.status_code}, retrying... (attempt {attempt + 1}/{self.retry_count})")
                else:
                    return response
            except Exception as e:
                last_exception = e
                if attempt < self.retry_count - 1:
                    logger.warning(f"Request failed with error: {e}, retrying... (attempt {attempt + 1}/{self.retry_count})")
                else:
                    logger.error(f"Request failed after {self.retry_count} attempts: {e}")
                    raise
        
        if last_exception:
            raise last_exception
        
        return response


class ApiClientFactory:
    """
    Factory class to create and manage multiple API clients
    Supports centralized configuration and client pooling
    """
    
    _instances = {}  # Client pool
    _config = None
    
    @classmethod
    def load_config(cls, env: str = None):
        """Load API configuration using centralized ConfigManager"""
        if cls._config:
            return cls._config
        
        # Use centralized config manager
        cls._config = get_config(reload=False)
        logger.info(f"Loaded API configuration from ConfigManager")
        
        return cls._config
    
    @classmethod
    def get_client(cls, service_name: str = None) -> ApiClient:
        """
        Get or create an API client
        
        Args:
            service_name: Name of the API service in config (e.g., 'work_item_notification')
                         If None, uses legacy api_base_url
        
        Returns:
            ApiClient instance
        """
        # Load config if not already loaded
        if not cls._config:
            cls.load_config()
        
        # Return existing client if available
        pool_key = service_name or 'default'
        if pool_key in cls._instances:
            logger.info(f"Reusing existing API client: {pool_key}")
            return cls._instances[pool_key]
        
        # Get API endpoint configuration
        base_url = None
        auth_token = None
        custom_headers = {}
        timeout = 30
        retry_count = 3
        verify = False
        
        if service_name:
            # Get from api_endpoints configuration
            api_endpoints = cls._config.get('api_endpoints', {})
            if service_name in api_endpoints:
                endpoint_config = api_endpoints[service_name]
                base_url = substitute_env_vars(endpoint_config.get('base_url'))
                auth_token = substitute_env_vars(endpoint_config.get('auth_token'))
                
                # Load custom headers from config
                if 'custom_headers' in endpoint_config:
                    custom_headers = {k: substitute_env_vars(v) for k, v in endpoint_config['custom_headers'].items()}
                
                timeout = int(substitute_env_vars(str(endpoint_config.get('timeout', 30))))
                retry_count = int(substitute_env_vars(str(endpoint_config.get('retry_count', 3))))
                verify = endpoint_config.get('verify', False)
                use_azure_auth = endpoint_config.get('use_azure_auth', False)
                azure_resource = endpoint_config.get('azure_resource', 'https://management.azure.com/')
                
                # Azure AD Authentication support
                if use_azure_auth and AZURE_AUTH_AVAILABLE:
                    try:
                        logger.info(f"Using Azure AD authentication for API: {service_name}")
                        if not check_azure_login():
                            raise RuntimeError("Not logged in to Azure CLI. Please run 'az login' first.")
                        
                        auth_token = get_azure_access_token(azure_resource)
                        logger.info("✓ Azure AD access token generated successfully")
                    except Exception as e:
                        logger.error(f"Azure AD authentication failed: {e}")
                        raise
                elif use_azure_auth and not AZURE_AUTH_AVAILABLE:
                    logger.warning("Azure AD authentication requested but not available.")
                
                # Handle special case where auth_token might be a placeholder for Azure auth
                if auth_token and auth_token.upper() in ['AZURE_AD', 'AZURE_AUTH', 'USE_AZURE_AD']:
                    if AZURE_AUTH_AVAILABLE:
                        try:
                            logger.info(f"Auth token placeholder detected, using Azure AD authentication")
                            auth_token = get_azure_access_token(azure_resource)
                        except Exception as e:
                            logger.error(f"Failed to get Azure AD token: {e}")
                            raise
                    else:
                        raise ValueError("Azure AD authentication requested but azure_auth module not available")
            else:
                raise ValueError(f"API endpoint '{service_name}' not found in configuration")
        else:
            # Legacy: use api_base_url from config
            base_url = substitute_env_vars(cls._config.get('api_base_url'))
            auth_token = substitute_env_vars(cls._config.get('auth_token'))
        
        if not base_url:
            raise ValueError(f"No base URL found for API service: {service_name or 'default'}")
        
        # Create new client
        client = ApiClient(
            base_url=base_url,
            auth_token=auth_token,
            custom_headers=custom_headers,
            verify=verify,
            timeout=timeout,
            retry_count=retry_count
        )
        
        # Store in pool
        cls._instances[pool_key] = client
        logger.info(f"Created new API client: {pool_key} -> {base_url}")
        
        return client
    
    @classmethod
    def clear_pool(cls):
        """Clear the client pool"""
        cls._instances.clear()
        logger.info("API client pool cleared")


# Usage examples:
"""
# Using factory to get API client for specific service
client = ApiClientFactory.get_client('work_item_notification')
response = client.request('GET', '/api/workitems')

# Using default/legacy client
client = ApiClientFactory.get_client()
response = client.request('POST', '/api/users', json={'name': 'John'})

# In test fixtures
@pytest.fixture(scope="function")
def client(config):
    service_name = config.get('service_name')
    return ApiClientFactory.get_client(service_name)
"""