"""
API Contract Testing Examples

Demonstrates comprehensive contract testing:
- JSON Schema validation
- OpenAPI/Swagger validation
- Contract generation and storage
- Breaking change detection
"""

from unittest.mock import Mock

import pytest

from utils.api_response_utils import (
    ContractRegistry,
    ContractTester,
    ContractValidationResult,
    JSONSchemaValidator,
    OpenAPIValidator,
)

# ============================================================================
# JSON Schema Validation Examples
# ============================================================================


def test_json_schema_validation_basic():
    """Test basic JSON schema validation"""
    validator = JSONSchemaValidator(strict=True)

    # Define schema
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["id", "name"],
    }

    # Valid data
    valid_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}

    result = validator.validate(valid_data, schema)
    assert result.is_valid, f"Validation failed: {result.errors}"
    assert len(result.errors) == 0


def test_json_schema_validation_invalid():
    """Test schema validation with invalid data"""
    validator = JSONSchemaValidator(strict=True)

    schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["id", "name"],
    }

    # Missing required field
    invalid_data = {
        "id": 1
        # Missing 'name'
    }

    result = validator.validate(invalid_data, schema)
    assert not result.is_valid
    assert len(result.errors) > 0
    print(f"Expected validation errors: {result.errors}")


def test_json_schema_array_validation():
    """Test validation of array responses"""
    validator = JSONSchemaValidator()

    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "username": {"type": "string"}},
            "required": ["id", "username"],
        },
        "minItems": 1,
    }

    data = [{"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}]

    result = validator.validate(data, schema)
    assert result.is_valid


def test_json_schema_nested_objects():
    """Test validation of nested objects"""
    validator = JSONSchemaValidator()

    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                        },
                        "required": ["firstName", "lastName"],
                    },
                },
                "required": ["id", "profile"],
            }
        },
        "required": ["user"],
    }

    data = {"user": {"id": 1, "profile": {"firstName": "John", "lastName": "Doe"}}}

    result = validator.validate(data, schema)
    assert result.is_valid


def test_schema_generation_from_example():
    """Test automatic schema generation from example data"""
    validator = JSONSchemaValidator()

    example = {
        "id": 123,
        "name": "Test Product",
        "price": 99.99,
        "inStock": True,
        "tags": ["electronics", "sale"],
        "metadata": {"created": "2024-01-01", "author": "admin"},
    }

    schema = validator.create_schema_from_example(example)

    # Verify generated schema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert schema["properties"]["id"]["type"] == "integer"
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["price"]["type"] == "number"
    assert schema["properties"]["inStock"]["type"] == "boolean"
    assert schema["properties"]["tags"]["type"] == "array"

    # Schema should validate the example
    result = validator.validate(example, schema)
    assert result.is_valid


# ============================================================================
# Response Validation Examples
# ============================================================================


def test_validate_mock_response():
    """Test validation of mock API response"""
    validator = JSONSchemaValidator()

    # Create mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "username": "testuser", "email": "test@example.com"}

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "string"},
            "email": {"type": "string"},
        },
        "required": ["id", "username", "email"],
    }

    result = validator.validate_response(mock_response, schema, status_code=200)
    assert result.is_valid


def test_validate_response_status_code():
    """Test status code validation"""
    validator = JSONSchemaValidator()

    # Mock response with wrong status
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not found"}

    schema = {"type": "object"}

    result = validator.validate_response(mock_response, schema, status_code=200)
    assert not result.is_valid
    assert any("status code" in error.lower() for error in result.errors)


# ============================================================================
# OpenAPI/Swagger Validation Examples
# ============================================================================


def test_openapi_spec_creation():
    """Test creating OpenAPI validator with spec"""
    # Create sample OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }

    # Create validator with in-memory spec
    validator = OpenAPIValidator()
    validator.spec = openapi_spec

    # Get schema
    schema = validator.get_endpoint_schema("/users", "GET", 200)

    assert schema is not None
    assert schema["type"] == "array"


def test_openapi_response_validation():
    """Test validating response against OpenAPI spec"""
    # Setup OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users/1": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                        "required": ["id", "name"],
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }

    validator = OpenAPIValidator()
    validator.spec = openapi_spec

    # Mock valid response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "John Doe", "email": "john@example.com"}

    result = validator.validate_response("/users/1", "GET", mock_response, 200)
    assert result.is_valid, f"Validation failed: {result.errors}"


# ============================================================================
# Contract Testing Examples
# ============================================================================


def test_contract_tester_basic():
    """Test basic contract testing"""
    tester = ContractTester()

    # Define contract
    contract = {
        "endpoint": "/api/products",
        "method": "GET",
        "status_code": 200,
        "response_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
                "required": ["id", "name", "price"],
            },
        },
    }

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "Product 1", "price": 99.99},
        {"id": 2, "name": "Product 2", "price": 149.99},
    ]

    result = tester.test_contract(contract, mock_response)
    assert result.is_valid, f"Contract test failed: {result.errors}"


def test_contract_generation():
    """Test automatic contract generation from response"""
    tester = ContractTester()

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 123,
        "name": "New Product",
        "created": "2024-01-01T00:00:00Z",
    }

    # Generate contract
    contract = tester.generate_contract_from_response("/api/products", "POST", mock_response)

    assert contract["endpoint"] == "/api/products"
    assert contract["method"] == "POST"
    assert contract["status_code"] == 201
    assert "response_schema" in contract
    assert contract["response_schema"]["type"] == "object"


def test_breaking_change_detection():
    """Test detection of breaking changes between contracts"""
    tester = ContractTester()

    # Old contract
    old_contract = {
        "response_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["id", "name", "email"],
        }
    }

    # New contract - removed required field and changed type
    new_contract = {
        "response_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},  # Changed from integer
                "name": {"type": "string"},
                # Removed 'email'
            },
            "required": ["id", "name"],  # 'email' no longer required
        }
    }

    changes = tester.compare_contracts(old_contract, new_contract)

    assert len(changes) > 0
    assert any("email" in change.lower() for change in changes)
    assert any("type change" in change.lower() for change in changes)
    print(f"Detected breaking changes: {changes}")


# ============================================================================
# Contract Registry Examples
# ============================================================================


def test_contract_registry(tmp_path):
    """Test saving and loading contracts"""
    registry = ContractRegistry(storage_dir=str(tmp_path / "contracts"))

    contract = {
        "endpoint": "/api/users",
        "method": "GET",
        "status_code": 200,
        "response_schema": {"type": "array", "items": {"type": "object"}},
    }

    # Save contract
    registry.save_contract("users_list", contract)

    # Load contract
    loaded = registry.load_contract("users_list")
    assert loaded is not None
    assert loaded["endpoint"] == "/api/users"

    # List contracts
    contracts = registry.list_contracts()
    assert "users_list" in contracts

    # Delete contract
    deleted = registry.delete_contract("users_list")
    assert deleted

    contracts = registry.list_contracts()
    assert "users_list" not in contracts


# ============================================================================
# Integration Examples
# ============================================================================


def test_complete_contract_workflow(tmp_path):
    """Test complete contract testing workflow"""
    registry = ContractRegistry(storage_dir=str(tmp_path / "contracts"))
    tester = ContractTester()

    # Step 1: Make API call (mocked)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
    }

    # Step 2: Generate contract from response
    contract = tester.generate_contract_from_response("/api/users/1", "GET", mock_response)

    # Step 3: Save contract as baseline
    registry.save_contract("get_user", contract)

    # Step 4: Later, validate new response against saved contract
    new_response = Mock()
    new_response.status_code = 200
    new_response.json.return_value = {
        "id": 2,
        "username": "newuser",
        "email": "new@example.com",
        "created_at": "2024-01-02T00:00:00Z",
    }

    saved_contract = registry.load_contract("get_user")
    result = tester.test_contract(saved_contract, new_response)

    assert result.is_valid, f"Contract validation failed: {result.errors}"


def test_contract_validation_result_formatting():
    """Test formatting of validation results"""
    result = ContractValidationResult(is_valid=False, endpoint="/api/users", method="GET")

    result.add_error("Missing required field: 'email'")
    result.add_error("Type mismatch for 'id': expected integer, got string")
    result.add_warning("Additional property 'extra_field' found")

    output = str(result)

    assert "✗ INVALID" in output
    assert "GET /api/users" in output
    assert "email" in output
    assert "Warnings" in output
    print(f"\nValidation Result:\n{output}")


# ============================================================================
# Real-World Example: User API Contract
# ============================================================================


def test_user_api_contract_example():
    """Real-world example: User API contract testing"""

    # Define user API contract
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "username": {"type": "string", "minLength": 3, "maxLength": 50},
            "email": {"type": "string", "format": "email"},
            "roles": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "created_at": {"type": "string", "format": "date-time"},
        },
        "required": ["id", "username", "email", "roles"],
    }

    contract = {
        "endpoint": "/api/users/{id}",
        "method": "GET",
        "status_code": 200,
        "response_schema": user_schema,
    }

    # Test with valid user data
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "roles": ["user", "admin"],
        "created_at": "2024-01-01T12:00:00Z",
    }

    tester = ContractTester()
    result = tester.test_contract(contract, mock_response)

    assert result.is_valid, f"User contract validation failed: {result.errors}"
    print("\n✓ User API contract validated successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
