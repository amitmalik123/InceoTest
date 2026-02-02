import json
import os
import re
from framework.common.logger import get_logger

logger = get_logger(__name__)

class ApiDefinitionsLoader:
    def __init__(self, definitions_file=None):
        if definitions_file is None:
            definitions_file = os.path.join(os.path.dirname(__file__), '..', 'api_common_definitions.json')
        self.definitions_file = definitions_file
        self._definitions = None

    def load(self, force_reload=False):
        if self._definitions and not force_reload:
            return self._definitions

        logger.info(f"Loading API definitions from: {self.definitions_file}")
        try:
            with open(self.definitions_file, 'r') as f:
                self._definitions = json.load(f)
            logger.info("Loaded API definitions successfully.")
            self._validate_structure()
            return self._definitions
        except Exception as e:
            logger.error(f"Error loading API definitions: {e}")
            raise

    def _validate_structure(self):
        required_keys = ['headers', 'custom_validations', 'validate', 'common_functions']
        for key in required_keys:
            if key not in self._definitions:
                raise ValueError(f"Missing required key in definitions: {key}")

    def get_headers(self, token=None, additional_headers=None):
        headers = self._definitions.get('headers', {}).copy()
        if token:
            for k, v in headers.items():
                headers[k] = v.replace('{{token}}', token)
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def get_validations(self):
        return self._definitions.get('custom_validations', {}).get('fields', {})

    def get_common_functions(self, function_type=None):
        functions = self._definitions.get('common_functions', [])
        if function_type:
            return [f for f in functions if f.get('type') == function_type]
        return functions

    def validate_field(self, field_name, value):
        validations = self.get_validations()
        rule = validations.get(field_name)
        if not rule:
            logger.warning(f"No validation rule for field: {field_name}")
            return True
        pattern = rule.get('regex')
        if pattern and not re.match(pattern, str(value)):
            logger.warning(f"Validation failed for field '{field_name}' with value '{value}'")
            return False
        return True
