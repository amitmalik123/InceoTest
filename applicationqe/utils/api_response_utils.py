import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

logger = logging.getLogger(__name__)


def get_values_from_household_api_open_accounts(field_name: str) -> List[str]:
    paths = []
    for i in range(20):
        paths.append(f"accounts[{i}].{field_name}")
    return paths


def retrieve_all_values_from_response(response: Any, json_paths: List[str]) -> List[Any]:
    values = []

    if hasattr(response, 'json'):
        data = response.json()
    elif isinstance(response, dict):
        data = response
    else:
        raise ValueError("Response must be a requests.Response object or dict")

    for path in json_paths:
        value = data
        parts = path.replace('[', '.').replace(']', '').split('.')
        try:
            for part in parts:
                if part.isdigit():
                    value = value[int(part)]
                elif isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None
                if value is None:
                    break
            if value is not None:
                values.append(value)
        except (KeyError, IndexError, TypeError, AttributeError):
            continue

    return values


def retrieve_boolean_value_from_response(response: Any, json_path: str) -> bool:
    if hasattr(response, 'json'):
        data = response.json()
    elif isinstance(response, dict):
        data = response
    else:
        raise ValueError("Response must be a requests.Response object or dict")
    
    try:
        value = data
        parts = json_path.replace('[', '.').replace(']', '').split('.')
        
        for part in parts:
            if part.isdigit():
                value = value[int(part)]
            else:
                value = value.get(part) if isinstance(value, dict) else None
            
            if value is None:
                return False
        
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        elif isinstance(value, int):
            return value != 0
        else:
            return bool(value)
    except (KeyError, IndexError, TypeError, AttributeError):
        return False


@dataclass
class ContractValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None
    method: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)

    def __str__(self) -> str:
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        result = [f"{status} - {self.method} {self.endpoint}"]

        if self.errors:
            result.append(f"  Errors ({len(self.errors)}):")
            for error in self.errors:
                result.append(f"    - {error}")

        if self.warnings:
            result.append(f"  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                result.append(f"    - {warning}")

        return "\n".join(result)


class JSONSchemaValidator:
    def __init__(self, strict: bool = True):
        self.strict = strict

    def validate(
        self, data: Any, schema: Dict, allow_additional_properties: Optional[bool] = None
    ) -> ContractValidationResult:
        result = ContractValidationResult(is_valid=True)

        if allow_additional_properties is None:
            allow_additional_properties = not self.strict

        if not allow_additional_properties and schema.get("type") == "object":
            if "additionalProperties" not in schema:
                schema = schema.copy()
                schema["additionalProperties"] = False

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            result.add_error(f"Schema validation failed: {e.message}")
            logger.error(
                f"Validation error at path {'.'.join(str(p) for p in e.path)}: {e.message}"
            )
        except jsonschema.SchemaError as e:
            result.add_error(f"Invalid schema: {e.message}")
            logger.error(f"Schema error: {e.message}")

        return result

    def validate_response(
        self, response: Any, expected_schema: Dict, status_code: Optional[int] = None
    ) -> ContractValidationResult:
        result = ContractValidationResult(is_valid=True)

        if status_code is not None:
            actual_status = getattr(response, "status_code", None)
            if actual_status != status_code:
                result.add_error(
                    f"Status code mismatch: expected {status_code}, got {actual_status}"
                )

        try:
            data = response.json() if hasattr(response, "json") else response
            schema_result = self.validate(data, expected_schema)
            result.errors.extend(schema_result.errors)
            result.warnings.extend(schema_result.warnings)
            result.is_valid = result.is_valid and schema_result.is_valid
        except Exception as e:
            result.add_error(f"Failed to parse response: {str(e)}")

        return result

    def create_schema_from_example(self, example: Dict) -> Dict:
        def infer_type(value: Any) -> Dict:
            if value is None:
                return {"type": "null"}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, list):
                if len(value) > 0:
                    return {"type": "array", "items": infer_type(value[0])}
                return {"type": "array"}
            elif isinstance(value, dict):
                properties = {}
                required = []
                for key, val in value.items():
                    properties[key] = infer_type(val)
                    required.append(key)
                return {"type": "object", "properties": properties, "required": required}
            else:
                return {}

        return infer_type(example)


class OpenAPIValidator:
    def __init__(self, spec_path: Optional[str] = None):
        self.spec_path = spec_path
        self.spec: Optional[Dict] = None

        if spec_path:
            self.load_spec(spec_path)

    def load_spec(self, spec_path: str):
        path = Path(spec_path)

        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        try:
            if spec_path.endswith((".yaml", ".yml")):
                import yaml

                with open(spec_path, "r") as f:
                    self.spec = yaml.safe_load(f)
            else:
                with open(spec_path, "r") as f:
                    self.spec = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load spec: {e}")

    def load_spec_from_url(self, url: str):
        try:
            import requests

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if "yaml" in response.headers.get("content-type", ""):
                import yaml

                self.spec = yaml.safe_load(response.text)
            else:
                self.spec = response.json()
        except Exception as e:
            raise ValueError(f"Failed to load spec from URL: {e}")

    def get_endpoint_schema(
        self, path: str, method: str, response_code: int = 200
    ) -> Optional[Dict]:
        if not self.spec:
            raise ValueError("No spec loaded")

        method = method.lower()

        paths = self.spec.get("paths", {})
        endpoint_spec = paths.get(path)

        if not endpoint_spec:
            logger.warning(f"Path {path} not found in spec")
            return None

        method_spec = endpoint_spec.get(method)
        if not method_spec:
            logger.warning(f"Method {method} not found for path {path}")
            return None

        responses = method_spec.get("responses", {})
        response_spec = responses.get(str(response_code))

        if not response_spec:
            logger.warning(f"Response {response_code} not found for {method} {path}")
            return None

        content = response_spec.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema")

        if not schema:
            schema = response_spec.get("schema")

        return schema

    def validate_response(
        self, path: str, method: str, response: Any, status_code: int = 200
    ) -> ContractValidationResult:
        result = ContractValidationResult(is_valid=True, endpoint=path, method=method.upper())

        if not self.spec:
            result.add_error("No OpenAPI spec loaded")
            return result

        schema = self.get_endpoint_schema(path, method, status_code)

        if not schema:
            result.add_warning(f"No schema found for {method.upper()} {path} {status_code}")
            return result

        validator = JSONSchemaValidator(strict=False)
        validation_result = validator.validate_response(response, schema, status_code)

        result.errors.extend(validation_result.errors)
        result.warnings.extend(validation_result.warnings)
        result.is_valid = validation_result.is_valid

        return result


class ContractTester:
    def __init__(self, openapi_spec: Optional[str] = None):
        self.schema_validator = JSONSchemaValidator()
        self.openapi_validator = None

        if openapi_spec:
            self.openapi_validator = OpenAPIValidator(openapi_spec)

    def test_contract(
        self, contract: Dict, response: Any, strict: bool = True
    ) -> ContractValidationResult:
        result = ContractValidationResult(is_valid=True)

        endpoint = contract.get("endpoint")
        method = contract.get("method")
        expected_status = contract.get("status_code", 200)
        response_schema = contract.get("response_schema")

        result.endpoint = endpoint
        result.method = method

        actual_status = getattr(response, "status_code", None)
        if actual_status != expected_status:
            result.add_error(f"Status code: expected {expected_status}, got {actual_status}")

        if response_schema:
            schema_result = self.schema_validator.validate_response(response, response_schema)
            result.errors.extend(schema_result.errors)
            result.warnings.extend(schema_result.warnings)
            result.is_valid = result.is_valid and schema_result.is_valid

        return result

    def test_openapi_contract(
        self, path: str, method: str, response: Any, status_code: int = 200
    ) -> ContractValidationResult:
        if not self.openapi_validator:
            result = ContractValidationResult(is_valid=False)
            result.add_error("No OpenAPI spec configured")
            return result

        return self.openapi_validator.validate_response(path, method, response, status_code)

    def generate_contract_from_response(self, endpoint: str, method: str, response: Any) -> Dict:
        data = response.json() if hasattr(response, "json") else response
        schema = self.schema_validator.create_schema_from_example(data)

        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": getattr(response, "status_code", 200),
            "response_schema": schema,
        }

    def compare_contracts(self, old_contract: Dict, new_contract: Dict) -> List[str]:
        breaking_changes = []

        old_schema = old_contract.get("response_schema", {})
        new_schema = new_contract.get("response_schema", {})

        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        removed_required = old_required - new_required
        if removed_required:
            breaking_changes.append(f"Removed required fields: {', '.join(removed_required)}")

        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})

        for field, old_prop in old_props.items():
            if field in new_props:
                old_type = old_prop.get("type")
                new_type = new_props[field].get("type")

                if old_type != new_type:
                    breaking_changes.append(f"Type change for '{field}': {old_type} -> {new_type}")

        return breaking_changes


class ContractRegistry:
    def __init__(self, storage_dir: str = "contracts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_contract(self, name: str, contract: Dict):
        filepath = self.storage_dir / f"{name}.json"

        with open(filepath, "w") as f:
            json.dump(contract, f, indent=2)

    def load_contract(self, name: str) -> Optional[Dict]:
        filepath = self.storage_dir / f"{name}.json"

        if not filepath.exists():
            logger.warning(f"Contract not found: {name}")
            return None

        with open(filepath, "r") as f:
            contract = json.load(f)
        return contract

    def list_contracts(self) -> List[str]:
        contracts = [f.stem for f in self.storage_dir.glob("*.json")]
        return sorted(contracts)

    def delete_contract(self, name: str) -> bool:
        filepath = self.storage_dir / f"{name}.json"

        if filepath.exists():
            filepath.unlink()
            return True

        return False
