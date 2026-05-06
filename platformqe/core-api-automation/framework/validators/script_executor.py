"""
Script Executor Module

Dynamically loads and executes custom validator scripts from test case configuration.
Provides full test context to scripts and captures results for use in extract_values,
data_comparison, and assertions.

Usage in test case JSON:
    "scripts": "analyticsApiServices\\validators\\ewma_validator.py"
    
The script should implement either:
1. A 'validate' function that accepts test context
2. A 'run' function that accepts test context  
3. A class with 'validate' or 'run' method

The script receives a ScriptContext object with:
- test_case: Full test case configuration
- request: Request details (endpoint, method, headers, payload)
- response: API response object and data
- db_results: Database query results
- extracted_vars: Previously extracted variables
- config: Framework configuration
"""

import os
import sys
import importlib.util
import traceback
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

from framework.common.logger import get_logger
from framework.common.utils import normalize_path

logger = get_logger(__name__)


@dataclass
class ScriptExecutionLog:
    """
    Structured log entry for script execution.
    Captures all details for debugging and audit purposes.
    """
    script_path: str = ""
    resolved_path: str = ""
    test_id: str = ""
    test_name: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_ms: float = 0.0
    status: str = ""  # "success", "failed", "error"
    validator_function: str = ""
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    exception: Optional[str] = None
    traceback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_log_string(self, verbose: bool = False) -> str:
        """Format as readable log string."""
        lines = [
            f"{'='*60}",
            f"SCRIPT EXECUTION LOG",
            f"{'='*60}",
            f"Script: {self.script_path}",
            f"Resolved Path: {self.resolved_path}",
            f"Test ID: {self.test_id}",
            f"Test Name: {self.test_name}",
            f"Start Time: {self.start_time}",
            f"End Time: {self.end_time}",
            f"Duration: {self.duration_ms:.2f} ms",
            f"Status: {self.status.upper()}",
            f"Validator Function: {self.validator_function}",
        ]
        
        if verbose:
            lines.append(f"Input Summary: {json.dumps(self.input_summary, indent=2, default=str)}")
            lines.append(f"Output Summary: {json.dumps(self.output_summary, indent=2, default=str)}")
        
        if self.errors:
            lines.append(f"Errors: {self.errors}")
        
        if self.exception:
            lines.append(f"Exception: {self.exception}")
            if verbose and self.traceback:
                lines.append(f"Traceback:\n{self.traceback}")
        
        lines.append(f"{'='*60}")
        return "\n".join(lines)


@dataclass
class RequestContext:
    """Request details passed to scripts."""
    endpoint: str = ""
    method: str = ""
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Any = None
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class ResponseContext:
    """Response details passed to scripts."""
    status_code: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    text: str = ""
    response_time_ms: int = 0
    raw_response: Any = None  # Original response object if needed


@dataclass
class ScriptContext:
    """
    Full context passed to custom validator scripts.
    
    Contains all information needed for custom validation logic:
    - test_case: Complete test case configuration
    - request: Request details
    - response: Response data
    - db_results: Database query results (list for single query, dict for named queries)
    - extracted_vars: Variables extracted from previous operations
    - config: Framework configuration
    """
    test_case: Dict[str, Any] = field(default_factory=dict)
    request: RequestContext = field(default_factory=RequestContext)
    response: ResponseContext = field(default_factory=ResponseContext)
    db_results: Any = field(default_factory=list)  # List[Dict] or Dict[str, List[Dict]] for named queries
    extracted_vars: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for scripts that prefer dict access."""
        return {
            "test_case": self.test_case,
            "request": {
                "endpoint": self.request.endpoint,
                "method": self.request.method,
                "url": self.request.url,
                "headers": self.request.headers,
                "payload": self.request.payload,
                "query_params": self.request.query_params
            },
            "response": {
                "status_code": self.response.status_code,
                "headers": self.response.headers,
                "body": self.response.body,
                "text": self.response.text,
                "response_time_ms": self.response.response_time_ms
            },
            "db_results": self.db_results,
            "extracted_vars": self.extracted_vars,
            "config": self.config
        }


@dataclass
class ScriptResult:
    """
    Result returned from script execution.
    
    Attributes:
        success: Whether validation passed
        errors: List of error messages
        extracted_values: Dict of values to be available for extract_values
        computed_values: Dict of computed values (e.g., expected values)
        comparison_data: Data for data_comparison validation
        metadata: Additional metadata from script
    """
    success: bool = True
    errors: List[str] = field(default_factory=list)
    extracted_values: Dict[str, Any] = field(default_factory=dict)
    computed_values: Dict[str, Any] = field(default_factory=dict)
    comparison_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "errors": self.errors,
            "extracted_values": self.extracted_values,
            "computed_values": self.computed_values,
            "comparison_data": self.comparison_data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptResult":
        """Create ScriptResult from dictionary (for scripts returning dict)."""
        return cls(
            success=data.get("success", True),
            errors=data.get("errors", []),
            extracted_values=data.get("extracted_values", {}),
            computed_values=data.get("computed_values", {}),
            comparison_data=data.get("comparison_data", {}),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_tuple(cls, data: Tuple) -> "ScriptResult":
        """
        Create ScriptResult from tuple format.
        Supports: (success, errors, computed_values) tuple from existing validators.
        """
        if len(data) >= 3:
            return cls(
                success=data[0],
                errors=data[1] if isinstance(data[1], list) else [data[1]] if data[1] else [],
                computed_values=data[2] if isinstance(data[2], dict) else {}
            )
        elif len(data) == 2:
            return cls(
                success=data[0],
                errors=data[1] if isinstance(data[1], list) else [data[1]] if data[1] else []
            )
        elif len(data) == 1:
            return cls(success=data[0])
        return cls()


class ScriptExecutor:
    """
    Executes custom validator scripts with full test context.
    
    Loads Python scripts dynamically and invokes their validation logic,
    passing the complete test context and capturing results.
    
    Security Features:
    - Script path validation to prevent path traversal attacks
    - Allowed directory enforcement (scripts must be within BASE_PATHS)
    - File extension validation (only .py files allowed)
    - Symbolic link resolution to prevent escape attacks
    """
    
    # Base paths to search for scripts (also used as security boundaries)
    BASE_PATHS = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'testdata'),  # testdata folder
        os.path.join(os.path.dirname(__file__), '..', '..'),  # project root
        os.path.join(os.path.dirname(__file__), '..'),  # framework folder
    ]
    
    # Allowed file extensions for scripts
    ALLOWED_EXTENSIONS = {'.py'}
    
    # Blocked path patterns (security)
    BLOCKED_PATTERNS = {'..', '~', '$'}
    
    # Default cache TTL in seconds (0 = no expiration)
    DEFAULT_CACHE_TTL = 0
    
    def __init__(
        self, 
        additional_paths: List[str] = None, 
        enable_detailed_logging: bool = True,
        strict_security: bool = True,
        cache_ttl: int = 0,
        auto_reload_on_change: bool = True
    ):
        """
        Initialize script executor.
        
        Args:
            additional_paths: Additional paths to search for scripts
            enable_detailed_logging: Whether to log detailed execution info
            strict_security: If True, enforce strict path validation (recommended)
            cache_ttl: Cache time-to-live in seconds (0 = no expiration)
            auto_reload_on_change: If True, reload script if file modified since cache
        """
        self.search_paths = self.BASE_PATHS.copy()
        if additional_paths:
            self.search_paths.extend(additional_paths)
        
        # Normalize and resolve all search paths for security comparison
        self._allowed_paths = [os.path.realpath(os.path.normpath(p)) for p in self.search_paths]
        
        # Security settings
        self.strict_security = strict_security
        
        # Cache settings
        self.cache_ttl = cache_ttl
        self.auto_reload_on_change = auto_reload_on_change
        
        # Cache for loaded modules: {path: (module, mtime, load_time)}
        self._module_cache: Dict[str, Tuple[Any, float, float]] = {}
        
        # Execution logging
        self.enable_detailed_logging = enable_detailed_logging
        self.execution_logs: List[ScriptExecutionLog] = []
        self._current_log: Optional[ScriptExecutionLog] = None
        
        logger.debug(f"ScriptExecutor initialized with search paths: {self.search_paths}")
        logger.debug(f"Detailed logging: {'enabled' if enable_detailed_logging else 'disabled'}")
        logger.debug(f"Cache TTL: {cache_ttl}s, Auto-reload on change: {auto_reload_on_change}")
    
    def _start_execution_log(self, script_path: str, context: 'ScriptContext') -> ScriptExecutionLog:
        """Start a new execution log entry."""
        log_entry = ScriptExecutionLog(
            script_path=script_path,
            test_id=context.test_case.get('test_id', 'N/A'),
            test_name=context.test_case.get('test_name', 'N/A'),
            start_time=datetime.now().isoformat(),
            input_summary={
                "endpoint": context.request.endpoint,
                "method": context.request.method,
                "has_payload": context.request.payload is not None,
                "response_status": context.response.status_code,
                "db_results_count": len(context.db_results),
                "extracted_vars_count": len(context.extracted_vars)
            }
        )
        self._current_log = log_entry
        return log_entry
    
    def _end_execution_log(
        self, 
        log_entry: ScriptExecutionLog,
        result: 'ScriptResult',
        resolved_path: str = "",
        validator_func_name: str = "",
        exception: Exception = None
    ) -> None:
        """Complete and save execution log entry."""
        log_entry.end_time = datetime.now().isoformat()
        log_entry.resolved_path = resolved_path
        log_entry.validator_function = validator_func_name
        
        # Calculate duration
        try:
            start = datetime.fromisoformat(log_entry.start_time)
            end = datetime.fromisoformat(log_entry.end_time)
            log_entry.duration_ms = (end - start).total_seconds() * 1000
        except Exception:
            log_entry.duration_ms = 0.0
        
        # Set status and output
        if exception:
            log_entry.status = "error"
            log_entry.exception = str(exception)
            log_entry.traceback = traceback.format_exc()
        elif result.success:
            log_entry.status = "success"
        else:
            log_entry.status = "failed"
        
        log_entry.errors = result.errors
        log_entry.output_summary = {
            "success": result.success,
            "error_count": len(result.errors),
            "extracted_values_count": len(result.extracted_values),
            "computed_values_count": len(result.computed_values),
            "extracted_keys": list(result.extracted_values.keys()),
            "computed_keys": list(result.computed_values.keys())
        }
        
        # Store log entry
        self.execution_logs.append(log_entry)
        self._current_log = None
        
        # Log to framework logger
        self._log_execution(log_entry)
    
    def _log_execution(self, log_entry: ScriptExecutionLog) -> None:
        """Output execution log to framework logger."""
        if log_entry.status == "success":
            logger.info(
                f"[PASS] Script executed successfully: {log_entry.script_path} "
                f"[{log_entry.duration_ms:.2f}ms] "
                f"(extracted: {log_entry.output_summary.get('extracted_values_count', 0)}, "
                f"computed: {log_entry.output_summary.get('computed_values_count', 0)})"
            )
        elif log_entry.status == "failed":
            logger.warning(
                f"[FAIL] Script validation failed: {log_entry.script_path} "
                f"[{log_entry.duration_ms:.2f}ms] "
                f"Errors: {log_entry.errors}"
            )
        else:  # error
            logger.error(
                f"[ERROR] Script execution error: {log_entry.script_path} "
                f"Exception: {log_entry.exception}"
            )
        
        if self.enable_detailed_logging:
            logger.debug(log_entry.to_log_string(verbose=True))
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all script executions."""
        total = len(self.execution_logs)
        successful = sum(1 for log in self.execution_logs if log.status == "success")
        failed = sum(1 for log in self.execution_logs if log.status == "failed")
        errors = sum(1 for log in self.execution_logs if log.status == "error")
        total_duration = sum(log.duration_ms for log in self.execution_logs)
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "errors": errors,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / total if total > 0 else 0,
            "scripts_executed": [log.script_path for log in self.execution_logs]
        }
    
    def get_execution_logs(self) -> List[Dict[str, Any]]:
        """Get all execution logs as dictionaries."""
        return [log.to_dict() for log in self.execution_logs]
    
    def clear_logs(self) -> None:
        """Clear execution logs."""
        self.execution_logs.clear()
    
    # =========================================================================
    # SECURITY VALIDATION METHODS
    # =========================================================================
    
    def _validate_path_security(self, script_path: str) -> Tuple[bool, str]:
        """
        Validate script path for security issues.
        
        Checks for:
        1. Blocked patterns (path traversal attempts)
        2. Valid file extension
        3. Path is within allowed directories
        4. Symbolic link resolution doesn't escape boundaries
        
        Args:
            script_path: Raw script path from test case
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for blocked patterns (path traversal attempts)
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in script_path:
                return False, f"Security violation: blocked pattern '{pattern}' in path: {script_path}"
        
        return True, ""
    
    def _validate_resolved_path(self, resolved_path: str) -> Tuple[bool, str]:
        """
        Validate that resolved path is within allowed directories.
        
        Args:
            resolved_path: Absolute resolved path to script
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not resolved_path:
            return False, "Resolved path is empty"
        
        # Validate file extension
        ext = os.path.splitext(resolved_path)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Security violation: file extension '{ext}' not allowed. Allowed: {self.ALLOWED_EXTENSIONS}"
        
        # Resolve to real path (follows symlinks)
        try:
            real_path = os.path.realpath(resolved_path)
        except Exception as e:
            return False, f"Security violation: cannot resolve real path: {e}"
        
        # Check if path is within allowed directories
        is_within_allowed = False
        for allowed_path in self._allowed_paths:
            try:
                # Use os.path.commonpath for robust comparison
                if real_path.startswith(allowed_path + os.sep) or real_path == allowed_path:
                    is_within_allowed = True
                    break
            except ValueError:
                # Different drives on Windows
                continue
        
        if not is_within_allowed:
            return False, (
                f"Security violation: script path '{resolved_path}' is outside allowed directories. "
                f"Allowed: {self._allowed_paths}"
            )
        
        # Verify file exists and is a file (not directory)
        if not os.path.isfile(real_path):
            return False, f"Security violation: path is not a file: {resolved_path}"
        
        logger.debug(f"Security validation passed for: {resolved_path}")
        return True, ""
    
    def validate_script_path(self, script_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Full security validation of script path.
        
        Public method for pre-flight validation of scripts.
        
        Args:
            script_path: Script path from test case
            
        Returns:
            Tuple of (is_valid, error_message, resolved_path)
        """
        # Step 1: Validate raw path
        is_valid, error = self._validate_path_security(script_path)
        if not is_valid:
            logger.error(f"[SECURITY] {error}")
            return False, error, None
        
        # Step 2: Resolve path
        resolved_path = self._resolve_path_unsecured(script_path)
        if not resolved_path:
            return False, f"Script not found: {script_path}", None
        
        # Step 3: Validate resolved path
        is_valid, error = self._validate_resolved_path(resolved_path)
        if not is_valid:
            logger.error(f"[SECURITY] {error}")
            return False, error, None
        
        return True, "", resolved_path
    
    def _resolve_path_unsecured(self, script_path: str) -> Optional[str]:
        """
        Resolve script path without security checks (internal use only).
        
        Args:
            script_path: Script path from test case
            
        Returns:
            Resolved absolute path or None
        """
        # Normalize path separators
        script_path = normalize_path(script_path)
        
        # Check if already absolute
        if os.path.isabs(script_path) and os.path.exists(script_path):
            return script_path
        
        # Search in base paths
        for base_path in self.search_paths:
            full_path = os.path.normpath(os.path.join(base_path, script_path))
            if os.path.exists(full_path):
                return full_path
        
        return None
    
    # =========================================================================
    # PATH RESOLUTION
    # =========================================================================

    def resolve_script_path(self, script_path: str) -> Optional[str]:
        """
        Resolve script path to absolute path with security validation.
        
        Searches in order:
        1. Absolute path (if provided)
        2. Relative to testdata folder
        3. Relative to project root
        4. Relative to framework folder
        
        Security checks:
        - Validates path doesn't contain traversal patterns
        - Ensures resolved path is within allowed directories
        - Validates file extension is .py
        
        Args:
            script_path: Script path from test case (can be relative)
        
        Returns:
            Absolute path to script or None if not found or security check fails
        """
        if self.strict_security:
            # Use full security validation
            is_valid, error, resolved = self.validate_script_path(script_path)
            if not is_valid:
                logger.warning(f"Script path rejected: {error}")
                return None
            logger.debug(f"Resolved script path (secure): {script_path} -> {resolved}")
            return resolved
        else:
            # Legacy mode without strict security (not recommended)
            logger.warning("[SECURITY] Running in non-strict mode - path validation disabled")
            return self._resolve_path_unsecured(script_path)
    
    def load_module(self, script_path: str) -> Optional[Any]:
        """
        Load Python module from script path with smart caching.
        
        Cache invalidation triggers:
        1. File modified since last load (if auto_reload_on_change=True)
        2. Cache entry expired (if cache_ttl > 0)
        3. Manual invalidation via reload_script() or clear_module_cache()
        
        Args:
            script_path: Absolute path to Python script
        
        Returns:
            Loaded module or None if loading failed
        """
        current_time = time.time()
        
        # Check cache
        if script_path in self._module_cache:
            cached_module, cached_mtime, load_time = self._module_cache[script_path]
            
            # Check TTL expiration
            if self.cache_ttl > 0 and (current_time - load_time) > self.cache_ttl:
                logger.debug(f"Cache expired for: {script_path} (TTL: {self.cache_ttl}s)")
                self._invalidate_cache_entry(script_path)
            # Check file modification
            elif self.auto_reload_on_change:
                try:
                    current_mtime = os.path.getmtime(script_path)
                    if current_mtime > cached_mtime:
                        logger.info(f"Script modified, reloading: {script_path}")
                        self._invalidate_cache_entry(script_path)
                    else:
                        # Cache hit - return cached module
                        logger.debug(f"Cache hit for: {script_path}")
                        return cached_module
                except OSError:
                    # File might have been deleted
                    self._invalidate_cache_entry(script_path)
            else:
                # No auto-reload, return cached module
                return cached_module
        
        # Load fresh module
        try:
            # Get file modification time
            try:
                file_mtime = os.path.getmtime(script_path)
            except OSError:
                file_mtime = current_time
            
            # Generate unique module name
            module_name = Path(script_path).stem + "_" + str(hash(script_path))[-8:]
            
            # Load module spec
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load module spec for: {script_path}")
                return None
            
            # Create and execute module
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to allow imports within the script
            sys.modules[module_name] = module
            
            # Execute module
            spec.loader.exec_module(module)
            
            # Cache module with metadata: (module, mtime, load_time)
            self._module_cache[script_path] = (module, file_mtime, current_time)
            
            logger.info(f"Loaded script module: {script_path}")
            return module
            
        except Exception as e:
            logger.error(f"Failed to load script module {script_path}: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    # =========================================================================
    # CACHE MANAGEMENT METHODS
    # =========================================================================
    
    def _invalidate_cache_entry(self, script_path: str) -> None:
        """
        Invalidate a single cache entry and clean up sys.modules.
        
        Args:
            script_path: Path to the cached script
        """
        if script_path in self._module_cache:
            cached_module, _, _ = self._module_cache[script_path]
            
            # Remove from sys.modules to allow fresh import
            module_name = getattr(cached_module, '__name__', None)
            if module_name and module_name in sys.modules:
                del sys.modules[module_name]
            
            del self._module_cache[script_path]
            logger.debug(f"Cache invalidated for: {script_path}")
    
    def reload_script(self, script_path: str) -> Optional[Any]:
        """
        Force reload of a specific script.
        
        Invalidates cache and loads fresh module.
        
        Args:
            script_path: Path to script (relative or absolute)
            
        Returns:
            Freshly loaded module or None if loading failed
        """
        resolved_path = self.resolve_script_path(script_path)
        if resolved_path:
            self._invalidate_cache_entry(resolved_path)
            logger.info(f"Force reloading script: {script_path}")
            return self.load_module(resolved_path)
        return None
    
    def clear_module_cache(self) -> int:
        """
        Clear all cached modules.
        
        Useful for long-running processes or when scripts are updated.
        
        Returns:
            Number of cache entries cleared
        """
        count = len(self._module_cache)
        
        # Clean up sys.modules references
        for script_path in list(self._module_cache.keys()):
            self._invalidate_cache_entry(script_path)
        
        logger.info(f"Module cache cleared: {count} entries removed")
        return count
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache statistics and details.
        
        Returns:
            Dict with cache statistics
        """
        current_time = time.time()
        entries = []
        
        for path, (module, mtime, load_time) in self._module_cache.items():
            age_seconds = current_time - load_time
            try:
                current_mtime = os.path.getmtime(path)
                is_stale = current_mtime > mtime
            except OSError:
                is_stale = True
            
            entries.append({
                "path": path,
                "module_name": getattr(module, '__name__', 'unknown'),
                "age_seconds": round(age_seconds, 2),
                "is_stale": is_stale,
                "ttl_remaining": max(0, self.cache_ttl - age_seconds) if self.cache_ttl > 0 else None
            })
        
        return {
            "total_entries": len(self._module_cache),
            "cache_ttl": self.cache_ttl,
            "auto_reload_on_change": self.auto_reload_on_change,
            "entries": entries
        }
    
    def is_script_cached(self, script_path: str) -> bool:
        """
        Check if a script is currently cached.
        
        Args:
            script_path: Path to script (relative or absolute)
            
        Returns:
            True if script is in cache
        """
        resolved_path = self.resolve_script_path(script_path)
        return resolved_path in self._module_cache if resolved_path else False

    def find_validator_function(self, module: Any) -> Optional[Callable]:
        """
        Find the validation function in the loaded module.
        
        Searches for (in order):
        1. 'validate' function
        2. 'run' function
        3. 'validate_analytics_calculation' function (legacy support)
        4. Class with 'validate' or 'run' method
        
        Args:
            module: Loaded Python module
        
        Returns:
            Callable validator function or None
        """
        # Check for standalone functions
        for func_name in ['validate', 'run', 'validate_analytics_calculation', 'execute']:
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                if callable(func):
                    logger.debug(f"Found validator function: {func_name}")
                    return func
        
        # Check for validator classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name.endswith('Validator'):
                # Instantiate the class
                try:
                    instance = attr()
                    for method_name in ['validate', 'run', 'validate_api_response']:
                        if hasattr(instance, method_name):
                            method = getattr(instance, method_name)
                            if callable(method):
                                logger.debug(f"Found validator class method: {attr_name}.{method_name}")
                                return method
                except Exception as e:
                    logger.debug(f"Could not instantiate {attr_name}: {e}")
        
        return None
    
    def build_context(
        self,
        test_case: Dict[str, Any],
        response: Any = None,
        db_results: List[Dict] = None,
        extracted_vars: Dict = None,
        config: Dict = None
    ) -> ScriptContext:
        """
        Build ScriptContext from test execution data.
        
        Args:
            test_case: Test case configuration
            response: API response object
            db_results: Database query results
            extracted_vars: Previously extracted variables
            config: Framework configuration
        
        Returns:
            ScriptContext with all test data
        """
        # Get the actual parsed payload from extracted_vars (api_request) or fall back to test_case
        # extracted_vars['api_request'] contains the rendered/parsed payload from PayloadManager
        actual_payload = None
        if extracted_vars and 'api_request' in extracted_vars:
            actual_payload = extracted_vars['api_request']
        if actual_payload is None:
            # Fall back to test_case payload (might be file path for external payloads)
            actual_payload = test_case.get('payload')
        
        # Build request context
        request_ctx = RequestContext(
            endpoint=test_case.get('endpoint', ''),
            method=test_case.get('method', ''),
            url=test_case.get('mainURL', ''),
            headers=test_case.get('headers_additional', {}),
            payload=actual_payload,
            query_params=test_case.get('query_params', {})
        )
        
        # Build response context
        response_ctx = ResponseContext()
        if response is not None:
            try:
                response_ctx.status_code = getattr(response, 'status_code', 0)
                response_ctx.headers = dict(getattr(response, 'headers', {}))
                response_ctx.text = getattr(response, 'text', '')
                response_ctx.raw_response = response
                
                # Try to get JSON body
                try:
                    response_ctx.body = response.json()
                except Exception:
                    response_ctx.body = response_ctx.text
                    
            except Exception as e:
                logger.warning(f"Error extracting response context: {e}")
        
        return ScriptContext(
            test_case=test_case,
            request=request_ctx,
            response=response_ctx,
            db_results=db_results or [],
            extracted_vars=extracted_vars or {},
            config=config or {}
        )
    
    def execute_script(
        self,
        script_path: str,
        context: ScriptContext
    ) -> ScriptResult:
        """
        Execute a validator script with the provided context.
        
        Args:
            script_path: Path to script (relative or absolute)
            context: ScriptContext with test data
        
        Returns:
            ScriptResult with validation results and extracted values
        """
        # Start execution logging
        log_entry = self._start_execution_log(script_path, context)
        resolved_path = ""
        validator_func_name = ""
        
        logger.info(f"[START] Script execution: {script_path}")
        logger.debug(f"   Test ID: {context.test_case.get('test_id', 'N/A')}")
        logger.debug(f"   Test Name: {context.test_case.get('test_name', 'N/A')}")
        
        # Resolve script path
        resolved_path = self.resolve_script_path(script_path)
        if not resolved_path:
            result = ScriptResult(
                success=False,
                errors=[f"Script not found: {script_path}"]
            )
            self._end_execution_log(log_entry, result, resolved_path, validator_func_name)
            return result
        
        logger.debug(f"   Resolved path: {resolved_path}")
        
        # Load module
        module = self.load_module(resolved_path)
        if not module:
            result = ScriptResult(
                success=False,
                errors=[f"Failed to load script: {script_path}"]
            )
            self._end_execution_log(log_entry, result, resolved_path, validator_func_name)
            return result
        
        logger.debug(f"   Module loaded successfully")
        
        # Find validator function
        validator_func = self.find_validator_function(module)
        if not validator_func:
            result = ScriptResult(
                success=False,
                errors=[f"No validator function found in script: {script_path}"]
            )
            self._end_execution_log(log_entry, result, resolved_path, validator_func_name)
            return result
        
        validator_func_name = getattr(validator_func, '__name__', str(validator_func))
        logger.debug(f"   Validator function: {validator_func_name}")
        
        # Log input context summary
        logger.debug(f"   Input context:")
        logger.debug(f"     - Endpoint: {context.request.endpoint}")
        logger.debug(f"     - Method: {context.request.method}")
        logger.debug(f"     - Response status: {context.response.status_code}")
        logger.debug(f"     - DB results count: {len(context.db_results)}")
        logger.debug(f"     - Extracted vars: {list(context.extracted_vars.keys())}")
        
        # Execute validator
        try:
            start_time = time.perf_counter()
            
            # Try calling with ScriptContext first
            try:
                logger.debug(f"   Calling {validator_func_name}(ScriptContext)...")
                result = validator_func(context)
            except TypeError as te:
                logger.debug(f"   ScriptContext failed ({te}), trying dict context...")
                # Fall back to dict context
                try:
                    result = validator_func(context.to_dict())
                except TypeError:
                    logger.debug(f"   Dict context failed, trying legacy signature...")
                    # Try legacy signature: (api_response, request_payload, ...)
                    result = self._call_legacy_validator(validator_func, context)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"   Script execution completed in {execution_time:.2f}ms")
            
            # Normalize result to ScriptResult
            normalized_result = self._normalize_result(result)
            
            # Log output summary
            logger.debug(f"   Output summary:")
            logger.debug(f"     - Success: {normalized_result.success}")
            logger.debug(f"     - Errors: {normalized_result.errors}")
            logger.debug(f"     - Extracted values: {list(normalized_result.extracted_values.keys())}")
            logger.debug(f"     - Computed values: {list(normalized_result.computed_values.keys())}")
            
            self._end_execution_log(log_entry, normalized_result, resolved_path, validator_func_name)
            return normalized_result
            
        except Exception as e:
            logger.error(f"[EXCEPTION] Script execution error in {script_path}: {e}")
            logger.debug(traceback.format_exc())
            result = ScriptResult(
                success=False,
                errors=[f"Script execution error: {str(e)}"],
                metadata={"exception": str(e), "traceback": traceback.format_exc()}
            )
            self._end_execution_log(log_entry, result, resolved_path, validator_func_name, exception=e)
            return result
    
    def _call_legacy_validator(self, func: Callable, context: ScriptContext) -> Any:
        """
        Call legacy validator functions with old signature.
        
        Supports signatures like:
        - validate_analytics_calculation(api_response, request_payload, db_results, ...)
        """
        # Try common legacy signatures
        try:
            # Most common legacy format
            return func(
                api_response=context.response.body,
                request_payload=context.test_case.get('payload'),
                db_results=context.db_results
            )
        except TypeError:
            pass
        
        try:
            # Simple format
            return func(context.response.body, context.test_case.get('payload'))
        except TypeError:
            pass
        
        # Last resort - just response
        return func(context.response.body)
    
    def _normalize_result(self, result: Any) -> ScriptResult:
        """
        Normalize script result to ScriptResult object.
        
        Handles various return formats:
        - ScriptResult object
        - Dict with result fields
        - Tuple (success, errors, computed_values)
        - Boolean (success only)
        """
        if isinstance(result, ScriptResult):
            return result
        
        if isinstance(result, dict):
            return ScriptResult.from_dict(result)
        
        if isinstance(result, tuple):
            return ScriptResult.from_tuple(result)
        
        if isinstance(result, bool):
            return ScriptResult(success=result)
        
        # Unknown format - treat as success with result in metadata
        logger.warning(f"Unknown script result format: {type(result)}")
        return ScriptResult(
            success=True,
            metadata={"raw_result": result}
        )
    
    def execute_from_test_case(
        self,
        test_case: Dict[str, Any],
        response: Any = None,
        db_results: List[Dict] = None,
        extracted_vars: Dict = None,
        config: Dict = None
    ) -> Optional[ScriptResult]:
        """
        Execute script(s) defined in test case configuration.
        
        Reads 'scripts' field from test case and executes the validator(s).
        
        Args:
            test_case: Test case configuration with 'scripts' field
            response: API response object
            db_results: Database query results
            extracted_vars: Previously extracted variables
            config: Framework configuration
        
        Returns:
            ScriptResult or None if no script configured
        """
        scripts = test_case.get('scripts')
        
        if not scripts:
            return None
        
        # Build context once
        context = self.build_context(
            test_case=test_case,
            response=response,
            db_results=db_results,
            extracted_vars=extracted_vars,
            config=config
        )
        
        # Handle single script or list of scripts
        if isinstance(scripts, str):
            script_list = [scripts]
        elif isinstance(scripts, list):
            script_list = scripts
        else:
            logger.warning(f"Invalid scripts format: {type(scripts)}")
            return None
        
        test_id = test_case.get('test_id', 'N/A')
        logger.info(f"[SCRIPTS] Executing {len(script_list)} script(s) for test: {test_id}")
        
        # Execute all scripts and aggregate results
        all_errors = []
        all_extracted = {}
        all_computed = {}
        all_comparison = {}
        overall_success = True
        execution_start = time.perf_counter()
        
        for idx, script in enumerate(script_list, 1):
            logger.info(f"   [{idx}/{len(script_list)}] Executing: {script}")
            result = self.execute_script(script, context)
            
            if not result.success:
                overall_success = False
                all_errors.extend(result.errors)
            
            all_extracted.update(result.extracted_values)
            all_computed.update(result.computed_values)
            all_comparison.update(result.comparison_data)
        
        total_duration = (time.perf_counter() - execution_start) * 1000
        
        # Log aggregate summary
        status_text = "[PASS]" if overall_success else "[FAIL]"
        logger.info(
            f"{status_text} Script execution complete for {test_id}: "
            f"{len(script_list)} scripts in {total_duration:.2f}ms "
            f"(success={overall_success}, errors={len(all_errors)}, "
            f"extracted={len(all_extracted)}, computed={len(all_computed)})"
        )
        
        if all_errors:
            logger.warning(f"   Errors encountered: {all_errors}")
        
        return ScriptResult(
            success=overall_success,
            errors=all_errors,
            extracted_values=all_extracted,
            computed_values=all_computed,
            comparison_data=all_comparison,
            metadata={
                "scripts_executed": script_list,
                "total_duration_ms": total_duration,
                "execution_summary": self.get_execution_summary()
            }
        )


# Convenience function for direct use
def execute_test_script(
    test_case: Dict[str, Any],
    response: Any = None,
    db_results: List[Dict] = None,
    extracted_vars: Dict = None,
    config: Dict = None
) -> Optional[ScriptResult]:
    """
    Execute custom script(s) defined in test case.
    
    Convenience function that creates a ScriptExecutor and runs the script.
    
    Args:
        test_case: Test case configuration
        response: API response object
        db_results: Database query results
        extracted_vars: Previously extracted variables  
        config: Framework configuration
    
    Returns:
        ScriptResult or None if no script configured
    """
    executor = ScriptExecutor()
    return executor.execute_from_test_case(
        test_case=test_case,
        response=response,
        db_results=db_results,
        extracted_vars=extracted_vars,
        config=config
    )
