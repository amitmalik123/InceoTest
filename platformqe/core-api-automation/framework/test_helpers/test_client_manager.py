"""
Test Client Manager

Manages client initialization for different protocols (REST, SOAP, DB_ONLY).
Centralizes client creation and request execution logic.
"""

from typing import Dict, Any, Optional, Tuple
import time
from framework.common.logger import get_logger

logger = get_logger(__name__)


class TestClientManager:
    """
    Handles client creation and request execution for REST/SOAP/DB_ONLY protocols.
    Provides unified interface for different protocol types.
    """
    
    def __init__(self):
        """Initialize client manager"""
        self.api_client_factory = None
        self.soap_client_class = None
        logger.debug("TestClientManager initialized")
    
    def _lazy_load_factories(self):
        """Lazy load client factories to avoid circular imports"""
        if self.api_client_factory is None:
            from framework.clients.api_client import ApiClientFactory
            self.api_client_factory = ApiClientFactory
        
        if self.soap_client_class is None:
            try:
                from framework.clients.soap_client import SoapClient
                self.soap_client_class = SoapClient
            except ImportError:
                logger.warning("SoapClient not available")
                self.soap_client_class = None
    
    def get_client(
        self, 
        case: Dict, 
        config: Dict,
        fallback_client: Any = None
    ) -> Optional[Any]:
        """
        Return appropriate client based on protocol/method from test case.
        
        Args:
            case: Test case configuration dictionary
            config: Configuration dictionary
            fallback_client: Fallback client if service_name not specified
        
        Returns:
            Client instance (ApiClient, SoapClient, or None for DB_ONLY)
        """
        self._lazy_load_factories()
        
        # Determine protocol - check explicit protocol field first, then fall back to method
        protocol = case.get('protocol', case.get('method', '')).upper()
        
        # For DB_ONLY, skip API client creation
        if protocol == 'DB_ONLY':
            logger.info("DB_ONLY protocol detected - skipping API client creation")
            return None
        
        # For SOAP, initialize SoapClient with wsdl_url from case
        if protocol == 'SOAP':
            if self.soap_client_class is None:
                raise ImportError("SoapClient not available. Install required SOAP dependencies.")
            
            wsdl_url = case.get('wsdl_url') or case.get('endpoint')
            if not wsdl_url:
                raise ValueError("SOAP protocol requires 'wsdl_url' or 'endpoint' in test case")
            
            logger.info(f"Creating SOAP client for WSDL: {wsdl_url}")
            return self.soap_client_class(wsdl_url)
        
        # For REST/HTTP, get API client based on service_name
        service_name = case.get('service_name')
        if service_name:
            logger.info(f"Creating API client for service: {service_name}")
            return self.api_client_factory.get_client(service_name)
        else:
            logger.info("No service_name specified, using fallback client")
            return fallback_client
    
    def get_client_url(self, client: Any, protocol: str = "REST") -> str:
        """
        Get the base URL from client.
        
        Args:
            client: Client instance
            protocol: Protocol type
        
        Returns:
            Base URL string or placeholder
        """
        if client and hasattr(client, 'base_url'):
            return client.base_url
        elif protocol == 'DB_ONLY':
            return "DB_ONLY (No HTTP URL)"
        else:
            return "Unknown"
    
    def execute_request(
        self, 
        client: Any, 
        method: str, 
        endpoint: str, 
        payload: Optional[Dict] = None,
        protocol: str = "REST",
        case: Dict = None
    ) -> Tuple[Any, float]:
        """
        Execute API request and return response with timing.
        Handles REST, SOAP, and DB_ONLY protocols.
        
        Args:
            client: Client instance
            method: HTTP method or operation name
            endpoint: Endpoint or operation path
            payload: Request payload (optional)
            protocol: Protocol type (REST, SOAP, DB_ONLY)
            case: Test case configuration (for SOAP operation)
        
        Returns:
            Tuple of (response, response_time_ms)
        """
        start_time = time.time()
        
        if protocol == 'DB_ONLY':
            # For DB_ONLY tests, create a mock response
            logger.info("Skipping API call for DB_ONLY protocol test")
            response = self._create_mock_response()
            response_time_ms = 0
            
        elif protocol == 'SOAP':
            # For SOAP, use SoapClient.call and create a wrapper response
            operation = case.get('wsdl_operation') or case.get('operation') or method
            params = payload if payload else {}
            
            logger.info(f"Executing SOAP request to operation: {operation}")
            logger.debug(f"SOAP params: {params}")
            
            response_json = client.call(operation, params)
            response = self._create_soap_response(response_json)
            response_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(f"SOAP response: {response_json}")
            
        else:
            # For REST/HTTP, use ApiClient.request
            logger.info(f"Executing {method} request to {endpoint}")
            
            # Extract headers_additional from case if available
            # Note: headers should already be rendered by test_api_generic.py before calling execute_request
            headers = case.get('headers_additional', {}) if case else {}
            
            if payload:
                logger.debug(f"Request payload: {payload}")
                if headers:
                    logger.debug(f"Additional headers: {headers}")
                    response = client.request(method, endpoint, json=payload, headers=headers)
                else:
                    response = client.request(method, endpoint, json=payload)
            else:
                if headers:
                    logger.debug(f"Additional headers: {headers}")
                    response = client.request(method, endpoint, headers=headers)
                else:
                    response = client.request(method, endpoint)
            
            response_time_ms = (
                response.elapsed.total_seconds() * 1000 
                if hasattr(response, 'elapsed') 
                else (time.time() - start_time) * 1000
            )
            
            logger.info(f"Response status: {response.status_code}")
            try:
                logger.debug(f"Response body: {response.json()}")
            except:
                logger.debug(f"Response body (non-JSON): {response.text[:200]}")
        
        return response, response_time_ms
    
    def _create_mock_response(self) -> Any:
        """
        Create mock response for DB_ONLY tests.
        
        Returns:
            Mock response object with standard interface
        """
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = ''
                self.headers = {}
                
            def json(self):
                return {}
        
        return MockResponse()
    
    def _create_soap_response(self, response_json: Dict) -> Any:
        """
        Create SOAP response wrapper.
        
        Args:
            response_json: SOAP response dictionary
        
        Returns:
            Response object with standard interface
        """
        class SOAPResponse:
            def __init__(self, json_data):
                self._json_data = json_data
                self.status_code = 200
                self.headers = {}
                self.text = str(json_data)
            
            def json(self):
                return self._json_data
        
        return SOAPResponse(response_json)


# Singleton accessor function
_client_manager_instance = None

def get_client_manager() -> TestClientManager:
    """
    Get the singleton TestClientManager instance.
    
    Returns:
        TestClientManager singleton instance
    
    Example:
        >>> client_mgr = get_client_manager()
        >>> client = client_mgr.get_client(case, config)
        >>> response, time_ms = client_mgr.execute_request(client, method, endpoint, payload)
    """
    global _client_manager_instance
    if _client_manager_instance is None:
        _client_manager_instance = TestClientManager()
    return _client_manager_instance
