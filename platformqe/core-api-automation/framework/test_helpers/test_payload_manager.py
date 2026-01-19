"""
Test Payload Manager

Handles payload loading, construction, and rendering for test requests.
Centralizes all payload-related operations including file loading,
CSV construction, and template rendering.
"""

import os
import json
from typing import Dict, Any, Optional
from framework.common.logger import get_logger
from framework.common.template_utils import render_hybrid
from framework.common.utils import normalize_path

logger = get_logger(__name__)


class PayloadManager:
    """
    Manages test payload preparation from various sources.
    Supports file loading, inline dictionaries, and CSV-based construction.
    """
    
    def __init__(self):
        """Initialize payload manager"""
        logger.debug("PayloadManager initialized")
    
    def load_payload(
        self, 
        case: Dict, 
        context: Dict, 
        method: str,
        test_data: Any = None
    ) -> Optional[Dict]:
        """
        Load payload from file, inline dict, or construct from test_data.
        
        Args:
            case: Test case configuration dictionary
            context: Context dictionary for template rendering
            method: HTTP method (GET, POST, PUT, etc.)
            test_data: Test data for CSV-based construction
        
        Returns:
            Payload dictionary or None for methods without body
        """
        # Check if payload file path is specified
        payload_file_path = self._get_payload_file_path(case)
        
        if payload_file_path:
            # Load from file
            return self._load_from_file(payload_file_path, context)
        
        # Check if constructing from CSV test_data_file
        # Skip CSV construction for SOAP tests that use soap_envelope
        # Also skip if 'payload' key exists and is explicitly null (user doesn't want a body)
        protocol = case.get('protocol', '').upper()
        has_soap_envelope = case.get('soap_envelope') and case.get('soap_envelope') != "<Envelope>...</Envelope>"
        
        # Only construct from CSV if:
        # 1. 'payload' key is NOT present in case (missing, not explicitly null)
        # 2. test_data_file is specified
        # 3. Method is POST, PUT, or PATCH
        # If 'payload' is explicitly set to null, the user intends no request body
        if 'payload' not in case and case.get('test_data_file') and method.upper() in ['POST', 'PUT', 'PATCH']:
            # Skip CSV payload construction for SOAP tests with soap_envelope
            if protocol == 'SOAP' and has_soap_envelope:
                logger.debug("Skipping CSV payload construction for SOAP test with soap_envelope")
                return None
            # Construct from CSV row
            return self._construct_from_csv(case, context)
        
        # Load inline payload or from test_data
        if 'payload' in case:
            payload_field = case['payload']
            
            if isinstance(payload_field, str) and payload_field.strip().endswith('.json'):
                # File path in payload field
                return self._load_from_file(payload_field.strip(), context)
            else:
                # Inline payload (dict or template string)
                return render_hybrid(payload_field, context)
        
        # Try loading from test_data using testdata_key
        if test_data:
            payload_key = case.get('testdata_key', '')
            if payload_key:
                payload = test_data.get(payload_key, None)
                return render_hybrid(payload, context)
        
        # No payload needed (e.g., GET requests)
        return None
    
    def _get_payload_file_path(self, case: Dict) -> Optional[str]:
        """
        Extract payload file path from test case if specified.
        
        Args:
            case: Test case configuration dictionary
        
        Returns:
            Payload file path or None
        """
        if 'payload' not in case:
            return None
        
        payload_field = case['payload']
        
        if isinstance(payload_field, str) and payload_field.strip().endswith(('.json', '.xml')):
            return payload_field.strip()
        
        return None
    
    def _load_from_file(self, file_path: str, context: Dict):
        """
        Load and render payload from JSON or XML file.
        
        Args:
            file_path: Path to payload file (relative or absolute)
            context: Context dictionary for rendering variables
        
        Returns:
            Rendered payload (dict for JSON, str for XML)
        
        Raises:
            FileNotFoundError: If payload file doesn't exist
            ValueError: If payload file is invalid
        """
        # Normalize path separators for cross-platform compatibility
        file_path = normalize_path(file_path)
        
        # Resolve path relative to testdata/ if not absolute
        if not os.path.isabs(file_path):
            file_path = os.path.join('testdata', file_path)
        
        if not os.path.exists(file_path):
            error_msg = f"Payload file not found: {os.path.abspath(file_path)}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Handle XML files
            if file_path.endswith('.xml'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_xml = f.read()
                
                # Render XML with context variables
                rendered_xml = render_template(raw_xml, context)
                
                logger.info(f"Loaded XML payload from file: {file_path}")
                logger.debug(f"Rendered XML payload: {rendered_xml[:200]}...")
                
                return rendered_xml
            
            # Handle JSON files
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_payload = json.load(f)
                
                # Always render the loaded payload with context
                payload = render_hybrid(raw_payload, context)
                
                logger.info(f"Loaded JSON payload from file: {file_path}")
                logger.debug(f"Rendered payload: {payload}")
                
                return payload
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in payload file {file_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load payload file {file_path}: {e}"
            logger.error(error_msg)
            raise
    
    def _construct_from_csv(self, case: Dict, context: Dict) -> Dict:
        """
        Construct payload from CSV test_data row.
        This handles the hardcoded field mapping for specific test types.
        
        Args:
            case: Test case configuration (contains CSV row data)
            context: Context dictionary (contains CSV row data)
        
        Returns:
            Constructed payload dictionary
        
        Note:
            This is hardcoded for specific fields. Consider making this
            configurable via a payload template in the future.
        """
        def get_field(row, key):
            """Get field value from row with whitespace stripping"""
            val = row.get(key, '')
            return val.strip() if isinstance(val, str) else val
        
        # Convert visibility field to boolean
        visibility_raw = get_field(case, 'visibility')
        if isinstance(visibility_raw, str):
            visibility_val = visibility_raw.lower() in ['true', '1', 'yes', 'y']
        else:
            visibility_val = bool(visibility_raw)
        
        # Construct payload with hardcoded structure
        # TODO: Make this configurable via payload template
        payload = {
            'workItemVisibilityPreferenceType': get_field(case, 'workItemVisibilityPreferenceType'),
            'agentAPLID': get_field(case, 'agentAPLID'),
            'visibility': visibility_val,
            'createdBy': get_field(case, 'createdBy')
        }
        
        logger.info(f"Constructed payload from CSV data")
        logger.debug(f"CSV payload: {payload}")
        
        return payload
    
    def merge_extra_params(self, payload: Optional[Dict], extra_param: Dict) -> Optional[Dict]:
        """
        Merge extra_param into payload for negative testing scenarios.
        
        Args:
            payload: Base payload dictionary
            extra_param: Extra parameters to merge
        
        Returns:
            Merged payload or None if base payload was None
        """
        if payload is None or not isinstance(payload, dict):
            return payload
        
        if extra_param and isinstance(extra_param, dict):
            payload.update(extra_param)
            logger.info(f"Merged extra_param into payload: {extra_param}")
        
        return payload
    
    def render_payload(self, payload: Any, context: Dict) -> Any:
        """
        Render payload with context variables.
        
        Args:
            payload: Payload to render (dict, list, string, or primitive)
            context: Context dictionary for variable substitution
        
        Returns:
            Rendered payload with variables substituted
        """
        if payload is None:
            return None
        
        try:
            return render_hybrid(payload, context)
        except Exception as e:
            logger.error(f"Failed to render payload: {e}")
            return payload


# Singleton accessor function
_payload_manager_instance = None

def get_payload_manager() -> PayloadManager:
    """
    Get the singleton PayloadManager instance.
    
    Returns:
        PayloadManager singleton instance
    
    Example:
        >>> payload_mgr = get_payload_manager()
        >>> payload = payload_mgr.load_payload(case, context, method)
        >>> payload = payload_mgr.merge_extra_params(payload, extra_param)
    """
    global _payload_manager_instance
    if _payload_manager_instance is None:
        _payload_manager_instance = PayloadManager()
    return _payload_manager_instance
