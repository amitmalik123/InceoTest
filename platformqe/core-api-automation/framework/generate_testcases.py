
import json
import yaml
import os
import sys
import pathlib
from typing import List, Dict, Optional
from framework.common.logger import get_logger
from framework.common.utils import normalize_path
from framework.loaders.path_loader import get_project_path
from zeep import Client

logger = get_logger(__name__)

class TestCaseGenerator:
    def __init__(self, testcase_template_path: Optional[str] = None):
        # Use path_utils for project root path resolution
        default_template_path = get_project_path('templates', 'TestCase_Template.json')
        self.testcase_template_path = testcase_template_path or str(default_template_path)
        self.testcase_template = self._load_template(self.testcase_template_path)
    
    def _generate_service_name(self, api_title: str, input_file: Optional[str] = None) -> str:
        """
        Generate a clean, unique service name from API title or input file.
        Maximum length: 30 characters to avoid Windows MAX_PATH issues.
        Examples:
            "Parties Service API 1.0" -> "parties"
            "PartiesService API 1.0" -> "parties"
            "Work Item Notification API" -> "work_item_notification"
            "UserService" -> "user_service"
        """
        import re
        
        MAX_SERVICE_NAME_LENGTH = 30
        
        # Try to extract service name from input file first
        if input_file:
            # Extract base filename without path and extension
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            # Clean up common patterns like "swagger", "openapi", "api", etc.
            base_name = re.sub(r'(swagger|openapi|spec|api)[-_]?', '', base_name, flags=re.IGNORECASE)
            if base_name and not base_name.isdigit():
                # Convert to snake_case
                service_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', base_name)
                service_name = re.sub(r'[\s\-\.]+', '_', service_name).lower()
                service_name = re.sub(r'[^a-z0-9_]', '', service_name)
                service_name = re.sub(r'_+', '_', service_name).strip('_')
                if service_name:
                    # Limit length
                    if len(service_name) > MAX_SERVICE_NAME_LENGTH:
                        service_name = service_name[:MAX_SERVICE_NAME_LENGTH].rstrip('_')
                    return service_name
        
        # Fall back to API title
        if api_title:
            # Remove version numbers first (v1, v2, 1.0, 2.0, etc.)
            clean_title = re.sub(r'\s+v?\d+[\.\d]*\s*$', '', api_title, flags=re.IGNORECASE)  # Trailing version
            clean_title = re.sub(r'\s+v?\d+[\.\d]*\s+', ' ', clean_title, flags=re.IGNORECASE)  # Middle version
            
            # Remove environment indicators and company names that appear at start (test, dev, prod, test12, t10, assetmark, etc.)
            clean_title = re.sub(r'^[^\w]*\b(test|dev|prod|uat|staging|qa|t)\d*\b[-_\s]*', '', clean_title, flags=re.IGNORECASE)
            clean_title = re.sub(r'^[^\w]*\b\w+\b\s*[-_]\s*', '', clean_title, flags=re.IGNORECASE)  # Remove "CompanyName - " pattern
            
            # Split on CamelCase first to separate "PartiesService" -> "Parties Service"
            clean_title = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', clean_title)
            
            # Remove standalone "API", "Service", "REST" words
            clean_title = re.sub(r'\b(API|Service|REST)\b', '', clean_title, flags=re.IGNORECASE)
            
            # Convert to lowercase and remove all separators (no underscores)
            service_name = re.sub(r'[\s\-\.]+', '', clean_title).lower()
            service_name = re.sub(r'[^a-z0-9]', '', service_name)
            
            # Limit length - if too long, try to keep last meaningful word (usually the actual service name)
            if len(service_name) > MAX_SERVICE_NAME_LENGTH:
                # Try to find word boundaries in the CamelCase before it was lowercased
                # For "WorkItemNotification" -> "workitemnotification", keep last part
                # Look for capital letters pattern to find word boundaries
                temp_title = clean_title.replace(' ', '').replace('-', '').replace('.', '')
                matches = re.findall(r'[A-Z][a-z]*', temp_title)
                if matches and len(matches) > 1:
                    # Take last 2-3 words
                    service_name = ''.join(matches[-2:]).lower()
                    if len(service_name) > MAX_SERVICE_NAME_LENGTH:
                        service_name = ''.join(matches[-1:]).lower()
                # If still too long, truncate
                if len(service_name) > MAX_SERVICE_NAME_LENGTH:
                    service_name = service_name[:MAX_SERVICE_NAME_LENGTH]
            
            return service_name if service_name else 'api_service'
        
        return 'api_service'

    def parse_wsdl(self, wsdl_path: str) -> List[Dict]:
        client = Client(wsdl=wsdl_path)
        cases = []
        id_counter = 1
        from lxml import etree
        for service in client.wsdl.services.values():
            # Generate clean service name
            service_name = self._generate_service_name(service.name, wsdl_path)
            
            for port in service.ports.values():
                operations = port.binding._operations.values()
                endpoint_address = port.binding_options.get('address', '')
                for op in operations:
                    # Extract soap_action
                    soap_action = getattr(op, 'soapaction', '')
                    # Generate a sample soap_envelope
                    soap_envelope = ''
                    try:
                        # Use Zeep's create_message to generate a sample envelope
                        binding = port.binding
                        # Use dummy values for input
                        dummy_args = []
                        elements = getattr(op.input.body.type, 'elements', [])
                        for _ in elements:
                            dummy_args.append('value')
                        envelope = binding.create_message(client.service, op.name, *dummy_args)
                        soap_envelope = etree.tostring(envelope, pretty_print=True, encoding='unicode')
                    except Exception as e:
                        soap_envelope = '<Envelope>...</Envelope>'
                    case = {
                        'test_id': f"TC{id_counter:03d}",
                        'service_name': service_name,
                        'port_name': port.name,
                        'operation': op.name,
                        'test_name': f"{op.name} [WSDL] (TC{id_counter:03d})",
                        'test_summary': f"Test TC{id_counter:03d}: {op.name} operation on {service.name}/{port.name}",
                        'endpoint': endpoint_address,
                        'method': 'SOAP',
                        'wsdl_operation': op.name,
                        'input': self._get_wsdl_input_example(op),
                        'soap_action': soap_action,
                        'soap_envelope': soap_envelope,
                        'expected_status': '200',
                        'test_type': ['Functional']
                    }
                    cases.append(case)
                    id_counter += 1
        logger.info(f"Extracted {len(cases)} test cases from WSDL: {wsdl_path}")
        return cases

    def _get_wsdl_input_example(self, op):
        # Use Zeep's operation input body elements for robust input extraction
        example = {}
        try:
            elements = getattr(op.input.body.type, 'elements', [])
            for name, element in elements:
                example[name] = f"<{getattr(element.type, 'name', 'value')}>"
        except Exception as e:
            example['input'] = '<value>'
        return example

    def _load_template(self, path: str) -> Dict:
        from pathlib import Path
        from framework.loaders.path_loader import get_project_path
        
        if Path(path).is_absolute():
            resolved_path = Path(path)
        else:
            resolved_path = get_project_path(*os.path.normpath(path).split(os.sep))
        logger.info(f"Resolved template path: {resolved_path}")
        if not resolved_path.exists():
            logger.error(f"Template file not found: {resolved_path}")
            raise FileNotFoundError(f"Template file not found: {resolved_path}")
        with open(str(resolved_path), 'r') as f:
            data = json.load(f)
        if not isinstance(data, list) or not data:
            raise ValueError("Template must be a non-empty JSON array.")
        logger.info(f"Loaded template from {resolved_path}")
        return data[0]

    def parse_openapi(self, openapi_path: str) -> List[Dict]:
        import re
        if re.match(r'^https?://', openapi_path):
            import requests
            logger.info(f"Fetching OpenAPI spec from URL: {openapi_path}")
            resp = requests.get(openapi_path, timeout=10, verify=False)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch OpenAPI spec from URL: {openapi_path} (status {resp.status_code})")
                raise FileNotFoundError(f"OpenAPI spec not found at URL: {openapi_path}")
            # Try to parse as JSON, fallback to YAML
            try:
                spec = resp.json()
            except Exception:
                spec = yaml.safe_load(resp.text)
        else:
            from framework.loaders.path_loader import get_project_path
            openapi_file_path = get_project_path(*os.path.normpath(openapi_path).split(os.sep))
            if not openapi_file_path.exists():
                logger.error(f"OpenAPI file not found: {openapi_path}")
                raise FileNotFoundError(f"OpenAPI file not found: {openapi_path}")
            with open(str(openapi_file_path), 'r') as f:
                spec = json.load(f) if openapi_path.endswith('.json') else yaml.safe_load(f)

        # Generate clean service name from API title and/or file name
        api_title = spec.get('info', {}).get('title', 'APIService')
        service_name = self._generate_service_name(api_title, openapi_path)
        logger.info(f"Generated service_name: '{service_name}' from API title: '{api_title}'")

        cases = []
        paths = spec.get('paths', {})
        id_counter = 1
        for endpoint, methods in paths.items():
            for method, details in methods.items():
                base_case = {
                    'endpoint': endpoint,
                    'method': method.upper(),
                    'service_name': service_name,
                }

                # Positive case
                pos_case = base_case.copy()
                pos_case['test_id'] = f"TC{id_counter:03d}"
                pos_case['test_name'] = (details.get('summary', f'{method.upper()} {endpoint}') + ' [positive] ' + f"({pos_case['test_id']})").strip()
                pos_case['test_summary'] = f"Test {pos_case['test_id']}: {pos_case['test_name']}"
                pos_case['expected_status'] = '200'
                pos_case['test_type'] = 'Functional'
                pos_case['test_type'] = ['Functional']
                cases.append(pos_case)
                id_counter += 1

                params = details.get('parameters', [])
                request_body = details.get('requestBody', {})
                responses = details.get('responses', {})
                # Negative: missing required param
                for param in params:
                    if param.get('required', False):
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: missing {param['name']}] (TC{id_counter:03d})",
                            'expected_status': '400',
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'missing_param': param['name']
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
                    # Negative: invalid type
                    schema = param.get('schema', {})
                    if schema.get('type') == 'integer':
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: invalid type for {param['name']}] (TC{id_counter:03d})",
                            'expected_status': '400',
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'invalid_param': {param['name']: 'not_an_integer'}
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
                    # Negative: invalid enum
                    if 'enum' in schema:
                        invalid_enum = schema['enum'][0] + '_invalid' if schema['enum'] else 'invalid_enum'
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: invalid enum for {param['name']}] (TC{id_counter:03d})",
                            'expected_status': '400',
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'invalid_param': {param['name']: invalid_enum}
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
                    # Negative: boundary values
                    if 'minimum' in schema:
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: below min for {param['name']}] (TC{id_counter:03d})",
                            'expected_status': '400',
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'invalid_param': {param['name']: schema['minimum'] - 1}
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
                    if 'maximum' in schema:
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: above max for {param['name']}] (TC{id_counter:03d})",
                            'expected_status': '400',
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'invalid_param': {param['name']: schema['maximum'] + 1}
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
                # Negative: extra/unexpected param
                case = {
                    **base_case,
                    'test_id': f"TC{id_counter:03d}",
                    'test_name': f"{method.upper()} {endpoint} [negative: extra param] (TC{id_counter:03d})",
                    'expected_status': '400',
                    'test_type': 'Negative',
                        'test_type': ['Negative'],
                    'extra_param': {'unexpected_param': 'unexpected'}
                }
                case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                cases.append(case)
                id_counter += 1
                # Negative: invalid payload (if requestBody present)
                if request_body:
                    case = {
                        **base_case,
                        'test_id': f"TC{id_counter:03d}",
                        'test_name': f"{method.upper()} {endpoint} [negative: invalid payload] (TC{id_counter:03d})",
                        'expected_status': '400',
                        'test_type': 'Negative',
                            'test_type': ['Negative'],
                        'invalid_payload': True
                    }
                    case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                    cases.append(case)
                    id_counter += 1
                # Negative: missing/invalid auth
                security = details.get('security', spec.get('security', []))
                if security:
                    case1 = {
                        **base_case,
                        'test_id': f"TC{id_counter:03d}",
                        'test_name': f"{method.upper()} {endpoint} [negative: missing auth] (TC{id_counter:03d})",
                        'expected_status': '401',
                        'test_type': 'Negative',
                            'test_type': ['Negative'],
                        'no_auth': True
                    }
                    case1['test_summary'] = f"Test {case1['test_id']}: {case1['test_name']}"
                    cases.append(case1)
                    id_counter += 1
                    case2 = {
                        **base_case,
                        'test_id': f"TC{id_counter:03d}",
                        'test_name': f"{method.upper()} {endpoint} [negative: invalid auth] (TC{id_counter:03d})",
                        'expected_status': '401',
                        'test_type': 'Negative',
                            'test_type': ['Negative'],
                        'invalid_auth': True
                    }
                    case2['test_summary'] = f"Test {case2['test_id']}: {case2['test_name']}"
                    cases.append(case2)
                    id_counter += 1
                # Negative: forbidden
                if '403' in responses:
                    case = {
                        **base_case,
                        'test_id': f"TC{id_counter:03d}",
                        'test_name': f"{method.upper()} {endpoint} [negative: forbidden] (TC{id_counter:03d})",
                        'expected_status': '403',
                        'test_type': 'Negative',
                            'test_type': ['Negative'],
                        'forbidden': True
                    }
                    case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                    cases.append(case)
                    id_counter += 1
                # Negative: not found
                if '404' in responses:
                    case = {
                        **base_case,
                        'test_id': f"TC{id_counter:03d}",
                        'test_name': f"{method.upper()} {endpoint} [negative: not found] (TC{id_counter:03d})",
                        'expected_status': '404',
                        'test_type': 'Negative',
                            'test_type': ['Negative'],
                        'not_found': True
                    }
                    case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                    cases.append(case)
                    id_counter += 1
                # Negative: error/validation error
                for err_code in ['422', '500']:
                    if err_code in responses:
                        case = {
                            **base_case,
                            'test_id': f"TC{id_counter:03d}",
                            'test_name': f"{method.upper()} {endpoint} [negative: error {err_code}] (TC{id_counter:03d})",
                            'expected_status': err_code,
                            'test_type': 'Negative',
                                'test_type': ['Negative'],
                            'error_case': err_code
                        }
                        case['test_summary'] = f"Test {case['test_id']}: {case['test_name']}"
                        cases.append(case)
                        id_counter += 1
        logger.info(f"Parsed {len(cases)} test cases from OpenAPI spec.")
        return cases

    def parse_postman(self, postman_path: str) -> List[Dict]:
        from framework.loaders.path_loader import get_project_path
        postman_file_path = get_project_path(*os.path.normpath(postman_path).split(os.sep))
        if not postman_file_path.exists():
            logger.error(f"Postman file not found: {postman_path}")
            raise FileNotFoundError(f"Postman file not found: {postman_path}")
        with open(str(postman_file_path), 'r') as f:
            collection = json.load(f)
        
        # Generate clean service name from collection name and/or file name
        collection_name = collection.get('info', {}).get('name', 'APIService')
        service_name = self._generate_service_name(collection_name, postman_path)
        logger.info(f"Generated service_name: '{service_name}' from collection: '{collection_name}'")
        
        cases = []
        self._extract_postman_items(collection.get('item', []), cases, service_name)
        logger.info(f"Parsed {len(cases)} test cases from Postman collection.")
        return cases

    def _extract_postman_items(self, items: List[Dict], cases: List[Dict], service_name: str):
        for item in items:
            if 'item' in item:
                self._extract_postman_items(item['item'], cases, service_name)
            else:
                request = item.get('request', {})
                endpoint = request.get('url', {}).get('raw', '')
                method = request.get('method', 'GET')
                cases.append({
                    'endpoint': endpoint,
                    'method': method.upper(),
                    'test_name': item.get('name', f'{method.upper()} {endpoint}'),
                    'expected_status': '200',
                        'test_type': ['Functional'],
                    'service_name': service_name
                })

    def fill_template(self, cases: List[Dict], testcase_output_path: str):
        import re
        from pathlib import Path
        from framework.loaders.path_loader import get_project_root
        testcases = []
        for i, case in enumerate(cases, 1):
            tc = self.testcase_template.copy()
            tc.update(case)
            tc['test_id'] = f'TC{i:03d}'
            # Replace any embedded TCxxx in test_name and test_summary with the new test_id
            for field in ['test_name', 'test_summary']:
                if field in tc and isinstance(tc[field], str):
                    # Replace (TCxxx) anywhere in the string
                    tc[field] = re.sub(r'\(TC\d{2,3}\)', f'({tc["test_id"]})', tc[field])
                    # Replace prefix 'Test TCxxx:' with correct test_id
                    tc[field] = re.sub(r'^Test TC\d{2,3}:', f'Test {tc["test_id"]}:', tc[field])
            testcases.append(tc)
        # Only join with project root if not absolute
        output_path_obj = Path(testcase_output_path)
        if not output_path_obj.is_absolute():
            output_path_obj = get_project_root().joinpath(output_path_obj)
        
        # Ensure parent directory exists
        parent_dir = output_path_obj.parent
        parent_dir.mkdir(parents=True, exist_ok=True)
        
        # Truncate filename if path exceeds Windows MAX_PATH
        MAX_PATH = 250  # Use 250 to have buffer
        MAX_FILENAME_LENGTH = 80  # Maximum filename length to avoid issues
        output_path_str = str(output_path_obj)
        filename = output_path_obj.name
        ext = ''.join(pathlib.Path(filename).suffixes)
        base = filename[:-len(ext)] if ext else filename
        
        # Always use shortened filename if original filename is longer than MAX_FILENAME_LENGTH
        if len(filename) > MAX_FILENAME_LENGTH or len(output_path_str) > MAX_PATH:
            import hashlib
            # Create a shorter name with hash
            hash_suffix = hashlib.md5(filename.encode()).hexdigest()[:8]
            # Keep a meaningful prefix
            prefix = base[:30] if len(base) > 30 else base
            new_filename = f"{prefix}_{hash_suffix}{ext}"
            output_path_obj = output_path_obj.parent / new_filename
            output_path_str = str(output_path_obj)
            logger.info(f"Shortened filename: {filename} -> {new_filename}")
        with open(output_path_str, 'w') as f:
            json.dump(testcases, f, indent=4)
        logger.info(f'Generated {len(testcases)} test cases in {output_path_obj}')


    def _create_folder_structure(self, base_dir: pathlib.Path, service_name: str):
        """
        Create standard folder structure for service:
        - service_name/testcases
        - service_name/data_driven
        - service_name/db_queries
        - service_name/payloads
        - service_name/schemas
        """
        folders = ['testcases', 'data_driven', 'db_queries', 'payloads', 'schemas']
        created_folders = []
        
        for folder in folders:
            folder_path = base_dir / service_name / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            created_folders.append(str(folder_path))
            logger.info(f"Created folder: {folder_path}")
        
        return created_folders
    
    def _generate_schema_file(self, case: Dict, schemas_dir: pathlib.Path, endpoint_key: str) -> Optional[str]:
        """
        Generate JSON schema file for test case response validation.
        Returns the relative path to the schema file.
        """
        try:
            # Extract service name and create schema filename
            service_name = case.get('service_name', 'api')
            method = case.get('method', 'GET').upper()
            test_type = case.get('test_type', ['Positive'])
            test_type_str = test_type[0] if isinstance(test_type, list) else test_type
            
            # Generate schema filename - one per endpoint/method combo
            schema_filename = f"Schema_{endpoint_key}.json"
            schema_path = schemas_dir / schema_filename
            
            # Skip if already generated
            if schema_path.exists():
                relative_path = os.path.join(service_name, 'schemas', schema_filename)
                return relative_path
            
            # Create comprehensive JSON schema structure based on method
            if method == 'GET':
                schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "title": f"{method} {case.get('endpoint', '')} Response Schema",
                    "description": f"Response schema for {case.get('endpoint', '')}",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier"},
                        "data": {"type": "object", "description": "Response data object"},
                        "status": {"type": "string", "enum": ["success", "error"]},
                        "message": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    },
                    "required": ["status"]
                }
            elif method in ['POST', 'PUT', 'PATCH']:
                schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "title": f"{method} {case.get('endpoint', '')} Response Schema",
                    "description": f"Response schema for {case.get('endpoint', '')}",
                    "properties": {
                        "id": {"type": "string"},
                        "status": {"type": "string", "enum": ["created", "updated", "success"]},
                        "data": {"type": "object"},
                        "message": {"type": "string"},
                        "createdAt": {"type": "string", "format": "date-time"},
                        "updatedAt": {"type": "string", "format": "date-time"}
                    },
                    "required": ["id", "status"]
                }
            else:  # DELETE, etc.
                schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "title": f"{method} {case.get('endpoint', '')} Response Schema",
                    "description": f"Response schema for {case.get('endpoint', '')}",
                    "properties": {
                        "status": {"type": "string"},
                        "message": {"type": "string"}
                    },
                    "required": ["status"]
                }
            
            # Write schema file
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2)
            
            # Return relative path (OS-appropriate separators)
            relative_path = os.path.join(service_name, 'schemas', schema_filename)
            logger.debug(f"Generated schema: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.warning(f"Failed to generate schema file: {e}")
            return None
    
    def _generate_payload_file(self, case: Dict, payloads_dir: pathlib.Path, endpoint_key: str) -> Optional[str]:
        """
        Generate payload JSON file for test case request body.
        Returns the relative path to the payload file.
        """
        try:
            # Only generate payload for methods that typically have request bodies
            method = case.get('method', 'GET').upper()
            if method in ['GET', 'DELETE', 'HEAD']:
                return None
            
            service_name = case.get('service_name', 'api')
            test_type = case.get('test_type', ['Positive'])
            test_type_str = test_type[0] if isinstance(test_type, list) else test_type
            
            # Generate payload filename - separate for positive/negative
            payload_filename = f"Payload_{endpoint_key}_{test_type_str.lower()}.json"
            payload_path = payloads_dir / payload_filename
            
            # Skip if already generated
            if payload_path.exists():
                relative_path = os.path.join(service_name, 'payloads', payload_filename)
                return relative_path
            
            # Get existing payload or create sample based on method
            payload = case.get('payload', {})
            if not payload or not isinstance(payload, dict):
                # Create method-specific sample payloads
                if method == 'POST':
                    payload = {
                        "name": "Sample Name",
                        "description": "Sample Description",
                        "status": "active",
                        "createdBy": "{{user_id}}",
                        "metadata": {}
                    }
                elif method == 'PUT':
                    payload = {
                        "id": "{{resource_id}}",
                        "name": "Updated Name",
                        "description": "Updated Description",
                        "status": "active",
                        "updatedBy": "{{user_id}}"
                    }
                elif method == 'PATCH':
                    payload = {
                        "status": "updated",
                        "updatedBy": "{{user_id}}"
                    }
            
            # Write payload file
            with open(payload_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            
            # Return relative path (OS-appropriate separators)
            relative_path = os.path.join(service_name, 'payloads', payload_filename)
            logger.debug(f"Generated payload: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.warning(f"Failed to generate payload file: {e}")
            return None
    
    def _generate_test_scenario(self, case: Dict) -> str:
        """
        Generate plain English test scenario description.
        """
        method = case.get('method', 'GET').upper()
        endpoint = case.get('endpoint', '')
        test_type = case.get('test_type', ['Positive'])
        test_type_str = test_type[0] if isinstance(test_type, list) else test_type
        test_name = case.get('test_name', '')
        
        # Extract scenario context
        if 'missing' in test_name.lower():
            param = test_name.split('missing ')[-1].split(']')[0] if 'missing ' in test_name else 'parameter'
            scenario = f"Verify that the API returns a 400 Bad Request error when the required parameter '{param}' is missing from the {method} request to {endpoint}."
        elif 'invalid' in test_name.lower():
            scenario = f"Verify that the API returns a 400 Bad Request error when invalid data is provided in the {method} request to {endpoint}."
        elif 'not found' in test_name.lower():
            scenario = f"Verify that the API returns a 404 Not Found error when requesting a non-existent resource at {endpoint}."
        elif test_type_str.lower() == 'positive':
            scenario = f"Verify that the API successfully processes a valid {method} request to {endpoint} and returns the expected response with a 200 OK status."
        else:
            scenario = f"Test {method} request to {endpoint} for {test_type_str.lower()} scenario validation."
        
        return scenario
    
    def _generate_sample_csv_files(self, data_driven_dir: pathlib.Path, service_name: str, cases: List[Dict]):
        """
        Generate sample CSV files for data-driven testing in data_driven folder.
        """
        try:
            # Create a sample CSV for POST/PUT endpoints
            post_put_cases = [c for c in cases if c.get('method', '').upper() in ['POST', 'PUT', 'PATCH']]
            if post_put_cases:
                csv_path = data_driven_dir / f"Data_{service_name}_sample.csv"
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    f.write("environment,test_id,name,description,status,expected_status\n")
                    f.write("TSADEV,TC001,Sample Name 1,Sample Description 1,active,200\n")
                    f.write("TSADEV,TC002,Sample Name 2,Sample Description 2,inactive,200\n")
                    f.write("TSADEV,TC003,Invalid Name,Invalid Description,invalid_status,400\n")
                logger.debug(f"Generated sample CSV: {csv_path}")
            
            # Create a sample CSV for GET endpoints with parameters
            get_cases = [c for c in cases if c.get('method', '').upper() == 'GET' and '{' in c.get('endpoint', '')]
            if get_cases:
                csv_path = data_driven_dir / f"Data_{service_name}_get_params.csv"
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    f.write("environment,test_id,resource_id,expected_status\n")
                    f.write("TSADEV,TC001,12345,200\n")
                    f.write("TSADEV,TC002,67890,200\n")
                    f.write("TSADEV,TC003,invalid_id,404\n")
                logger.debug(f"Generated GET params CSV: {csv_path}")
                
        except Exception as e:
            logger.warning(f"Failed to generate sample CSV files: {e}")
    
    def _generate_sample_db_queries(self, db_queries_dir: pathlib.Path, service_name: str, cases: List[Dict]):
        """
        Generate sample SQL query files in db_queries folder.
        """
        try:
            # Create sample SELECT query
            select_query_path = db_queries_dir / f"Query_{service_name}_select.sql"
            with open(select_query_path, 'w', encoding='utf-8') as f:
                f.write(f"-- Sample SELECT query for {service_name}\n")
                f.write(f"-- Usage: Verify data retrieved from API matches database\n\n")
                f.write(f"SELECT \n")
                f.write(f"    id,\n")
                f.write(f"    name,\n")
                f.write(f"    description,\n")
                f.write(f"    status,\n")
                f.write(f"    created_date,\n")
                f.write(f"    updated_date\n")
                f.write(f"FROM {service_name}_table\n")
                f.write(f"WHERE id = '{{{{resource_id}}}}'\n")
                f.write(f"    AND status = '{{{{expected_status}}}}'\n")
                f.write(f"ORDER BY created_date DESC;\n")
            logger.debug(f"Generated SELECT query: {select_query_path}")
            
            # Create sample INSERT validation query
            if any(c.get('method', '').upper() == 'POST' for c in cases):
                insert_query_path = db_queries_dir / f"Query_{service_name}_validate_insert.sql"
                with open(insert_query_path, 'w', encoding='utf-8') as f:
                    f.write(f"-- Validate POST/INSERT operation for {service_name}\n")
                    f.write(f"-- Usage: Verify new record was created in database\n\n")
                    f.write(f"SELECT \n")
                    f.write(f"    id,\n")
                    f.write(f"    name,\n")
                    f.write(f"    created_date,\n")
                    f.write(f"    created_by\n")
                    f.write(f"FROM {service_name}_table\n")
                    f.write(f"WHERE name = '{{{{created_name}}}}'\n")
                    f.write(f"    AND created_by = '{{{{user_id}}}}'\n")
                    f.write(f"ORDER BY created_date DESC\n")
                    f.write(f"LIMIT 1;\n")
                logger.debug(f"Generated INSERT validation query: {insert_query_path}")
                
        except Exception as e:
            logger.warning(f"Failed to generate sample DB query files: {e}")

    def generate(self, mode: str, input_file: str, testcase_output_dir: str = None):
        mode = mode.lower()
        if mode == 'openapi':
            cases = self.parse_openapi(input_file)
        elif mode == 'postman':
            cases = self.parse_postman(input_file)
        elif mode == 'wsdl':
            cases = self.parse_wsdl(input_file)
        else:
            logger.error("Mode must be one of: 'openapi', 'postman', 'wsdl'")
            raise ValueError("Invalid mode")

        # Extract service name from first case or use provided testcase_output_dir as service name
        if testcase_output_dir:
            # If provided, treat testcase_output_dir as the service name override
            service_name = testcase_output_dir
            # Also update all cases with the new service name
            for case in cases:
                case['service_name'] = service_name
        else:
            service_name = cases[0].get('service_name', 'api') if cases else 'api'
        
        # Determine base output directory
        from pathlib import Path
        from framework.loaders.path_loader import get_project_root
        
        # Always create under testcases_autogenerated/service_name
        base_output_dir = get_project_root() / 'testcases_autogenerated' / service_name
        
        # Create folder structure
        logger.info(f"Creating folder structure for service: {service_name}")
        # base_output_dir is already testcases_autogenerated/service_name, so use parent (testcases_autogenerated)
        # _create_folder_structure will append service_name again: base_dir / service_name / folder
        service_base = base_output_dir.parent  # testcases_autogenerated/
        self._create_folder_structure(service_base, service_name)
        
        # Set up directories
        testcases_dir = base_output_dir / 'testcases'
        schemas_dir = base_output_dir / 'schemas'
        payloads_dir = base_output_dir / 'payloads'
        
        # Group cases by endpoint and method
        from collections import defaultdict
        import re
        endpoint_groups = defaultdict(list)
        
        for case in cases:
            endpoint = str(case.get('endpoint', '')).strip('/').replace('/', '_').replace('{', '').replace('}', '')
            method = str(case.get('method', '')).upper()
            key = f"{endpoint}_{method}"
            # Sanitize key for Windows filenames
            key = re.sub(r'[:\\/*?"<>|]', '_', key)
            
            # Generate schema and payload files
            schema_path = self._generate_schema_file(case, schemas_dir, key)
            if schema_path:
                # Normalize path for cross-platform compatibility
                case['expected_response_schema'] = normalize_path(schema_path)
            
            payload_path = self._generate_payload_file(case, payloads_dir, key)
            if payload_path and case.get('method', 'GET').upper() in ['POST', 'PUT', 'PATCH']:
                # Store payload file reference instead of inline payload (normalize for cross-platform)
                case['payload_file'] = normalize_path(payload_path)
            
            # Generate test scenario
            case['test_scenario'] = self._generate_test_scenario(case)
            
            # Enhance test_summary with more details
            case['test_summary'] = f"Test {case.get('test_id')}: {case.get('test_name')} - {case['test_scenario']}"
            
            endpoint_groups[key].append(case)

        # Write each group to a separate file in testcases folder
        for key, group_cases in endpoint_groups.items():
            output_path = str(testcases_dir / f"TestCase_{key}.json")
            self.fill_template(group_cases, output_path)
        
        # Generate sample CSV files for data-driven testing
        data_driven_dir = base_output_dir / 'data_driven'
        self._generate_sample_csv_files(data_driven_dir, service_name, cases)
        
        # Generate sample DB query files
        db_queries_dir = base_output_dir / 'db_queries'
        self._generate_sample_db_queries(db_queries_dir, service_name, cases)
        
        # Count generated files
        schema_count = len(list(schemas_dir.glob('*.json')))
        payload_count = len(list(payloads_dir.glob('*.json')))
        csv_count = len(list(data_driven_dir.glob('*.csv')))
        sql_count = len(list(db_queries_dir.glob('*.sql')))
        total_test_cases = len(cases)
        
        logger.info(f"[SUCCESS] Generated {len(endpoint_groups)} test case files in {testcases_dir}")
        logger.info(f"[SUCCESS] Generated {schema_count} schema files in {schemas_dir}")
        logger.info(f"[SUCCESS] Generated {payload_count} payload files in {payloads_dir}")
        logger.info(f"[SUCCESS] Generated {csv_count} CSV files in {data_driven_dir}")
        logger.info(f"[SUCCESS] Generated {sql_count} SQL query files in {db_queries_dir}")
        logger.info(f"[SUCCESS] Folder structure created: testcases, data_driven, db_queries, payloads, schemas")
        
        # Summary message with folder name and test case count
        summary_msg = f"\n{'='*80}\n[GENERATION SUMMARY]\nFolder: {service_name}\nTotal Test Cases: {total_test_cases}\nTest Case Files: {len(endpoint_groups)}\nSchema Files: {schema_count}\nPayload Files: {payload_count}\nCSV Files: {csv_count}\nSQL Files: {sql_count}\nOutput Directory: {base_output_dir}\n{'='*80}"
        print(summary_msg)
        logger.info(summary_msg)

if __name__ == '__main__':
        if len(sys.argv) not in (3, 4):
            from framework.common.logger import get_logger
            logger = get_logger(__name__)
            logger.info("Usage: python generate_testcases.py <openapi|postman|wsdl> <input_file> [<service_name>]")
            logger.info("Example: python generate_testcases.py openapi https://api.example.com/swagger.json work_item_notification")
            sys.exit(1)
        mode = sys.argv[1]
        input_file = sys.argv[2]
        testcase_output_dir = sys.argv[3] if len(sys.argv) == 4 else None
        
        generator = TestCaseGenerator()
        generator.generate(mode, input_file, testcase_output_dir)
