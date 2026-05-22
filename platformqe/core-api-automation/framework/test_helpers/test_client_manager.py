"""
Test Client Manager

Manages client initialization for different protocols (REST, SOAP, DB_ONLY).
Centralizes client creation and request execution logic.
"""

from typing import Dict, Any, Optional, Tuple
import time
import os
from contextlib import ExitStack
from framework.common.logger import get_logger
from framework.loaders.config_loader import substitute_env_vars
from framework.common.utils import normalize_path

logger = get_logger(__name__)


class TestClientManager:
    """
    Handles client creation and request execution for REST/SOAP/DB_ONLY protocols.
    Provides unified interface for different protocol types.
    """
    
    def __init__(self):
        """
        Initialize client manager.
        """
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
            
            # Get WSDL URL - either explicit wsdl_url or construct from mainURL + endpoint
            wsdl_url = case.get('wsdl_url')
            if not wsdl_url:
                main_url = case.get('mainURL', '')
                endpoint = case.get('endpoint', '')
                if not endpoint:
                    raise ValueError("SOAP protocol requires 'wsdl_url' or 'endpoint' in test case")
                
                # Get base_url from config based on service_name
                service_name = case.get('service_name')
                base_url = ''
                if service_name:
                    api_endpoints = config.get('api_endpoints', {})
                    if service_name in api_endpoints:
                        base_url = substitute_env_vars(api_endpoints[service_name].get('base_url', ''))
                
                # Resolve template variables in mainURL (e.g., {{base_url}})
                from framework.common.template_utils import render_template
                template_context = {'base_url': base_url}
                main_url = render_template(main_url, template_context)
                
                # Construct full WSDL URL: mainURL + endpoint + ?wsdl
                wsdl_url = f"{main_url.rstrip('/')}{endpoint}"
                if '?wsdl' not in wsdl_url.lower():
                    wsdl_url += '?wsdl'
            
            logger.info(f"Creating SOAP client for WSDL: {wsdl_url}")
            return self.soap_client_class(wsdl_url, enable_validation=True)
        
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
            # For SOAP, use SoapClient.call with support for both params and raw XML
            operation = case.get('wsdl_operation') or case.get('operation') or method
            params = payload if payload else {}
            soap_envelope_raw = case.get('soap_envelope')
            soap_action = case.get('soap_action')
            
            # Process soap_envelope: support inline XML, file path, or template variables
            soap_envelope = self._load_soap_envelope(soap_envelope_raw, case)
            
            logger.info(f"Executing SOAP operation: {operation}")
            
            response_json = client.call(operation, params, soap_envelope, soap_action, validate_request=True)
            response = self._create_soap_response(response_json, case)
            response_time_ms = (time.time() - start_time) * 1000
            
        else:
            # For REST/HTTP, use ApiClient.request
            # Extract headers_additional from case if available
            # Note: headers should already be rendered by test_api_generic.py before calling execute_request
            headers = case.get('headers_additional', {}) if case else {}

            if isinstance(payload, dict) and payload.get('_multipart_files'):
                response = self._execute_multipart_request(client, method, endpoint, payload, headers)
            elif isinstance(payload, str):
                if headers:
                    response = client.request(method, endpoint, data=payload, headers=headers)
                else:
                    response = client.request(method, endpoint, data=payload)
            elif payload:
                if headers:
                    response = client.request(method, endpoint, json=payload, headers=headers)
                else:
                    response = client.request(method, endpoint, json=payload)
            else:
                if headers:
                    response = client.request(method, endpoint, headers=headers)
                else:
                    response = client.request(method, endpoint)
            
            response_time_ms = (
                response.elapsed.total_seconds() * 1000 
                if hasattr(response, 'elapsed') 
                else (time.time() - start_time) * 1000
            )
        
        return response, response_time_ms

    def _execute_multipart_request(
        self,
        client: Any,
        method: str,
        endpoint: str,
        payload: Dict,
        headers: Dict
    ) -> Any:
        """
        Execute multipart/form-data request when payload contains _multipart_files.
        """
        multipart_files = payload.get('_multipart_files', {})
        form_data = {
            key: value
            for key, value in payload.items()
            if key != '_multipart_files'
        }

        # Remove Content-Type so requests can generate multipart boundary.
        request_headers = dict(headers or {})
        request_headers.pop('Content-Type', None)

        with ExitStack() as stack:
            files = {}
            for field_name, file_spec in multipart_files.items():
                file_path, content_type, file_name = self._parse_file_spec(file_spec)
                resolved_path = self._resolve_upload_file_path(file_path)
                file_obj = stack.enter_context(open(resolved_path, 'rb'))
                if not file_name:
                    file_name = os.path.basename(resolved_path)

                if content_type:
                    files[field_name] = (file_name, file_obj, content_type)
                else:
                    files[field_name] = (file_name, file_obj)

            logger.info(f"Executing multipart upload for fields: {list(files.keys())}")
            if request_headers:
                return client.request(method, endpoint, data=form_data, files=files, headers=request_headers)
            return client.request(method, endpoint, data=form_data, files=files)

    def _parse_file_spec(self, file_spec: Any) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse supported file spec formats into (path, content_type, filename)."""
        if isinstance(file_spec, str):
            return file_spec, None, None

        if isinstance(file_spec, dict):
            file_path = file_spec.get('path')
            if not file_path:
                raise ValueError("Multipart file spec must include 'path'.")
            return file_path, file_spec.get('content_type'), file_spec.get('filename')

        raise ValueError(f"Unsupported multipart file spec type: {type(file_spec)}")

    def _resolve_upload_file_path(self, file_path: str) -> str:
        """Resolve upload file path from absolute path, repo root, or testdata folder."""
        normalized = normalize_path(file_path)

        candidates = [normalized]
        if not os.path.isabs(normalized):
            candidates.append(os.path.join('testdata', normalized))

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        raise FileNotFoundError(
            f"Upload file not found: {file_path}. Checked: {', '.join(candidates)}"
        )
    
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
    
    def _create_soap_response(self, response_json: Dict, case: Dict = None) -> Any:
        """
        Create SOAP response wrapper.
        
        Args:
            response_json: SOAP response dictionary
            case: Test case (optional, for extracting XML response)
        
        Returns:
            Response object with standard interface
        """
        class SOAPResponse:
            def __init__(self, json_data):
                self._json_data = json_data
                self.status_code = json_data.get('status_code', 200) if isinstance(json_data, dict) else 200
                self.headers = {}
                # Store XML response if available
                self.xml_response = json_data.get('xml_response', '') if isinstance(json_data, dict) else ''
                self.text = self.xml_response or str(json_data)
            
            def json(self):
                return self._json_data
        
        return SOAPResponse(response_json)
    
    def _load_soap_envelope(self, soap_envelope_raw: str, case: Dict) -> str:
        """
        Load SOAP envelope from inline XML, file path, or render template variables.

        Args:
            soap_envelope_raw: Raw soap_envelope value from test case
            case: Test case dictionary for context

        Returns:
            Processed SOAP envelope string or None
        """
        if not soap_envelope_raw or soap_envelope_raw == "<Envelope>...</Envelope>":
            return None

        # Check if it's a file path (doesn't start with < and ends with .xml)
        soap_envelope_trimmed = soap_envelope_raw.strip()
        if not soap_envelope_trimmed.startswith('<') and soap_envelope_trimmed.endswith('.xml'):
            # Load from file
            import os
            from framework.common.utils import normalize_path

            file_path = normalize_path(soap_envelope_trimmed)

            # Resolve path relative to testdata/ if not absolute
            if not os.path.isabs(file_path):
                file_path = os.path.join('testdata', file_path)

            if not os.path.exists(file_path):
                logger.warning(f"SOAP envelope file not found: {file_path}, using raw value")
                return soap_envelope_raw

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    soap_envelope_content = f.read()
                logger.info(f"Loaded SOAP envelope from file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load SOAP envelope file {file_path}: {e}")
                return soap_envelope_raw
        else:
            # Use inline XML
            soap_envelope_content = soap_envelope_raw
        
        # Render template variables {{var}} from case context
        if '{{' in soap_envelope_content and '}}' in soap_envelope_content:
            from framework.common.template_utils import render_template
            from framework.test_helpers.test_context_manager import get_context_manager
            
            # Get context manager to access global variables
            context_mgr = get_context_manager()
            
            # Build context from case and global variables
            context = dict(case)
            context.update(context_mgr._global_variables)
            
            soap_envelope_content = render_template(soap_envelope_content, context)
            logger.debug(f"Rendered SOAP envelope with template variables")
        
        return soap_envelope_content

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
