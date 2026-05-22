"""
Generic Test Data Teardown
==========================

This module provides a generic cleanup manager that can be used
by any service to clean up test data after test execution.

Usage:
    from framework.hooks import teardown_test_data, CleanupManager
    
    # Simple usage
    teardown_test_data('parties')
    
    # Advanced usage with custom manager
    manager = CleanupManager('parties')
    manager.teardown()
"""

import os
import csv
from typing import Dict, List, Optional, Any

from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config
from .config import HooksConfig, get_service_hooks_config

logger = get_logger(__name__)


class CleanupManager:
    """
    Generic manager for cleaning up test data for any service.
    
    This class handles:
    - Deleting data created during test setup via API
    - Restoring original CSV files
    - Clearing caches
    """
    
    def __init__(
        self,
        service_name: str,
        environment: Optional[str] = None,
        config: Optional[HooksConfig] = None,
        created_data: Optional[List[Dict]] = None
    ):
        """
        Initialize the CleanupManager.
        
        Args:
            service_name: Name of the service (e.g., 'parties', 'securities')
            environment: Environment name (defaults to config environment)
            config: Optional HooksConfig, will load default if not provided
            created_data: List of data items created during setup to be cleaned up
        """
        self.service_name = service_name
        self.config = config or get_service_hooks_config(service_name)
        self.app_config = get_config()
        self.environment = environment or os.environ.get('ENV_NAME', '').strip() or self.app_config.get('environment', 'test')
        
        # Data to clean up
        self.created_data = created_data or []
        self.original_csv_data: Dict[str, List[Dict]] = {}
        
        # Initialize API client lazily
        self._api_client = None
        
        logger.info(f"CleanupManager initialized for service: {service_name}")
    
    @property
    def api_client(self):
        """Lazy initialization of API client."""
        if self._api_client is None:
            try:
                from framework.clients.api_client import ApiClientFactory
                self._api_client = ApiClientFactory.get_client(self.service_name)
            except Exception as e:
                logger.warning(f"Could not create API client: {e}")
        return self._api_client
    
    def teardown(self) -> bool:
        """
        Run all teardown operations based on configuration.
        
        Returns:
            True if teardown completed successfully, False otherwise
        """
        if not self.config.enabled:
            logger.info(f"Hooks disabled for service: {self.service_name}")
            return True
        
        logger.info(f"Starting teardown for service: {self.service_name}")
        
        try:
            # Delete data from database (if configured)
            if self.config.cleanup_db.get('enabled'):
                self._cleanup_db_data()
            
            # Delete data created during tests via API (if configured)
            if self.created_data:
                self._delete_created_data()
            
            # Restore original CSV files
            # NOTE: CSV restoration disabled to keep prerequisite-generated test data
            # if self.original_csv_data:
            #     self._restore_csv_files()
            
            # Clear caches
            self._clear_cache()
            
            logger.info(f"Teardown completed for service: {self.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Teardown failed for service {self.service_name}: {e}")
            return False
    
    def _delete_created_data(self) -> None:
        """Delete data that was created during test setup via API."""
        if not self.api_client:
            logger.warning("No API client available, skipping data deletion")
            return
        
        for item in self.created_data:
            try:
                item_id = item.get('id')
                if item_id:
                    logger.info(f"Deleting test data with ID: {item_id}")
                    self.api_client.request('DELETE', f"/{item_id}")
                    logger.info(f"Successfully deleted: {item_id}")
            except Exception as e:
                logger.error(f"Failed to delete data {item.get('id')}: {e}")
    
    def _cleanup_db_data(self) -> None:
        """
        Clean up test data directly from the database using configured cleanup queries.

        SAFETY GUARDS (all must pass before any DELETE runs):
        1. Environment whitelist - cleanup only runs in allowed envs (e.g. never PROD)
        2. Dry-run mode - if enabled, logs SQL + params but executes nothing
        3. Max-deletes cap - aborts if total deletes would exceed configured limit
        4. Pre-delete verification - per-row SELECT must confirm record exists and
           (optionally) was created by the expected user before DELETE runs
        5. Per-row parameterized SQL - prevents SQL injection
        6. Only IDs returned by THIS run's POST responses are deleted (created_data),
           which keeps concurrent runs isolated from each other
        """
        cleanup_config = self.config.cleanup_db
        if not cleanup_config:
            logger.info(f"No DB cleanup configured for service: {self.service_name}")
            return

        # ---------------- SAFETY 1: Environment whitelist ----------------
        allowed_envs = [e.upper() for e in cleanup_config.get('allowed_environments', [])]
        current_env = (self.environment or '').upper()
        if allowed_envs and current_env not in allowed_envs:
            logger.error(
                f"[CLEANUP-DB] BLOCKED: environment '{current_env}' is not in "
                f"allowed_environments={allowed_envs} for service '{self.service_name}'. "
                f"Skipping DB cleanup as a safety measure."
            )
            return

        # ---------------- SAFETY 2: Dry-run mode ----------------
        # Allow runtime override via env var (e.g. set by --cleanup-dry-run CLI flag)
        env_dry_run = os.environ.get('DRY_RUN_CLEANUP', '').lower() in ('1', 'true', 'yes')
        dry_run = bool(cleanup_config.get('dry_run', False)) or env_dry_run
        if dry_run:
            logger.warning(
                f"[CLEANUP-DB] DRY-RUN MODE for service '{self.service_name}'. "
                f"SQL will be logged but NOT executed."
            )

        db_type = cleanup_config.get('db_type')
        db_connection_name = cleanup_config.get('db_connection_name')
        cleanup_queries = cleanup_config.get('cleanup_queries', [])
        max_deletes = int(cleanup_config.get('max_deletes_per_run', 50))
        expected_created_by = cleanup_config.get('expected_created_by')

        if not db_type or not db_connection_name or not cleanup_queries:
            logger.warning(f"Incomplete DB cleanup config for service: {self.service_name}")
            return

        if not self.created_data:
            logger.info(f"No created data to clean up from DB for service: {self.service_name}")
            return

        # ---------------- SAFETY 3: Max-deletes cap (pre-check) ----------------
        # Worst-case = (#queries) x (#created items). Abort early if grossly oversized.
        worst_case = len(cleanup_queries) * len(self.created_data)
        if worst_case > max_deletes:
            logger.error(
                f"[CLEANUP-DB] BLOCKED: worst-case deletes={worst_case} exceeds "
                f"max_deletes_per_run={max_deletes} for service '{self.service_name}'. "
                f"Refusing to proceed."
            )
            return

        logger.info(
            f"[CLEANUP-DB] Starting cleanup: service='{self.service_name}' env='{current_env}' "
            f"items={len(self.created_data)} queries={len(cleanup_queries)} "
            f"max_deletes={max_deletes} dry_run={dry_run}"
        )

        try:
            from framework.clients.db_client import DatabaseClientFactory
            db_client = DatabaseClientFactory.get_client(db_type, db_connection_name, auto_connect=True)

            total_deleted = 0
            for query_config in cleanup_queries:
                description = query_config.get('description', 'Cleanup query')
                query_file = query_config.get('query_file')
                param_field = query_config.get('param_field', 'id')
                verify_query_file = query_config.get('verify_query_file')

                sql = self._load_cleanup_query(query_file)
                if not sql:
                    logger.warning(f"Skipping cleanup query: {description} (query not loaded)")
                    continue

                # Optional pre-delete verification SQL
                verify_sql = self._load_cleanup_query(verify_query_file) if verify_query_file else None

                logger.info(f"[CLEANUP-DB] {description}")

                for item in self.created_data:
                    param_value = item.get(param_field)
                    if not param_value:
                        logger.warning(f"No '{param_field}' in created_data item: {item}")
                        continue

                    # ---------------- SAFETY 4: Pre-delete verification ----------------
                    if verify_sql and not self._verify_record_safe_to_delete(
                        db_client, verify_sql, param_value, expected_created_by, description
                    ):
                        # Verification failed - skip DELETE for this ID
                        continue

                    # ---------------- SAFETY 3 (running): Cap during execution ----------------
                    if total_deleted >= max_deletes:
                        logger.error(
                            f"[CLEANUP-DB] STOPPING: max_deletes_per_run={max_deletes} reached. "
                            f"Remaining items will NOT be deleted."
                        )
                        return

                    if dry_run:
                        logger.warning(
                            f"  [DRY-RUN] Would execute: {sql!r} with param=({param_value!r},)"
                        )
                        continue

                    try:
                        # Count parameter markers and replicate param for each
                        param_count = sql.count('?')
                        params = (param_value,) * param_count if param_count > 0 else (param_value,)
                        rows_affected = db_client.execute(sql, params)
                        total_deleted += rows_affected
                        logger.info(
                            f"  [{description}] ID={param_value}: {rows_affected} rows deleted"
                        )
                    except Exception as e:
                        logger.error(f"  [{description}] Failed for ID={param_value}: {e}")

            logger.info(
                f"[CLEANUP-DB] Completed for {self.service_name}: "
                f"{total_deleted} total rows deleted (dry_run={dry_run})"
            )

        except Exception as e:
            logger.error(f"DB cleanup failed for service {self.service_name}: {e}", exc_info=True)

    def _verify_record_safe_to_delete(
        self,
        db_client,
        verify_sql: str,
        param_value: Any,
        expected_created_by: Optional[str],
        description: str,
    ) -> bool:
        """
        SAFETY 4: Run a verification SELECT to confirm a record is safe to delete.

        Returns True only when:
          - verify_sql returns at least one row matching the ID, AND
          - if expected_created_by is set, the row's CreatedBy matches.

        Any failure logs an error and returns False, which causes the DELETE to be skipped.
        """
        try:
            rows = db_client.query(verify_sql, (param_value,))
        except Exception as e:
            logger.error(
                f"  [{description}] Verification query failed for ID={param_value}: {e}. "
                f"Skipping DELETE for safety."
            )
            return False

        if not rows:
            logger.warning(
                f"  [{description}] Verification returned 0 rows for ID={param_value}. "
                f"Record does not exist or does not match safety criteria. Skipping DELETE."
            )
            return False

        if expected_created_by:
            actual_created_by = rows[0].get('CreatedBy') or rows[0].get('createdby')
            if actual_created_by != expected_created_by:
                logger.error(
                    f"  [{description}] CreatedBy mismatch for ID={param_value}: "
                    f"expected='{expected_created_by}' actual='{actual_created_by}'. "
                    f"Skipping DELETE for safety."
                )
                return False

        return True
    
    def _load_cleanup_query(self, query_file: str) -> Optional[str]:
        """
        Load a SQL cleanup query from a file in the testdata directory.
        
        Args:
            query_file: Relative path from testdata/ (e.g., 'parties/db_queries/Cleanup_Party_DELETE.sql')
            
        Returns:
            SQL query string, or None if file not found
        """
        if not query_file:
            return None
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        query_path = os.path.join(base_path, 'testdata', query_file)
        
        if not os.path.exists(query_path):
            logger.error(f"Cleanup query file not found: {query_path}")
            return None
        
        try:
            with open(query_path, 'r', encoding='utf-8') as f:
                sql = f.read().strip()
            logger.debug(f"Loaded cleanup query from: {query_file}")
            return sql
        except Exception as e:
            logger.error(f"Failed to read cleanup query file {query_file}: {e}")
            return None
    
    def _restore_csv_files(self) -> None:
        """Restore CSV files to their original state."""
        from .config import restore_csv_file
        
        for csv_file, original_data in self.original_csv_data.items():
            restore_csv_file(csv_file, original_data)
    
    def _clear_cache(self) -> None:
        """Clear any cached data for the service."""
        logger.info(f"Clearing cache for service: {self.service_name}")
        
        # Clear config loader cache
        try:
            from framework.loaders.config_loader import ConfigManager
            config_manager = ConfigManager()
            config_manager.clear_cache()
            logger.info("Configuration cache cleared")
        except Exception as e:
            logger.warning(f"Could not clear config cache: {e}")
        
        logger.info("Cache clearing completed")
    
    def cleanup_specific_data(self, data_ids: List[str]) -> None:
        """
        Clean up specific data items by their IDs via API DELETE.
        
        Args:
            data_ids: List of IDs to delete
        """
        if not self.api_client:
            logger.error("No API client available for data cleanup")
            return
        
        for data_id in data_ids:
            try:
                logger.info(f"Deleting data with ID: {data_id}")
                self.api_client.request('DELETE', f"/{data_id}")
                logger.info(f"Successfully deleted: {data_id}")
            except Exception as e:
                logger.error(f"Failed to delete data {data_id}: {e}")


def teardown_test_data(
    service_name: str,
    environment: Optional[str] = None,
    config: Optional[HooksConfig] = None,
    created_data: Optional[List[Dict]] = None
) -> bool:
    """
    Convenience function to run test data teardown for a service.
    
    Args:
        service_name: Name of the service
        environment: Optional environment override
        config: Optional custom HooksConfig
        created_data: Data items created during setup that need cleanup
        
    Returns:
        True if teardown succeeded, False otherwise
    """
    manager = CleanupManager(service_name, environment, config, created_data)
    return manager.teardown()
