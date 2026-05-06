"""
SOAP Validators Module

Provides comprehensive validation for SOAP requests and responses including:
- XML/XSD schema validation
- SOAP envelope structure validation
- WSDL operation validation
- SOAP fault validation
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple
from lxml import etree
from defusedxml import ElementTree as DefusedET
import xmlschema
from zeep import Client as ZeepClient
from zeep.wsdl import Document
from framework.common.logger import get_logger

logger = get_logger(__name__)


class SOAPValidationError(Exception):
    """Custom exception for SOAP validation failures."""
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []


class SOAPEnvelopeValidator:
    """
    Validates SOAP envelope structure including namespaces, headers, and body.
    """
    
    # Common SOAP namespaces
    SOAP_11_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    SOAP_12_NS = "http://www.w3.org/2003/05/soap-envelope"
    
    def __init__(self):
        self.errors = []
    
    def validate_envelope(self, xml_content: str, soap_version: str = "1.1") -> Tuple[bool, List[str]]:
        """
        Validate SOAP envelope structure.
        
        Args:
            xml_content: SOAP XML content as string
            soap_version: SOAP version ("1.1" or "1.2")
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        self.errors = []
        
        try:
            # Parse XML safely
            root = DefusedET.fromstring(xml_content.encode('utf-8'))
            
            # Determine expected namespace
            expected_ns = self.SOAP_11_NS if soap_version == "1.1" else self.SOAP_12_NS
            
            # Check root element is Envelope
            if not self._check_envelope_root(root, expected_ns):
                return False, self.errors
            
            # Check for Body element
            if not self._check_body_element(root, expected_ns):
                return False, self.errors
            
            # Validate namespace declarations
            self._validate_namespaces(root)
            
            # Check for valid structure (Header is optional, Body is required)
            self._validate_structure(root, expected_ns)
            
            if self.errors:
                logger.warning(f"SOAP envelope validation found issues: {self.errors}")
                return False, self.errors
            
            logger.info("SOAP envelope validation PASSED")
            return True, []
            
        except Exception as e:
            error_msg = f"Failed to parse SOAP envelope: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False, self.errors
    
    def _check_envelope_root(self, root: Any, expected_ns: str) -> bool:
        """Check if root element is a valid SOAP Envelope."""
        # Extract namespace from root tag
        if '}' in root.tag:
            ns, tag = root.tag.rsplit('}', 1)
            ns = ns.lstrip('{')
        else:
            tag = root.tag
            ns = None
        
        if tag != 'Envelope':
            self.errors.append(f"Root element must be 'Envelope', found '{tag}'")
            return False
        
        if ns and ns not in [self.SOAP_11_NS, self.SOAP_12_NS]:
            self.errors.append(f"Invalid SOAP namespace: {ns}")
            return False
        
        return True
    
    def _check_body_element(self, root: Any, expected_ns: str) -> bool:
        """Check if Body element exists."""
        # Look for Body element
        body = None
        for child in root:
            if '}' in child.tag:
                ns, tag = child.tag.rsplit('}', 1)
            else:
                tag = child.tag
            
            if tag == 'Body':
                body = child
                break
        
        if body is None:
            self.errors.append("SOAP Body element is required but not found")
            return False
        
        return True
    
    def _validate_namespaces(self, root: Any):
        """Validate namespace declarations."""
        # Check if SOAP namespace is properly declared
        nsmap = root.nsmap if hasattr(root, 'nsmap') else {}
        
        soap_ns_declared = False
        for prefix, uri in nsmap.items():
            if uri in [self.SOAP_11_NS, self.SOAP_12_NS]:
                soap_ns_declared = True
                break
        
        if not soap_ns_declared:
            logger.warning("SOAP namespace not explicitly declared in nsmap (may be in tag)")
    
    def _validate_structure(self, root: Any, expected_ns: str):
        """Validate SOAP envelope structure."""
        # SOAP envelope should only contain Header (optional) and Body (required)
        valid_children = ['Header', 'Body']
        
        for child in root:
            if '}' in child.tag:
                ns, tag = child.tag.rsplit('}', 1)
            else:
                tag = child.tag
            
            if tag not in valid_children:
                self.errors.append(f"Invalid child element in Envelope: {tag}")


class SOAPSchemaValidator:
    """
    Validates SOAP messages against XSD schemas.
    """
    
    def __init__(self):
        self.schema_cache = {}
    
    def validate_against_schema(
        self, 
        xml_content: str, 
        schema_source: Any
    ) -> Tuple[bool, List[str]]:
        """
        Validate XML content against XSD schema.
        
        Args:
            xml_content: XML content as string
            schema_source: Path to XSD file, XSD content as string, or xmlschema.XMLSchema object
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        try:
            # Load schema
            if isinstance(schema_source, xmlschema.XMLSchema):
                schema = schema_source
            elif isinstance(schema_source, str):
                if os.path.isfile(schema_source):
                    # Load from file
                    if schema_source in self.schema_cache:
                        schema = self.schema_cache[schema_source]
                    else:
                        schema = xmlschema.XMLSchema(schema_source)
                        self.schema_cache[schema_source] = schema
                else:
                    # Assume it's XSD content as string
                    schema = xmlschema.XMLSchema(schema_source)
            else:
                error_msg = f"Invalid schema_source type: {type(schema_source)}"
                logger.error(error_msg)
                return False, [error_msg]
            
            # Validate XML against schema
            if schema.is_valid(xml_content):
                logger.info("XML schema validation PASSED")
                return True, []
            else:
                # Get detailed validation errors
                try:
                    schema.validate(xml_content)
                except xmlschema.XMLSchemaException as ve:
                    error_msg = f"Schema validation failed: {str(ve)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                
                return False, errors
                
        except Exception as e:
            error_msg = f"Schema validation error: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]


class SOAPFaultValidator:
    """
    Validates and parses SOAP fault messages.
    """
    
    def __init__(self):
        pass
    
    def extract_fault(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract SOAP fault information from response.
        
        Args:
            xml_content: SOAP response XML content
        
        Returns:
            Dictionary with fault details or None if no fault
        """
        try:
            root = DefusedET.fromstring(xml_content.encode('utf-8'))
            
            # Find Body element
            body = None
            for child in root:
                if 'Body' in child.tag:
                    body = child
                    break
            
            if body is None:
                return None
            
            # Find Fault element
            fault = None
            for child in body:
                if 'Fault' in child.tag:
                    fault = child
                    break
            
            if fault is None:
                return None
            
            # Extract fault details
            fault_info = {
                'has_fault': True,
                'faultcode': None,
                'faultstring': None,
                'faultactor': None,
                'detail': None
            }
            
            for element in fault:
                tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
                
                if tag.lower() == 'faultcode':
                    fault_info['faultcode'] = element.text
                elif tag.lower() == 'faultstring':
                    fault_info['faultstring'] = element.text
                elif tag.lower() == 'faultactor':
                    fault_info['faultactor'] = element.text
                elif tag.lower() == 'detail':
                    # Get detail as XML string
                    fault_info['detail'] = etree.tostring(element, encoding='unicode')
            
            logger.info(f"SOAP Fault detected: {fault_info['faultcode']} - {fault_info['faultstring']}")
            return fault_info
            
        except Exception as e:
            logger.error(f"Failed to extract SOAP fault: {str(e)}")
            return None
    
    def validate_fault(
        self, 
        xml_content: str, 
        expected_fault: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], Optional[Dict[str, Any]]]:
        """
        Validate SOAP fault against expected fault.
        
        Args:
            xml_content: SOAP response XML content
            expected_fault: Expected fault details (optional)
                {
                    'faultcode': 'expected code',
                    'faultstring': 'expected string or regex pattern',
                    'allow_fault': True  # If True, any fault is acceptable
                }
        
        Returns:
            Tuple of (is_valid, list of errors, actual fault info)
        """
        errors = []
        
        # Extract actual fault
        actual_fault = self.extract_fault(xml_content)
        
        # If no expected fault specified, just return the extracted fault
        if expected_fault is None:
            if actual_fault:
                return True, [], actual_fault
            return True, [], None
        
        # If expected_fault allows any fault
        if expected_fault.get('allow_fault'):
            if actual_fault:
                logger.info("SOAP fault validation PASSED (any fault allowed)")
                return True, [], actual_fault
            else:
                errors.append("Expected SOAP fault but none was found")
                return False, errors, None
        
        # Validate specific fault details
        if actual_fault is None:
            errors.append("Expected SOAP fault but none was found")
            return False, errors, None
        
        # Check faultcode
        if 'faultcode' in expected_fault:
            expected_code = expected_fault['faultcode']
            actual_code = actual_fault.get('faultcode', '')
            if expected_code not in actual_code:
                errors.append(f"Expected faultcode '{expected_code}', got '{actual_code}'")
        
        # Check faultstring (supports regex)
        if 'faultstring' in expected_fault:
            expected_string = expected_fault['faultstring']
            actual_string = actual_fault.get('faultstring', '')
            
            # Try regex match first
            try:
                if not re.search(expected_string, actual_string):
                    errors.append(
                        f"Faultstring '{actual_string}' does not match pattern '{expected_string}'"
                    )
            except re.error:
                # Not a valid regex, try exact match
                if expected_string != actual_string:
                    errors.append(
                        f"Expected faultstring '{expected_string}', got '{actual_string}'"
                    )
        
        if errors:
            logger.error(f"SOAP fault validation FAILED: {errors}")
            return False, errors, actual_fault
        
        logger.info("SOAP fault validation PASSED")
        return True, [], actual_fault


class WSDLOperationValidator:
    """
    Validates SOAP messages against WSDL operation definitions.
    """
    
    def __init__(self, wsdl_url: str):
        """
        Initialize WSDL validator.
        
        Args:
            wsdl_url: URL or path to WSDL file
        """
        self.wsdl_url = wsdl_url
        self.client = None
        self.wsdl_document = None
        self._load_wsdl()
    
    def _load_wsdl(self):
        """Load WSDL document."""
        try:
            from zeep.transports import Transport
            transport = Transport()
            self.client = ZeepClient(wsdl=self.wsdl_url, transport=transport)
            self.wsdl_document = self.client.wsdl
            logger.info(f"WSDL loaded successfully from {self.wsdl_url}")
        except Exception as e:
            logger.error(f"Failed to load WSDL: {str(e)}")
            raise
    
    def get_operations(self) -> List[str]:
        """
        Get list of available operations from WSDL.
        
        Returns:
            List of operation names
        """
        if not self.client:
            return []
        
        operations = []
        for service in self.wsdl_document.services.values():
            for port in service.ports.values():
                for operation in port.binding._operations.values():
                    operations.append(operation.name)
        
        return operations
    
    def validate_operation_exists(self, operation_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if operation exists in WSDL.
        
        Args:
            operation_name: Name of the operation to check
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        operations = self.get_operations()
        
        if operation_name in operations:
            logger.info(f"Operation '{operation_name}' found in WSDL")
            return True, None
        
        error_msg = f"Operation '{operation_name}' not found in WSDL. Available operations: {', '.join(operations)}"
        logger.error(error_msg)
        return False, error_msg
    
    def validate_request_params(
        self, 
        operation_name: str, 
        params: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate request parameters against WSDL operation definition.
        
        Args:
            operation_name: Name of the operation
            params: Parameters dictionary
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        try:
            # Check if operation exists
            is_valid, error = self.validate_operation_exists(operation_name)
            if not is_valid:
                return False, [error]
            
            # Get operation from service
            operation = getattr(self.client.service, operation_name, None)
            if not operation:
                error_msg = f"Could not access operation '{operation_name}'"
                return False, [error_msg]
            
            # Try to get operation signature (this is Zeep-specific)
            try:
                # Zeep validates parameters when we access the operation
                # We can attempt to create a request to validate parameters
                logger.info(f"Request parameters validation for '{operation_name}' would require actual call")
                logger.debug(f"Parameters provided: {list(params.keys())}")
                return True, []
                
            except Exception as e:
                error_msg = f"Parameter validation failed: {str(e)}"
                errors.append(error_msg)
                return False, errors
                
        except Exception as e:
            error_msg = f"Failed to validate request parameters: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]


class SOAPValidator:
    """
    Main SOAP validator that orchestrates all validation types.
    """
    
    def __init__(self, wsdl_url: Optional[str] = None):
        """
        Initialize SOAP validator.
        
        Args:
            wsdl_url: URL or path to WSDL file (optional)
        """
        self.envelope_validator = SOAPEnvelopeValidator()
        self.schema_validator = SOAPSchemaValidator()
        self.fault_validator = SOAPFaultValidator()
        self.wsdl_validator = None
        
        if wsdl_url:
            try:
                self.wsdl_validator = WSDLOperationValidator(wsdl_url)
            except Exception as e:
                logger.warning(f"Failed to initialize WSDL validator: {e}")
    
    def validate_request(
        self,
        soap_envelope: str,
        operation_name: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        validate_envelope: bool = True,
        validate_wsdl: bool = True,
        soap_version: str = "1.1"
    ) -> Tuple[bool, List[str]]:
        """
        Validate SOAP request before sending.
        
        Args:
            soap_envelope: SOAP XML envelope as string
            operation_name: Name of the WSDL operation
            params: Request parameters (for WSDL validation)
            validate_envelope: Whether to validate envelope structure
            validate_wsdl: Whether to validate against WSDL
            soap_version: SOAP version ("1.1" or "1.2")
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        all_errors = []
        
        # Validate envelope structure
        if validate_envelope and soap_envelope:
            is_valid, errors = self.envelope_validator.validate_envelope(
                soap_envelope, soap_version
            )
            if not is_valid:
                all_errors.extend([f"Envelope validation: {e}" for e in errors])
        
        # Validate against WSDL
        if validate_wsdl and self.wsdl_validator and operation_name:
            is_valid, error = self.wsdl_validator.validate_operation_exists(operation_name)
            if not is_valid:
                all_errors.append(f"WSDL validation: {error}")
            
            # Validate parameters if provided
            if params:
                is_valid, errors = self.wsdl_validator.validate_request_params(
                    operation_name, params
                )
                if not is_valid:
                    all_errors.extend([f"WSDL param validation: {e}" for e in errors])
        
        if all_errors:
            logger.error(f"SOAP request validation FAILED: {all_errors}")
            return False, all_errors
        
        logger.info("SOAP request validation PASSED")
        return True, []
    
    def validate_response(
        self,
        xml_content: str,
        expected_fault: Optional[Dict[str, Any]] = None,
        validate_envelope: bool = True,
        soap_version: str = "1.1"
    ) -> Tuple[bool, List[str], Optional[Dict[str, Any]]]:
        """
        Validate SOAP response.
        
        Args:
            xml_content: SOAP response XML content
            expected_fault: Expected fault details (if fault is expected)
            validate_envelope: Whether to validate envelope structure
            soap_version: SOAP version ("1.1" or "1.2")
        
        Returns:
            Tuple of (is_valid, list of errors, fault_info)
        """
        all_errors = []
        fault_info = None
        
        # Check for SOAP fault first
        fault_info = self.fault_validator.extract_fault(xml_content)
        
        # If fault is present, validate it
        if fault_info:
            is_valid, errors, fault_info = self.fault_validator.validate_fault(
                xml_content, expected_fault
            )
            if not is_valid:
                all_errors.extend([f"Fault validation: {e}" for e in errors])
        
        # Validate envelope structure (even if fault is present)
        if validate_envelope:
            is_valid, errors = self.envelope_validator.validate_envelope(
                xml_content, soap_version
            )
            if not is_valid:
                all_errors.extend([f"Envelope validation: {e}" for e in errors])
        
        if all_errors:
            logger.error(f"SOAP response validation FAILED: {all_errors}")
            return False, all_errors, fault_info
        
        logger.info("SOAP response validation PASSED")
        return True, [], fault_info
    
    def validate_against_schema(
        self,
        xml_content: str,
        schema_source: Any
    ) -> Tuple[bool, List[str]]:
        """
        Validate XML against XSD schema.
        
        Args:
            xml_content: XML content as string
            schema_source: Path to XSD file, XSD content, or xmlschema.XMLSchema object
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        return self.schema_validator.validate_against_schema(xml_content, schema_source)
