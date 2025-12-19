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
        has_query = case.get('db_query') or case.get('db_queries')
        return db_query_timing == 'before_api' and has_query
    
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
        has_query = case.get('db_query') or case.get('db_queries')
        return db_query_timing == 'after_api' and has_query
    
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
    
    def execute_queries(self, case: Dict, context: Dict) -> Dict[str, List[Dict]]:
        """
        Execute multiple DB queries if db_queries dict is present, otherwise execute single db_query.
        Supports both new multiple query format and backward compatible single query format.
        
        Args:
            case: Test case configuration with db_query or db_queries
            context: Context dictionary for query rendering
        
        Returns:
            Dictionary mapping query names to their results
            For single query: {'default': result}
            For multiple queries: {'query_name_1': result1, 'query_name_2': result2, ...}
        """
        self._lazy_load_factory()
        
        results = {}
        
        # Check for new multiple queries format
        db_queries = case.get('db_queries')
        if db_queries and isinstance(db_queries, dict):
            # Execute multiple named queries
            db_type = case.get('db_type', 'mssql')
            db_connection_name = case.get('db_connection_name')
            
            logger.info(f"Executing multiple DB queries: {list(db_queries.keys())}")
            
            for query_name, query_content in db_queries.items():
                try:
                    # Get database client
                    db_client = self.db_client_factory.get_client(db_type, db_connection_name)
                    
                    # Load query from file if path provided
                    query_str = self.load_query_from_file(query_content, context)
                    
                    # Render the query with context variables
                    rendered_query = render_template(query_str, context)
                    
                    # Execute query based on database type
                    if db_type.lower() in ['mongodb', 'cosmosdb']:
                        query_dict = json.loads(rendered_query) if isinstance(rendered_query, str) else rendered_query
                        db_result = db_client.query(query_dict)
                    else:
                        db_result = db_client.query(rendered_query)
                    
                    results[query_name] = db_result
                    logger.info(f"DB query '{query_name}' executed successfully, stored as '{query_name}'")
                    logger.debug(f"Query '{query_name}' result: {db_result}")
                    
                except Exception as e:
                    logger.error(f"DB query '{query_name}' failed: {e}")
                    results[query_name] = None
            
            logger.info(f"Returning db_results with queries: {list(results.keys())}")
        
        else:
            # Backward compatibility: execute single db_query
            result = self.execute_query(case, context)
            if result is not None:
                results['default'] = result
                logger.info(f"Single db_query executed, returning as 'default'")
        
        return results if results else None
    
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
        Perform data comparison validation.
        Supports both old single comparison format and new array format.
        Delegates to validators.perform_data_comparison_array for new format,
        and validators.perform_db_comparison_validation for backward compatibility.
        
        Args:
            response: API response object
            db_result: Database query result (for backward compatibility)
            validate_config: Validation configuration from test case
            context: Context dictionary with all data sources
        
        Returns:
            Tuple of (is_valid, errors)
        """
        data_cmp_cfg = validate_config.get('data_comparison')
        
        if not data_cmp_cfg:
            logger.debug("No data_comparison config, skipping validation")
            return True, []
        
        try:
            # Check if new array format or old single dict format
            if isinstance(data_cmp_cfg, list):
                # New array format - supports multiple comparisons with any combination
                from framework.validators.validators import perform_data_comparison_array
                
                is_valid, errors = perform_data_comparison_array(
                    response,
                    context,
                    data_cmp_cfg
                )
                
            else:
                # Old single dict format - backward compatibility
                # Check if db_result is required for this comparison
                target = data_cmp_cfg.get('target', 'db_result')
                
                if target == 'db_result':
                    # For db_result target, check for named query first
                    target_query = data_cmp_cfg.get('target_query', 'default')
                    db_results = context.get('db_results', {})
                    
                    # Try to get the specific query result
                    if target_query != 'default' and target_query in db_results:
                        db_result = db_results[target_query]
                    elif target_query == 'default' and 'default' in db_results:
                        db_result = db_results['default']
                    # else db_result remains as is (could be None or legacy single query result)
                    
                    # Validate that required query exists
                    if not db_result:
                        available_queries = list(db_results.keys()) if db_results else []
                        if available_queries and target_query != 'default':
                            return False, [f"Query '{target_query}' not found in db_results. Available queries: {available_queries}"]
                        elif available_queries and target_query == 'default':
                            return False, [f"Query 'default' not found in db_results. Available queries: {available_queries}. Please specify one using 'target_query'."]
                        else:
                            logger.debug("No db_result available for comparison, skipping validation")
                            return True, []
                
                from framework.validators.validators import perform_db_comparison_validation
                
                is_valid, errors = perform_db_comparison_validation(
                    response, 
                    db_result, 
                    data_cmp_cfg, 
                    context
                )
            
            if is_valid:
                logger.info("Data comparison validation PASSED")
            else:
                logger.error(f"Data comparison validation FAILED: {errors}")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Data comparison validation error: {e}")
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
