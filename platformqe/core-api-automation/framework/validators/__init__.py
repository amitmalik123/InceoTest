"""
Validators Package

Contains validation logic for API testing framework including:
- Core validators (status, schema, fields, security)
- Script executor for custom validator scripts
- Base validator interface for creating custom validators
- SOAP validators for SOAP-specific validation
"""

from framework.validators.validators import (
    Validators,
    validate_db_comparison,
)

from framework.validators.script_executor import (
    ScriptExecutor,
    ScriptContext,
    ScriptResult,
    RequestContext,
    ResponseContext,
    execute_test_script,
)

from framework.validators.base_validator import (
    BaseValidator,
    create_success_result,
    create_failure_result,
)

__all__ = [
    # Core validators
    'Validators',
    'validate_db_comparison',
    
    # Script executor
    'ScriptExecutor',
    'ScriptContext',
    'ScriptResult',
    'RequestContext',
    'ResponseContext',
    'execute_test_script',
    
    # Base validator interface
    'BaseValidator',
    'create_success_result',
    'create_failure_result',
]
