
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
                    
                    # Extract parameter names from WSDL operation input
                    param_names = []
                    try:
                        elements = getattr(op.input.body.type, 'elements', [])
                        param_names = [name for name, element in elements]
                        if len(param_names) > 0:
                            logger.info(f"Operation {op.name}: Extracted {len(param_names)} parameters: {param_names}")
                    except Exception as e:
                        logger.warning(f"Failed to extract parameters for {op.name}: {e}")
                    
                    # Generate a sample soap_envelope with actual parameter names
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
                    
                    # Extract path from endpoint_address URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(endpoint_address)
                    endpoint_path = parsed_url.path if parsed_url.path else ""
                    
                    case = {
                        'test_id': f"TC{id_counter:03d}",
                        'service_name': service_name,
                        'port_name': port.name,
                        'test_name': f"{op.name} [WSDL] (TC{id_counter:03d})",
                        'test_summary': f"Test TC{id_counter:03d}: {op.name} operation on {service.name}/{port.name}",
                        'protocol': 'SOAP',
                        'endpoint': endpoint_path,
                        'method': 'POST',
                        'wsdl_operation': op.name,
                        'soap_action': soap_action,
                        'soap_envelope': soap_envelope,
                        'headers_additional': {
                            'Content-Type': 'text/xml; charset=utf-8'
                        },
                        'expected_status': '200',
                        'test_type': ['Functional'],
                        '_wsdl_params': param_names  # Internal use only for CSV/payload generation
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

    def fill_template(self, cases: List[Dict], testcase_output_path: str, mode: str = 'openapi'):
        import re
        from pathlib import Path
        from framework.loaders.path_loader import get_project_root
        testcases = []
        for i, case in enumerate(cases, 1):
            tc = self.testcase_template.copy()
            
            tc.update(case)
            
            # Remove internal fields that shouldn't be in final test case
            if '_wsdl_params' in tc:
                del tc['_wsdl_params']
            
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
        Generate schema file for test case response validation.
        For SOAP: Generate XSD files
        For REST: Generate JSON schema files
        Returns the relative path to the schema file.
        """
        try:
            # Extract service name and create schema filename
            service_name = case.get('service_name', 'api')
            method = case.get('method', 'GET').upper()
            protocol = case.get('protocol', '').upper()
            test_type = case.get('test_type', ['Positive'])
            test_type_str = test_type[0] if isinstance(test_type, list) else test_type
            
            # For SOAP, generate XSD schema files
            if protocol == 'SOAP':
                schema_filename = f"Schema_{endpoint_key}.xsd"
                schema_path = schemas_dir / schema_filename
                
                # Skip if already generated
                if schema_path.exists():
                    relative_path = os.path.join(service_name, 'schemas', schema_filename)
                    return relative_path
                
                # Generate basic XSD schema template for SOAP response
                operation = case.get('wsdl_operation', 'Operation')
                xsd_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:tns="http://tempuri.org/"
           targetNamespace="http://tempuri.org/"
           elementFormDefault="qualified">
  
  <!-- Response element for {operation} operation -->
  <xs:element name="{operation}Response">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="{operation}Result" type="xs:string" minOccurs="0"/>
        <!-- Add additional response elements here -->
      </xs:sequence>
    </xs:complexType>
  </xs:element>
  
  <!-- Common types -->
  <xs:complexType name="ResponseType">
    <xs:sequence>
      <xs:element name="Status" type="xs:string"/>
      <xs:element name="Message" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  
</xs:schema>'''
                
                # Write XSD schema file
                with open(schema_path, 'w', encoding='utf-8') as f:
                    f.write(xsd_content)
                
                # Return relative path
                relative_path = os.path.join(service_name, 'schemas', schema_filename)
                logger.debug(f"Generated SOAP XSD schema: {relative_path}")
                return relative_path
            
            # For REST APIs, generate JSON schema files
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
        Generate payload file for test case request body.
        For SOAP: Generate .xml files with SOAP envelope templates
        For REST: Generate .json files
        Returns the relative path to the payload file.
        """
        try:
            # Only generate payload for methods that typically have request bodies
            method = case.get('method', 'GET').upper()
            if method in ['GET', 'DELETE', 'HEAD']:
                return None
            
            service_name = case.get('service_name', 'api')
            protocol = case.get('protocol', '').upper()
            test_type = case.get('test_type', ['Positive'])
            test_type_str = test_type[0] if isinstance(test_type, list) else test_type
            
            # For SOAP, generate XML envelope files
            if protocol == 'SOAP':
                payload_filename = f"Payload_{endpoint_key}_envelope.xml"
                payload_path = payloads_dir / payload_filename
                
                # Skip if already generated
                if payload_path.exists():
                    relative_path = os.path.join(service_name, 'payloads', payload_filename)
                    return relative_path
                
                # Extract soap_envelope from case (generated by Zeep from WSDL)
                soap_envelope = case.get('soap_envelope', '')
                
                # Get actual parameter names from WSDL
                wsdl_params = case.get('_wsdl_params', [])
                operation = case.get('wsdl_operation', 'Operation')
                
                # Generate SOAP envelope with actual parameter names as template variables
                from lxml import etree
                
                if wsdl_params:
                    # Build envelope with actual parameter names
                    param_elements = '\n'.join([f"      <tem:{param}>{{{{{param}}}}}</tem:{param}>" for param in wsdl_params])
                    payload_content = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
  <soapenv:Header/>
  <soapenv:Body>
    <tem:{operation}>
{param_elements}
    </tem:{operation}>
  </soapenv:Body>
</soapenv:Envelope>'''
                else:
                    # Fallback: try to parse the soap_envelope and extract parameter names
                    soap_envelope = case.get('soap_envelope', '')
                    if soap_envelope and soap_envelope != '<Envelope>...</Envelope>':
                        try:
                            # Parse the SOAP envelope
                            root = etree.fromstring(soap_envelope.encode('utf-8'))
                            
                            # Find all elements in the Body and replace text content with template variables
                            namespaces = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/'}
                            body = root.find('.//soapenv:Body', namespaces)
                            
                            if body is not None:
                                # Find all leaf elements (elements with text content)
                                for elem in body.iter():
                                    if elem.text and elem.text.strip() and len(list(elem)) == 0:
                                        # Extract parameter name from tag (remove namespace)
                                        tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                                        # Replace value with template variable
                                        elem.text = f"{{{{{tag_name}}}}}"
                            
                            # Convert back to string
                            payload_content = etree.tostring(root, pretty_print=True, encoding='unicode')
                        except Exception as e:
                            logger.warning(f"Failed to parse SOAP envelope for {endpoint_key}: {e}")
                            # Final fallback to generic template
                            payload_content = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
  <soapenv:Header/>
  <soapenv:Body>
    <tem:{operation}>
      <tem:parameter1>{{{{parameter1}}}}</tem:parameter1>
      <tem:parameter2>{{{{parameter2}}}}</tem:parameter2>
    </tem:{operation}>
  </soapenv:Body>
</soapenv:Envelope>'''
                    else:
                        # Generate basic SOAP template if no envelope provided
                        payload_content = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
  <soapenv:Header/>
  <soapenv:Body>
    <tem:{operation}>
      <tem:parameter1>{{{{parameter1}}}}</tem:parameter1>
      <tem:parameter2>{{{{parameter2}}}}</tem:parameter2>
    </tem:{operation}>
  </soapenv:Body>
</soapenv:Envelope>'''
                
                # Write XML payload file
                with open(payload_path, 'w', encoding='utf-8') as f:
                    f.write(payload_content)
                
                # Return relative path
                relative_path = os.path.join(service_name, 'payloads', payload_filename)
                logger.debug(f"Generated SOAP XML payload: {relative_path}")
                return relative_path
            
            # For REST APIs, generate JSON payloads
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
        For SOAP operations, creates CSV files with operation-specific parameters.
        Returns a dict mapping CSV filenames to list of operations.
        """
        csv_param_map = {}
        try:
            # Create sample CSV for SOAP operations (check protocol field, not method)
            soap_cases = [c for c in cases if c.get('protocol', '').upper() == 'SOAP']
            logger.info(f"Found {len(soap_cases)} SOAP test cases for CSV generation")
            if soap_cases:
                # Group operations with similar parameters to reduce CSV files
                param_groups = {}
                for case in soap_cases:
                    # PRIORITY 1: Get parameters from _wsdl_params (extracted from WSDL)
                    param_names = case.get('_wsdl_params', [])
                    operation_name = case.get('wsdl_operation', 'Unknown')
                    logger.info(f"Processing operation {operation_name}: _wsdl_params = {param_names}")
                    
                    # PRIORITY 2: If _wsdl_params not available, try extracting from soap_envelope (already normalized path)
                    if not param_names:
                        soap_envelope = case.get('soap_envelope', '')
                        if soap_envelope:
                            # soap_envelope is now a relative path like "platform_service7\\payloads\\Payload_xxx.xml"
                            # We need to construct full path from data_driven_dir parent
                            import re
                            if soap_envelope.endswith('.xml'):
                                # It's a file path, read the file
                                try:
                                    # data_driven_dir is base_output_dir/data_driven
                                    # We need base_output_dir (parent)
                                    xml_path = data_driven_dir.parent / soap_envelope
                                    if xml_path.exists():
                                        with open(xml_path, 'r', encoding='utf-8') as f:
                                            xml_content = f.read()
                                        template_vars = re.findall(r'\{\{(\w+)\}\}', xml_content)
                                        param_names = [v for v in template_vars if v not in ['environment', 'test_id']]
                                        logger.debug(f"Extracted {len(param_names)} params from XML: {param_names}")
                                    else:
                                        logger.debug(f"XML file not found (will be created): {xml_path}")
                                except Exception as e:
                                    logger.warning(f"Failed to read XML file {soap_envelope}: {e}")
                            elif not soap_envelope.startswith('<'):
                                # Not XML content and doesn't end with .xml, skip
                                logger.debug(f"Unexpected soap_envelope format: {soap_envelope}")
                            else:
                                # It's inline XML content, extract template variables
                                template_vars = re.findall(r'\{\{(\w+)\}\}', soap_envelope)
                                param_names = [v for v in template_vars if v not in ['environment', 'test_id']]
                    
                    # Create grouping key from parameter names
                    param_key = tuple(sorted(param_names)) if param_names else tuple()
                    
                    # Group operations - even if param_key is empty, we still want to generate a CSV
                    if param_key not in param_groups:
                        param_groups[param_key] = []
                    param_groups[param_key].append(case.get('wsdl_operation', case.get('operation', 'Unknown')))
                
                # Generate CSV for each parameter group (including operations with no parameters)
                for idx, (params, operations) in enumerate(param_groups.items(), 1):
                    # Create meaningful filename from operation names
                    # Use first operation name, or combine if only 2 operations, else use first + count
                    if len(operations) == 1:
                        operation_part = operations[0]
                    elif len(operations) == 2:
                        operation_part = '_'.join(operations)
                    else:
                        operation_part = f"{operations[0]}_and_{len(operations)-1}_others"
                    
                    # Sanitize operation name for filename (remove special chars, limit length)
                    import re
                    operation_part = re.sub(r'[^\w\s-]', '', operation_part)
                    operation_part = re.sub(r'[-\s]+', '_', operation_part)
                    # Limit total filename length to avoid Windows MAX_PATH issues
                    max_operation_length = 80 - len(f"Data_{service_name}_.csv")
                    if len(operation_part) > max_operation_length:
                        operation_part = operation_part[:max_operation_length]
                    
                    csv_filename = f"Data_{service_name}_{operation_part}.csv"
                    csv_path = data_driven_dir / csv_filename
                    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                        if params:
                            # Header: environment, test_id, then operation-specific params, expected_status
                            headers = ['environment', 'test_id'] + list(params) + ['expected_status']
                            f.write(','.join(headers) + '\n')
                            
                            # Sample data rows
                            f.write('TSADEV,TC001,' + ','.join(['sample_value'] * len(params)) + ',200\n')
                            f.write('TSADEV,TC002,' + ','.join(['sample_value_2'] * len(params)) + ',200\n')
                            f.write('TSADEV,TC003,' + ','.join(['invalid_value'] * len(params)) + ',500\n')
                        else:
                            # Operations with no parameters - create minimal CSV
                            headers = ['environment', 'test_id', 'expected_status']
                            f.write(','.join(headers) + '\n')
                            f.write('TSADEV,TC001,200\n')
                            f.write('TSADEV,TC002,200\n')
                            f.write('TSADEV,TC003,500\n')
                    
                    logger.info(f"Generated SOAP CSV for {len(operations)} operations ({', '.join(operations[:3])}{'...' if len(operations) > 3 else ''}): {csv_path}")
                    # Store mapping of CSV file to operations
                    csv_param_map[csv_filename] = operations
            
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
        
        return csv_param_map
    
    def _generate_sample_db_queries(self, db_queries_dir: pathlib.Path, service_name: str, cases: List[Dict]):
        """
        Generate sample SQL query files in db_queries folder.
        Creates placeholder queries for SOAP and REST operations.
        """
        try:
            # Create SQL queries for SOAP operations
            soap_cases = [c for c in cases if c.get('method', '').upper() == 'SOAP']
            if soap_cases:
                for case in soap_cases[:5]:  # Limit to first 5 operations to avoid too many files
                    operation = case.get('wsdl_operation', case.get('operation', 'Unknown'))
                    sql_path = db_queries_dir / f"Query_{operation}_validate.sql"
                    if sql_path.exists():
                        continue
                    with open(sql_path, 'w', encoding='utf-8') as f:
                        f.write(f"-- Validation query for SOAP operation: {operation}\n")
                        f.write(f"-- Service: {service_name}\n")
                        f.write(f"-- Usage: Verify SOAP operation result against database\n\n")
                        f.write(f"SELECT \n")
                        f.write(f"    id,\n")
                        f.write(f"    name,\n")
                        f.write(f"    status,\n")
                        f.write(f"    last_modified_date\n")
                        f.write(f"FROM {service_name}_table\n")
                        f.write(f"WHERE id = '{{{{record_id}}}}'\n")
                        f.write(f"    AND status = 'active'\n")
                        f.write(f"ORDER BY last_modified_date DESC;\n")
                    logger.debug(f"Generated SOAP SQL query: {sql_path}")
            
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
            protocol = str(case.get('protocol', '')).upper()
            
            # For SOAP/WSDL, use operation name instead of full endpoint URL
            if protocol == 'SOAP' and 'wsdl_operation' in case:
                key = f"{case['wsdl_operation']}_{method}"
            else:
                key = f"{endpoint}_{method}"
            
            # Sanitize key for Windows filenames
            key = re.sub(r'[:\\/*?"<>|]', '_', key)
            
            # Generate schema and payload files
            schema_path = self._generate_schema_file(case, schemas_dir, key)
            if schema_path:
                # Normalize path for cross-platform compatibility (works for both .xsd and .json)
                case['expected_response_schema'] = normalize_path(schema_path)
            
            payload_path = self._generate_payload_file(case, payloads_dir, key)
            if payload_path:
                method = case.get('method', 'GET').upper()
                protocol = case.get('protocol', '').upper()
                if method in ['POST', 'PUT', 'PATCH'] and protocol != 'SOAP':
                    # Store payload file reference instead of inline payload (normalize for cross-platform)
                    case['payload_file'] = normalize_path(payload_path)
                elif protocol == 'SOAP':
                    # Store XML file path in soap_envelope
                    case['soap_envelope'] = normalize_path(payload_path)
            
            endpoint_groups[key].append(case)

        # Generate sample CSV files for data-driven testing AFTER payload files are created
        # This ensures XML envelope files exist for parameter extraction
        data_driven_dir = base_output_dir / 'data_driven'
        csv_param_map = self._generate_sample_csv_files(data_driven_dir, service_name, cases)
        
        # Map CSV files to SOAP test cases based on parameters
        if mode == 'wsdl' and csv_param_map:
            for case in cases:
                if case.get('method', '').upper() == 'SOAP':
                    wsdl_op = case.get('wsdl_operation', '')
                    # Find matching CSV file based on operation
                    for csv_file, operations in csv_param_map.items():
                        if wsdl_op in operations:
                            # Set test_data_file with relative path
                            case['test_data_file'] = normalize_path(f"{service_name}/data_driven/{csv_file}")
                            break

        # Write each group to a separate file in testcases folder
        for key, group_cases in endpoint_groups.items():
            output_path = str(testcases_dir / f"TestCase_{key}.json")
            self.fill_template(group_cases, output_path, mode=mode)
        
        # Generate sample DB query files
        db_queries_dir = base_output_dir / 'db_queries'
        self._generate_sample_db_queries(db_queries_dir, service_name, cases)
        
        # Count generated files
        schema_count = len(list(schemas_dir.glob('*.json'))) + len(list(schemas_dir.glob('*.xsd')))
        payload_count = len(list(payloads_dir.glob('*.json'))) + len(list(payloads_dir.glob('*.xml')))
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
