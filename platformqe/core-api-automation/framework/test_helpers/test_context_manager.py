"""
Test Context Manager

Manages test execution context, variable extraction, and global state.
Centralizes all context-related operations and eliminates duplicate extraction logic.
"""

from typing import Dict, List, Any, Optional
from framework.common.logger import get_logger
from framework.common.template_utils import render_template, render_hybrid
from framework.common.common_functions import extract_value
from framework.common.utils import random_string, random_email, random_firstname, random_lastname, random_int, random_numeric

logger = get_logger(__name__)


class TestContextManager:
    """
    Centralized context and variable management for test execution.
    Handles context creation, variable extraction, and global state management.
    Singleton pattern ensures consistent state across test cases.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super(TestContextManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize context manager (only once due to singleton)"""
        if self._initialized:
            return
        
        self._global_variables: Dict[str, Any] = {}  # Replaces extracted_globals
        self._initialized = True
        logger.debug("TestContextManager initialized")
    
    def create_context(
        self, 
        case: Dict, 
        test_data: Any, 
        api_defs: Dict
    ) -> Dict:
        """
        Build test execution context from case, test_data, and extracted globals.
        
        Args:
            case: Test case configuration dictionary
            test_data: Test data (dict, list, or None)
            api_defs: API definitions dictionary
        
        Returns:
            Complete context dictionary for template rendering
        """
        context = {}
        
        # Add utility functions for template rendering
        context['random_string'] = random_string
        context['random_int'] = random_int
        context['random_numeric'] = random_numeric
        context['random_email'] = random_email
        context['random_firstname'] = random_firstname
        context['random_lastname'] = random_lastname
        
        # Add extracted values from previous test cases (chaining)
        context.update(self._global_variables)
        
        # Add test data to context
        if test_data:
            if isinstance(test_data, list) and test_data:
                # Use first row if list (parameterization handles multiple rows)
                context.update(test_data[0])
            elif isinstance(test_data, dict):
                context.update(test_data)
        
        # Add current test case data (overrides test_data if conflicts)
        context.update(case)
        
        logger.debug(f"Created context for test_id: {case.get('test_id')} with "
                    f"{len(context)} variables (including {len(self._global_variables)} global)")
        
        return context
    
    def extract_value_single(
        self, 
        source_type: str, 
        source_data: Any, 
        key: str = None, 
        assign_to: str = None,
        record_count: bool = False,
        array_path: str = None
    ) -> Optional[Any]:
        """
        Extract single value from response or db_result and store in global state.
        
        Args:
            source_type: Source type ('response' or 'db_result')
            source_data: Source data to extract from
            key: Key path to extract (supports dot notation) - optional if record_count is True
            assign_to: Variable name to assign extracted value to
            record_count: If True, extract count of array items at array_path
            array_path: Path to array for counting (used with record_count)
        
        Returns:
            Extracted value or None if extraction failed
        """
        try:
            # Handle record count extraction
            if record_count and array_path:
                value = extract_value(source_data, key="", record_count=True, array_path=array_path)
            # Handle regular value extraction
            elif key:
                value = extract_value(source_data, key)
            else:
                logger.warning(f"No key or array_path provided for extraction from {source_type}")
                return None
            
            # Store in global variables for use in subsequent test cases
            if assign_to:
                self._global_variables[assign_to] = value
                logger.debug(f"Extracted variable '{assign_to}' from '{source_type}': {value}")
            
            return value
            
        except Exception as e:
            logger.warning(f"Failed to extract from {source_type}: {e}")
            return None
    
    def extract_values_batch(
        self, 
        extract_config: List[Dict], 
        response: Any = None,
        db_result: Any = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Process extract_values array from test case configuration.
        Supports both old and new format:
        - Old: {"from": "api_response", "key": "id", "assign_to": "user_id"}
        - New: {"from": "api_response", "assign": [{"key": "id", "assign_to": "user_id"}]}
        
        Supported source types (backward compatible with legacy names):
        - 'api_response' (or 'response'): API response data
        - 'api_request' (or 'request'): API request payload
        - 'db_result': Database query result
        - 'variable': Previously extracted global variables
        - 'context': Test context variables
        - Direct variable name: Extract from context by name
        
        Args:
            extract_config: List of extraction configurations
            response: Response object (optional)
            db_result: Database result (optional)
            context: Test context dictionary (optional)
        
        Returns:
            Dictionary of extracted variables
        """
        from framework.validators.validators import _resolve_data_source
        
        extracted = {}
        
        if not extract_config:
            return extracted
        
        # Build temporary context for data source resolution
        temp_context = context.copy() if context else {}
        # Add global variables to context for variable extraction
        temp_context.update(self._global_variables)
        
        for extract in extract_config:
            source_type = extract.get('from')
            
            # Normalize legacy naming: 'response' -> 'api_response', 'request' -> 'api_request'
            if source_type == 'response':
                source_type = 'api_response'
            elif source_type == 'request':
                source_type = 'api_request'
            
            # Handle script_result source type - extract from script execution results
            if source_type == 'script_result':
                # Script results should be in context under 'script_result' key
                script_result = temp_context.get('script_result', {})
                
                if not script_result:
                    logger.debug("No script_result in context, skipping extraction")
                    continue
                
                # Extract from script_result.extracted_values
                extracted_values = script_result.get('extracted_values', {})
                
                # Handle nested 'assign' array structure
                if 'assign' in extract and isinstance(extract['assign'], list):
                    for assign_item in extract['assign']:
                        key = assign_item.get('key')
                        assign_to = assign_item.get('assign_to')
                        
                        if key and assign_to:
                            value = extracted_values.get(key)
                            if value is not None:
                                extracted[assign_to] = value
                                self._global_variables[assign_to] = value
                                logger.debug(f"Extracted '{assign_to}' = '{value}' from script_result")
                else:
                    # Old format: {"from": "script_result", "key": "computed_volatility", "assign_to": "expected_vol"}
                    key = extract.get('key')
                    assign_to = extract.get('assign_to')
                    
                    if key and assign_to:
                        value = extracted_values.get(key)
                        if value is not None:
                            extracted[assign_to] = value
                            self._global_variables[assign_to] = value
                            logger.debug(f"Extracted '{assign_to}' = '{value}' from script_result")
                
                continue  # Move to next extract config
            
            # Use validators' _resolve_data_source for consistent logic
            # Include the named query key so that db_results with non-'default' names resolve correctly
            try:
                source_data = _resolve_data_source(
                    data_source_type=source_type,
                    comparison_config={'source': source_type},
                    response=response,
                    context=temp_context
                )
            except Exception as e:
                logger.warning(f"Failed to resolve source '{source_type}': {e}")
                source_data = None
            
            if source_data is None:
                logger.debug(f"Skipping extraction from '{source_type}' - source not available")
                continue
            
            # Check if this uses the new nested 'assign' array structure
            if 'assign' in extract and isinstance(extract['assign'], list):
                # New format: {"from": "response", "assign": [{"key": "id", "assign_to": "user_id"}]}

                for assign_item in extract['assign']:
                    key = assign_item.get('key')
                    assign_to = assign_item.get('assign_to')
                    record_count = assign_item.get('record_count', False)
                    array_path = assign_item.get('array_path')
                    
                    if assign_to:
                        if record_count and array_path:
                            # Extract record count
                            value = self.extract_value_single(
                                source_type, source_data, 
                                key=None, assign_to=assign_to, 
                                record_count=record_count, array_path=array_path
                            )
                        elif key:
                            # Extract regular value
                            value = self.extract_value_single(source_type, source_data, key, assign_to)
                        else:
                            logger.warning(f"Missing 'key' or 'array_path' in extraction config: {assign_item}")
                            continue
                        
                        if value is not None:
                            extracted[assign_to] = value
            else:
                # Old format: {"from": "response", "key": "id", "assign_to": "user_id"}
                # Also supports: {"from": "response", "record_count": true, "array_path": "users", "assign_to": "userCount"}
                key = extract.get('key')
                assign_to = extract.get('assign_to')
                record_count = extract.get('record_count', False)
                array_path = extract.get('array_path')
                
                if assign_to:
                    if record_count and array_path:
                        # Extract record count
                        value = self.extract_value_single(
                            source_type, source_data, 
                            key=None, assign_to=assign_to, 
                            record_count=record_count, array_path=array_path
                        )
                    elif key:
                        # Extract regular value
                        value = self.extract_value_single(source_type, source_data, key, assign_to)
                    else:
                        logger.warning(f"Missing 'key' or 'array_path' in extraction config: {extract}")
                        continue
                    
                    if value is not None:
                        extracted[assign_to] = value
        
        logger.info(f"Extracted {len(extracted)} variables from batch extraction")
        return extracted
    
    def get_variable(self, var_name: str, default: Any = None) -> Any:
        """
        Get extracted variable from global state.
        
        Args:
            var_name: Variable name to retrieve
            default: Default value if variable not found
        
        Returns:
            Variable value or default
        """
        return self._global_variables.get(var_name, default)
    
    def set_variable(self, var_name: str, value: Any):
        """
        Set variable in global state.
        
        Args:
            var_name: Variable name to set
            value: Value to store
        """
        self._global_variables[var_name] = value
        logger.debug(f"Set global variable '{var_name}' = {value}")
    
    def get_all_variables(self) -> Dict[str, Any]:
        """
        Get all extracted global variables.
        
        Returns:
            Dictionary of all global variables
        """
        return self._global_variables.copy()
    
    def clear_variables(self):
        """
        Clear all extracted global variables.
        Useful for test isolation.
        """
        count = len(self._global_variables)
        self._global_variables.clear()
        logger.info(f"Cleared {count} global variables")
    
    def render_with_context(self, template: Any, context: Dict) -> Any:
        """
        Render template with context variables.
        Delegates to template_utils for actual rendering.
        
        Args:
            template: Template to render (str, dict, list, or primitive)
            context: Context dictionary with variables
        
        Returns:
            Rendered value with variables substituted
        """
        try:
            return render_hybrid(template, context)
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return template


# Singleton accessor function
_context_manager_instance = None

def get_context_manager() -> TestContextManager:
    """
    Get the singleton TestContextManager instance.
    
    Returns:
        TestContextManager singleton instance
    
    Example:
        >>> context_mgr = get_context_manager()
        >>> context = context_mgr.create_context(case, test_data, api_defs)
        >>> context_mgr.extract_values_batch(extract_config, response, db_result)
    """
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = TestContextManager()
    return _context_manager_instance
