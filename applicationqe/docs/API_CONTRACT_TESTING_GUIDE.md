# API Contract Testing Guide

## 📚 Overview

API Contract Testing ensures your APIs meet their specifications by validating:
- **Request/Response schemas** (JSON Schema)
- **OpenAPI/Swagger specs** compliance
- **Breaking changes** detection
- **Contract versioning** and drift

---

## 🎯 Key Features

### **1. JSON Schema Validation**
- Validate response structure
- Type checking
- Required fields validation
- Format validation (email, date-time, etc.)
- Nested object validation

### **2. OpenAPI/Swagger Support**
- Load specs from files (YAML/JSON) or URLs
- Validate responses against OpenAPI definitions
- Support for OpenAPI 2.0 and 3.0

### **3. Contract Management**
- Generate contracts from responses
- Save/load contracts
- Detect breaking changes
- Contract versioning

### **4. Integration with APIClient**
- Automatic validation on requests
- Seamless integration with existing API tests

---

## 🚀 Quick Start

### **Installation**

```bash
pip install -r requirements.txt
```

### **Basic JSON Schema Validation**

```python
from utils.api_contract import JSONSchemaValidator

validator = JSONSchemaValidator()

# Define schema
schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "name"]
}

# Validate response
result = validator.validate_response(response, schema)
assert result.is_valid, f"Validation failed: {result.errors}"
```

### **OpenAPI Validation**

```python
from utils.api_contract import OpenAPIValidator

# Load OpenAPI spec
validator = OpenAPIValidator("api_spec.yaml")

# Validate response against spec
result = validator.validate_response(
    "/users/1",
    "GET",
    response,
    status_code=200
)

print(result)  # Shows validation status and errors
```

### **Contract Testing**

```python
from utils.api_contract import ContractTester

tester = ContractTester()

# Define contract
contract = {
    "endpoint": "/api/users",
    "method": "GET",
    "status_code": 200,
    "response_schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"}
            }
        }
    }
}

# Test contract
result = tester.test_contract(contract, response)
assert result.is_valid
```

---

## 📖 Detailed Usage

### **1. JSON Schema Validation**

#### **Basic Types**

```python
validator = JSONSchemaValidator()

# Integer validation
schema = {"type": "integer", "minimum": 1, "maximum": 100}
result = validator.validate(42, schema)

# String validation
schema = {
    "type": "string",
    "minLength": 3,
    "maxLength": 50,
    "pattern": "^[a-z]+$"
}
result = validator.validate("hello", schema)

# Array validation
schema = {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 1,
    "maxItems": 10
}
result = validator.validate(["a", "b", "c"], schema)
```

#### **Object Validation**

```python
schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["id", "name", "email"]
}

data = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}

result = validator.validate(data, schema)
```

#### **Nested Objects**

```python
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
                        "lastName": {"type": "string"}
                    },
                    "required": ["firstName", "lastName"]
                }
            }
        }
    }
}
```

#### **Array of Objects**

```python
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    },
    "minItems": 1
}

data = [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
]

result = validator.validate(data, schema)
```

#### **Generate Schema from Example**

```python
example_data = {
    "id": 123,
    "name": "Product",
    "price": 99.99,
    "inStock": True,
    "tags": ["sale", "new"]
}

# Auto-generate schema
schema = validator.create_schema_from_example(example_data)

# Use generated schema for validation
result = validator.validate(example_data, schema)
```

---

### **2. OpenAPI/Swagger Validation**

#### **Load Spec from File**

```python
validator = OpenAPIValidator("openapi.yaml")
```

**Example OpenAPI Spec (openapi.yaml):**

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    username:
                      type: string
                    email:
                      type: string
```

#### **Load Spec from URL**

```python
validator = OpenAPIValidator()
validator.load_spec_from_url("https://api.example.com/openapi.json")
```

#### **Validate Against Spec**

```python
# Make API call
response = requests.get("https://api.example.com/users")

# Validate response
result = validator.validate_response(
    "/users",
    "GET",
    response,
    status_code=200
)

if not result.is_valid:
    print(f"Validation failed: {result.errors}")
```

---

### **3. Contract Management**

#### **Generate Contract from Response**

```python
tester = ContractTester()

# Make API call
response = requests.get("/api/products/1")

# Generate contract
contract = tester.generate_contract_from_response(
    "/api/products/{id}",
    "GET",
    response
)

print(contract)
# {
#     "endpoint": "/api/products/{id}",
#     "method": "GET",
#     "status_code": 200,
#     "response_schema": { ... }
# }
```

#### **Save and Load Contracts**

```python
from utils.api_contract import ContractRegistry

registry = ContractRegistry("contracts/")

# Save contract
registry.save_contract("get_product", contract)

# Load contract
saved_contract = registry.load_contract("get_product")

# List all contracts
contracts = registry.list_contracts()
print(contracts)  # ['get_product', 'list_users', ...]
```

#### **Detect Breaking Changes**

```python
# Old contract (v1)
old_contract = {
    "response_schema": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }
}

# New contract (v2)
new_contract = {
    "response_schema": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},  # Type changed!
            "name": {"type": "string"}
        },
        "required": ["id"]  # 'name' no longer required!
    }
}

# Detect changes
changes = tester.compare_contracts(old_contract, new_contract)

print("Breaking changes detected:")
for change in changes:
    print(f"  - {change}")
# Output:
#   - Type change for 'id': integer -> string
```

---

### **4. Integration with APIClient**

```python
from utils.api_client import APIClient
from utils.api_contract import ContractTester
import requests

# Setup contract validator
tester = ContractTester(openapi_spec="api_spec.yaml")

# Create API client with validator
session = requests.Session()
client = APIClient(
    session,
    "https://api.example.com",
    contract_validator=tester
)

# Make request
response = client.get("/users")

# Validate against contract
is_valid = client.validate_contract("/users", "GET", response)
assert is_valid, "Contract validation failed"
```

---

## 🎓 Advanced Examples

### **Complete Workflow Example**

```python
def test_user_api_complete_workflow():
    """Complete contract testing workflow"""

    # 1. Setup
    registry = ContractRegistry("contracts/")
    tester = ContractTester()

    # 2. Make initial API call (baseline)
    response = requests.get("https://api.example.com/users/1")

    # 3. Generate contract from response
    contract = tester.generate_contract_from_response(
        "/users/{id}",
        "GET",
        response
    )

    # 4. Save contract as baseline
    registry.save_contract("get_user_v1", contract)

    # 5. Later: Load and test new response
    new_response = requests.get("https://api.example.com/users/2")

    saved_contract = registry.load_contract("get_user_v1")
    result = tester.test_contract(saved_contract, new_response)

    # 6. Assert validation
    assert result.is_valid, f"Errors: {result.errors}"

    # 7. Check for changes
    new_contract = tester.generate_contract_from_response(
        "/users/{id}",
        "GET",
        new_response
    )

    changes = tester.compare_contracts(saved_contract, new_contract)
    if changes:
        print(f"⚠️ Breaking changes detected: {changes}")
```

### **Real-World User API Example**

```python
def test_user_api_contract():
    """Real-world user API contract test"""

    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 50,
                "pattern": "^[a-zA-Z0-9_]+$"
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "roles": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["user", "admin", "moderator"]
                },
                "minItems": 1
            },
            "created_at": {
                "type": "string",
                "format": "date-time"
            },
            "is_active": {"type": "boolean"}
        },
        "required": ["id", "username", "email", "roles"]
    }

    contract = {
        "endpoint": "/api/users/{id}",
        "method": "GET",
        "status_code": 200,
        "response_schema": user_schema
    }

    # Make API call
    response = requests.get("https://api.example.com/users/1")

    # Validate
    tester = ContractTester()
    result = tester.test_contract(contract, response)

    assert result.is_valid, f"Contract failed: {result}"
```

---

## 📊 Validation Results

### **Understanding Results**

```python
result = validator.validate_response(response, schema)

print(result.is_valid)      # True/False
print(result.errors)        # List of error messages
print(result.warnings)      # List of warnings
print(result.endpoint)      # API endpoint
print(result.method)        # HTTP method
print(result.timestamp)     # When validated

# Pretty print
print(result)
# Output:
# ✓ VALID - GET /api/users
#   Warnings (1):
#     - Additional property 'extra_field' found
```

---

## 🔧 Configuration

### **Strict Mode**

```python
# Strict: Additional properties fail validation
validator = JSONSchemaValidator(strict=True)

# Lenient: Additional properties allowed
validator = JSONSchemaValidator(strict=False)
```

### **Custom Validation**

```python
# Override per-validation
result = validator.validate(
    data,
    schema,
    allow_additional_properties=True  # Override strict mode
)
```

---

## 🎯 Best Practices

1. **Save Contracts**: Store baseline contracts for regression testing
2. **Version Contracts**: Track contract changes over time
3. **CI/CD Integration**: Run contract tests in pipeline
4. **Breaking Change Detection**: Alert on breaking changes
5. **Generate from Examples**: Use real responses to create schemas
6. **Validate Early**: Test contracts during development

---

## 🧪 Running Tests

```bash
# Run all contract tests
pytest tests/api/test_api_contract_examples.py -v

# Run specific test
pytest tests/api/test_api_contract_examples.py::test_json_schema_validation_basic -v

# With output
pytest tests/api/test_api_contract_examples.py -v -s
```

---

## 📝 Example Test Structure

```python
import pytest
from utils.api_contract import ContractTester, ContractRegistry

class TestUserAPI:
    @pytest.fixture
    def contract_tester(self):
        return ContractTester(openapi_spec="specs/user_api.yaml")

    @pytest.fixture
    def contract_registry(self, tmp_path):
        return ContractRegistry(str(tmp_path / "contracts"))

    def test_get_user(self, contract_tester, api_client):
        response = api_client.get("/users/1")
        result = contract_tester.test_openapi_contract(
            "/users/{id}",
            "GET",
            response
        )
        assert result.is_valid

    def test_create_user(self, contract_tester, api_client):
        data = {"username": "newuser", "email": "new@example.com"}
        response = api_client.post("/users", json=data)

        result = contract_tester.test_openapi_contract(
            "/users",
            "POST",
            response,
            status_code=201
        )
        assert result.is_valid
```

---

## 🚀 Integration with Framework

### **In conftest.py**

```python
@pytest.fixture(scope="session")
def contract_tester():
    """Shared contract tester"""
    return ContractTester(openapi_spec="specs/api.yaml")

@pytest.fixture
def validated_api_client(api_client, contract_tester):
    """API client with automatic contract validation"""
    api_client.contract_validator = contract_tester
    return api_client
```

### **In Tests**

```python
def test_with_contract_validation(validated_api_client):
    response = validated_api_client.get("/users")

    # Automatic validation
    is_valid = validated_api_client.validate_contract(
        "/users",
        "GET",
        response
    )
    assert is_valid
```

---

## 📚 Resources

- [JSON Schema Documentation](https://json-schema.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Example Tests](tests/api/test_api_contract_examples.py)
- [Contract Utilities](utils/api_response_utils.py)
- [API Request Client](utils/api_request_utils.py)

---

## ✅ Summary

API Contract Testing is now integrated into your framework with:
- ✅ JSON Schema validation
- ✅ OpenAPI/Swagger support
- ✅ Contract generation and storage
- ✅ Breaking change detection
- ✅ APIClient integration
- ✅ Comprehensive examples

**Next Steps**: Run the example tests and create contracts for your APIs!
