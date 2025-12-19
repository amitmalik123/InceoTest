# SOAP client stub for framework


from zeep import Client as ZeepClient
from zeep.transports import Transport
from zeep.exceptions import Fault
from lxml import etree
import requests
from framework.common.logger import get_logger
from framework.validators.soap_validators import SOAPValidator

logger = get_logger(__name__)

class SoapClient:
    def __init__(self, wsdl_url, enable_validation=False):
        """
        Initialize SOAP client.
        
        Args:
            wsdl_url: URL or path to WSDL file
            enable_validation: Enable SOAP request/response validation (default: False)
        """
        self.wsdl_url = wsdl_url
        # Extract base_url (protocol + host + port) for reporting
        from urllib.parse import urlparse
        parsed = urlparse(wsdl_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.soap_client = None
        self.enable_validation = enable_validation
        self.validator = None
        self._init_soap_client()
        
        # Initialize validator if enabled
        if self.enable_validation:
            try:
                self.validator = SOAPValidator(wsdl_url=wsdl_url)
                logger.info("SOAP validation enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize SOAP validator: {e}. Validation disabled.")
                self.enable_validation = False

    def _init_soap_client(self):
        try:
            transport = Transport()
            self.soap_client = ZeepClient(wsdl=self.wsdl_url, transport=transport)
            logger.info(f"Initialized SOAP client with WSDL: {self.wsdl_url}")
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {e}")
            raise

    def call(self, operation_name, params=None, soap_envelope=None, soap_action=None, validate_request=None):
        """
        Call a SOAP operation with parameters or raw XML envelope.
        
        Args:
            operation_name: Name of the SOAP operation to call
            params: Dictionary of parameters (for JSON-style input) or None
            soap_envelope: Raw SOAP XML envelope string (alternative to params)
            soap_action: SOAP Action header value
            validate_request: Override validation setting for this request (True/False/None)
            
        Returns:
            SOAP response
        """
        if not self.soap_client:
            raise RuntimeError("SOAP client not initialized.")
        
        # Determine if validation should be performed
        should_validate = validate_request if validate_request is not None else self.enable_validation
        
        # If raw XML envelope is provided, send it directly via HTTP
        if soap_envelope and soap_envelope.strip() and soap_envelope != "<Envelope>...</Envelope>":
            # Validate request if enabled
            if should_validate and self.validator:
                is_valid, errors = self.validator.validate_request(
                    soap_envelope=soap_envelope,
                    operation_name=operation_name,
                    validate_envelope=True,
                    validate_wsdl=True
                )
                if not is_valid:
                    error_msg = f"SOAP request validation failed: {errors}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            return self._call_with_raw_xml(soap_envelope, soap_action)
        
        # Otherwise use Zeep's native method call
        try:
            # Validate operation if enabled
            if should_validate and self.validator:
                is_valid, errors = self.validator.validate_request(
                    soap_envelope="",  # No envelope for Zeep calls
                    operation_name=operation_name,
                    params=params,
                    validate_envelope=False,
                    validate_wsdl=True
                )
                if not is_valid:
                    error_msg = f"SOAP operation validation failed: {errors}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Get the operation from the service
            operation = getattr(self.soap_client.service, operation_name, None)
            if not operation:
                # List available operations for debugging
                available_ops = [op for op in dir(self.soap_client.service) if not op.startswith('_')]
                error_msg = f"SOAP operation '{operation_name}' not found. Available operations: {', '.join(available_ops)}"
                logger.error(error_msg)
                raise AttributeError(error_msg)
            
            logger.info(f"SOAP Request (Zeep): {operation_name} params={params}")
            
            # Call with params as keyword arguments if provided
            if params:
                response = operation(**params)
            else:
                response = operation()
                
            logger.info(f"SOAP Response: {response}")
            return response
        except Fault as fault:
            logger.error(f"SOAP Fault: {fault}")
            raise
        except Exception as e:
            logger.error(f"SOAP Error: {e}")
            raise
    
    def _call_with_raw_xml(self, soap_envelope, soap_action=None):
        """
        Send a raw SOAP XML envelope via HTTP POST.
        
        Args:
            soap_envelope: Raw SOAP XML envelope string
            soap_action: SOAP Action header value
            
        Returns:
            Response object with parsed XML
        """
        try:
            # Extract endpoint URL from WSDL (remove ?wsdl)
            endpoint_url = self.wsdl_url.replace('?wsdl', '').replace('?WSDL', '')
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8'
            }
            if soap_action:
                headers['SOAPAction'] = f'"{soap_action}"'
            
            logger.info(f"SOAP Request (Raw XML) to {endpoint_url}")
            
            # Pretty print the SOAP envelope
            try:
                from xml.dom import minidom
                dom = minidom.parseString(soap_envelope)
                pretty_envelope = dom.toprettyxml(indent="  ")
                # Remove XML declaration and extra blank lines
                pretty_lines = [line for line in pretty_envelope.split('\n') if line.strip() and not line.strip().startswith('<?xml')]
                logger.debug(f"SOAP Envelope:\n{chr(10).join(pretty_lines)}")
            except:
                logger.debug(f"SOAP Envelope: {soap_envelope}")
            
            response = requests.post(
                endpoint_url,
                data=soap_envelope.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            logger.info(f"SOAP Response Status: {response.status_code}")
            
            # Pretty print the SOAP response
            try:
                from xml.dom import minidom
                dom = minidom.parseString(response.text)
                pretty_response = dom.toprettyxml(indent="  ")
                # Remove XML declaration and extra blank lines
                pretty_lines = [line for line in pretty_response.split('\n') if line.strip() and not line.strip().startswith('<?xml')]
                logger.debug(f"SOAP Response:\n{chr(10).join(pretty_lines)}")
            except:
                logger.debug(f"SOAP Response: {response.text}")
            
            # Parse XML response
            if response.status_code == 200:
                try:
                    root = etree.fromstring(response.content)
                    result = {'xml_response': response.text, 'status_code': response.status_code, 'parsed': root}
                    
                    # Automatically validate response if validation enabled
                    if self.enable_validation and self.validator:
                        is_valid, errors, fault_info = self.validator.validate_response(
                            response.text,
                            expected_fault=None,
                            validate_envelope=True,
                            soap_version="1.1"
                        )
                        if not is_valid:
                            error_msg = f"SOAP response validation failed: {errors}"
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                        
                        # Store fault info if present
                        if fault_info:
                            result['soap_fault'] = fault_info
                            logger.warning(f"SOAP Fault: {fault_info.get('faultcode')} - {fault_info.get('faultstring')}")
                    
                    return result
                except Exception as parse_error:
                    logger.warning(f"Failed to parse XML response: {parse_error}")
                    return {'xml_response': response.text, 'status_code': response.status_code}
            else:
                return {'xml_response': response.text, 'status_code': response.status_code, 'error': True}
                
        except Exception as e:
            logger.error(f"Raw SOAP call failed: {e}")
            raise
    
    def validate_response(
        self, 
        xml_response: str, 
        expected_fault: dict = None,
        soap_version: str = "1.1"
    ):
        """
        Validate SOAP response.
        
        Args:
            xml_response: SOAP response XML as string
            expected_fault: Expected fault details (optional)
            soap_version: SOAP version ("1.1" or "1.2")
        
        Returns:
            Tuple of (is_valid, errors, fault_info)
        """
        if not self.validator:
            logger.warning("SOAP validator not initialized")
            return True, [], None
        
        return self.validator.validate_response(
            xml_response,
            expected_fault=expected_fault,
            validate_envelope=True,
            soap_version=soap_version
        )
    
    def validate_against_schema(self, xml_content: str, schema_source):
        """
        Validate XML content against XSD schema.
        
        Args:
            xml_content: XML content as string
            schema_source: Path to XSD file or schema content
        
        Returns:
            Tuple of (is_valid, errors)
        """
        if not self.validator:
            logger.warning("SOAP validator not initialized")
            return True, []
        
        return self.validator.validate_against_schema(xml_content, schema_source)
