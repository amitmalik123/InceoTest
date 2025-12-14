"""
Test Database Manager

Handles database query execution and validation for tests.
Centralizes DB operations including query loading, execution timing,
and comparison validation.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from framework.common.logger import get_logger
from framework.common.template_utils import render_template

logger = get_logger(__name__)


class TestDatabaseManager:
    """
    Manages DB operations in tests including query execution and validation.
    Supports multiple database types and timing control (before/after API calls).
    """
    
    def __init__(self):
        """Initialize database manager"""
        self.db_client_factory = None
        logger.debug("TestDatabaseManager initialized")
    
    def _lazy_load_factory(self):
        """Lazy load DB client factory to avoid circular imports"""
        if self.db_client_factory is None:
            from framework.clients.db_client import DatabaseClientFactory
            self.db_client_factory = DatabaseClientFactory
    
    def should_execute_before(self, case: Dict, protocol: str) -> bool:
        """
        Check if DB query should execute BEFORE API call.
        
        Args:
            case: Test case configuration
            protocol: Protocol type (DB_ONLY always executes before)
        
        Returns:
            True if should execute before API call
        """
        if protocol == 'DB_ONLY':
            return True
        
        db_query_timing = case.get('db_query_timing', 'after_api')
        return db_query_timing == 'before_api' and case.get('db_query')
    
    def should_execute_after(self, case: Dict, protocol: str) -> bool:
        """
        Check if DB query should execute AFTER API call.
        
        Args:
            case: Test case configuration
            protocol: Protocol type
        
        Returns:
            True if should execute after API call
        """
        if protocol == 'DB_ONLY':
            return False
        
        db_query_timing = case.get('db_query_timing', 'after_api')
        return db_query_timing == 'after_api' and case.get('db_query')
    
    def execute_query(self, case: Dict, context: Dict) -> Optional[List[Dict]]:
        """
        Execute DB query with timing control (before/after API).
        
        Args:
            case: Test case configuration with db_query, db_type, db_connection_name
            context: Context dictionary for query rendering
        
        Returns:
            Database query result (list of dicts) or None if query failed
        """
        self._lazy_load_factory()
        
        db_query = case.get('db_query')
        if not db_query:
            logger.debug("No db_query specified, skipping DB execution")
            return None
        
        db_type = case.get('db_type', 'mssql')
        db_connection_name = case.get('db_connection_name')
        
        try:
            # Get database client based on type and connection name
            db_client = self.db_client_factory.get_client(db_type, db_connection_name)
            
            # Load query from file if path provided
            query_content = self.load_query_from_file(db_query, context)
            
            # Render the query with context variables
            rendered_query = render_template(query_content, context)
            
            # Execute query based on database type
            if db_type.lower() in ['mongodb', 'cosmosdb']:
                # For NoSQL databases, parse query as JSON
                query_dict = json.loads(rendered_query) if isinstance(rendered_query, str) else rendered_query
                db_result = db_client.query(query_dict)
            else:
                # For SQL databases, execute as string
                db_result = db_client.query(rendered_query)
            
            logger.info(f"DB query executed on {db_type} ({db_connection_name or 'default'}): "
                       f"{rendered_query[:100]}...")
            logger.debug(f"DB result: {db_result}")
            
            return db_result
            
        except Exception as e:
            logger.error(f"DB query failed on {db_type} ({db_connection_name or 'default'}): {e}")
            return None
    
    def load_query_from_file(self, query: str, context: Dict) -> str:
        """
        Load SQL from file if path provided, otherwise return query as-is.
        
        Args:
            query: Query string or file path
            context: Context dictionary (not used here but kept for consistency)
        
        Returns:
            Query content string
        """
        # Check if query is a file path
        if isinstance(query, str) and (query.endswith('.sql') or '/' in query or '\\' in query):
            query_path = query
            if not os.path.isabs(query_path):
                query_path = os.path.join('testdata', query_path)
            
            if os.path.exists(query_path):
                with open(query_path, 'r', encoding='utf-8') as f:
                    query_content = f.read().strip()
                logger.debug(f"Loaded SQL query from file: {query_path}")
                return query_content
            else:
                logger.warning(f"SQL file not found: {query_path}, using query value as-is")
        
        return query
    
    def perform_comparison_validation(
        self, 
        response: Any, 
        db_result: List[Dict],
        validate_config: Dict,
        context: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Perform DB comparison validation.
        Delegates to validators.perform_db_comparison_validation.
        
        Args:
            response: API response object
            db_result: Database query result
            validate_config: Validation configuration from test case
            context: Context dictionary
        
        Returns:
            Tuple of (is_valid, errors)
        """
        data_cmp_cfg = validate_config.get('data_comparison', {})
        
        if not data_cmp_cfg or not db_result:
            logger.debug("No data_comparison config or db_result, skipping validation")
            return True, []
        
        try:
            from framework.validators.validators import perform_db_comparison_validation
            
            is_valid, errors = perform_db_comparison_validation(
                response, 
                db_result, 
                data_cmp_cfg, 
                context
            )
            
            if is_valid:
                logger.info("DB comparison validation PASSED")
            else:
                logger.error(f"DB comparison validation FAILED: {errors}")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"DB comparison validation error: {e}")
            return False, [str(e)]


# Singleton accessor function
_db_manager_instance = None

def get_db_manager() -> TestDatabaseManager:
    """
    Get the singleton TestDatabaseManager instance.
    
    Returns:
        TestDatabaseManager singleton instance
    
    Example:
        >>> db_mgr = get_db_manager()
        >>> if db_mgr.should_execute_before(case, protocol):
        ...     db_result = db_mgr.execute_query(case, context)
        >>> is_valid, errors = db_mgr.perform_comparison_validation(response, db_result, config, context)
    """
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = TestDatabaseManager()
    return _db_manager_instance
