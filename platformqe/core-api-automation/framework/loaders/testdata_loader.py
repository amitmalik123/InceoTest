import json
import os
import glob
import yaml
import csv
import concurrent.futures
import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Union


def resolve_testcase_path(attr_value, base_dir=None):
    """
    Resolve and normalize path for cross-platform compatibility.
    Converts any path separator (\\, /, or mixed) to OS-appropriate format.
    
    Args:
        attr_value: Path string with any separator format
        base_dir: Optional base directory to resolve relative paths
    
    Returns:
        Normalized path with OS-appropriate separators
    """
    if not attr_value or not isinstance(attr_value, str):
        return attr_value
    
    # Normalize all separators to OS-appropriate format
    path = attr_value.replace('\\', os.sep).replace('/', os.sep)
    
    # Dynamically determine base_dir from path if not provided
    if not base_dir:
        # Use first segment as base_dir if path is relative and has a directory
        segments = path.split(os.sep)
        if len(segments) > 1:
            base_dir = segments[0]
    
    # Remove leading base_dir if present
    if base_dir and path.lower().startswith(base_dir.lower() + os.sep):
        path = path[len(base_dir) + 1:]
    elif base_dir and path.lower().startswith(base_dir.lower()):
        path = path[len(base_dir):]
    
    path = path.lstrip(os.sep)
    
    if base_dir:
        path = os.path.join(base_dir, path)
    
    return os.path.normpath(path)

try:
    from faker import Faker
    faker = Faker()
except ImportError:
    faker = None

from framework.common.logger import get_logger
logger = get_logger(__name__)

class TestDataLoader:
    __test__ = False  # Prevent pytest from collecting this class as a test
    """
    Loads test data files from the testdata directory.
    Supports JSON, YAML, CSV formats and runtime data generation via Faker.
    """
    def __init__(self, testdata_file: Optional[str] = None, data_dir: str = 'testdata'):
        self.testdata_file = testdata_file
        self.data_dir = data_dir
        self.registry = defaultdict(list)
        self.plugins = {
            '.json': self._load_json,
            '.yaml': self._load_yaml,
            '.yml': self._load_yaml,
            '.csv': self._load_csv
        }

    def _load_json(self, file: str) -> Union[List[Dict], Dict]:
        logger.info(f"Loading JSON test data from: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {file}: {e}")
            return []

    def _load_yaml(self, file: str) -> Union[List[Dict], Dict]:
        logger.info(f"Loading YAML test data from: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading YAML from {file}: {e}")
            return []

    def _load_csv(self, file: str) -> List[Dict]:
            logger.info(f"Loading CSV test data from: {file}")
            
            # Force file system read from disk (not cache) - critical for Docker/pipeline
            import os
            # Force file system read from disk (not cache) - critical for Docker/pipeline
            try:
                if os.name == 'posix':  # Linux/Mac
                    import subprocess
                    subprocess.run(['sync'], check=False, timeout=5)
            except Exception as e:
                logger.debug(f"OS cache clear (non-blocking): {e}")
            
            try:
                with open(file, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    rows = []
                    for row in reader:
                        # Strip whitespace from keys and values, handle None and empty strings
                        clean_row = {}
                        for k, v in row.items():
                            key = k.strip() if k else k
                            if v is None or v == '':
                                value = ''
                            elif isinstance(v, str):
                                value = v.strip()
                                # Auto-parse JSON arrays/objects in CSV cells
                                if value and (value.startswith('[') or value.startswith('{')):
                                    try:
                                        value = json.loads(value)
                                        logger.debug(f"Parsed JSON in CSV cell for key '{key}': {value}")
                                    except json.JSONDecodeError:
                                        # Not valid JSON, keep as string
                                        pass
                                # Auto-split pipe-delimited strings into arrays
                                elif value and '|' in value:
                                    value = [item.strip() for item in value.split('|')]
                                    logger.debug(f"Split pipe-delimited value for key '{key}': {value}")
                            else:
                                value = v
                            clean_row[key] = value
                        rows.append(clean_row)
                    logger.info(f"Loaded {len(rows)} rows from CSV")
                    return rows
            except Exception as e:
                logger.error(f"Error loading CSV from {file}: {e}")
                return []

    def _generate_runtime_data(self, template: Dict) -> Dict:
        if not faker:
            raise ImportError("Faker is not installed. Please install it for runtime data generation.")
        generated = {}
        for k, v in template.items():
            if isinstance(v, str) and v.startswith('faker.'):
                method = v.split('.', 1)[1]
                try:
                    generated[k] = getattr(faker, method)()
                except Exception as e:
                    logger.warning(f"Faker method '{method}' failed: {e}")
                    generated[k] = None
            else:
                generated[k] = v
        return generated

    def _filter_data(self, data: List[Dict], tags: Optional[List[str]] = None, version: Optional[str] = None, **kwargs) -> List[Dict]:
        filtered = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            if tags:
                entry_tags = entry.get('tags', [])
                if not set(tags).intersection(set(entry_tags)):
                    continue
            if version and entry.get('version') != version:
                continue
            # Remove any test_id-based filtering; treat each row as a parameter set
            filtered.append(entry)
        logger.info(f"Filtered down to {len(filtered)} entries based on tags/version only.")
        return filtered

    def _load_file(self, file: str) -> List[Dict]:
        ext = os.path.splitext(file)[1].lower()
        loader = self.plugins.get(ext)
        if not loader:
            logger.warning(f"No loader for file type: {ext}, skipping {file}")
            return []

        try:
            data = loader(file)
            if isinstance(data, dict) and data.get('runtime_generate'):
                template = data['runtime_generate']
                count = data.get('generate_count', 1)
                data = [self._generate_runtime_data(template) for _ in range(count)]

            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict):
                        entry['__source_file'] = file
                return data
            elif isinstance(data, dict):
                data['__source_file'] = file
                return [data]
            else:
                logger.warning(f"Unexpected data format in {file}, skipping.")
                return []
        except Exception as e:
            logger.error(f"Error loading file {file}: {e}")
            return []

    def load(self, tags: Optional[List[str]] = None, version: Optional[str] = None, parallel: bool = False, **kwargs) -> List[Dict]:
        # Only load the file specified in test_data_file
        if self.testdata_file is None or self.testdata_file == "":
            # Only log error if test_data_file is required for this test case (e.g., data-driven)
            # If not required, just return empty without error
            return []


        # Centralized path resolution for test_data_file and other file attributes
        # Dynamically resolve path for test_data_file
        resolved_path = resolve_testcase_path(self.testdata_file)
        # Only prepend self.data_dir if not already present
        if not os.path.isabs(resolved_path):
            if not resolved_path.lower().startswith(self.data_dir.lower() + os.sep):
                resolved_path = os.path.join(self.data_dir, resolved_path)
        resolved_path = os.path.normpath(resolved_path)
        if not os.path.exists(resolved_path):
            error_msg = f"Test data file not found: {os.path.abspath(resolved_path)}. Test FAIL."
            logger.error(error_msg)
            # Return a dummy row with error marker so only this test fails
            return [{
                "__testdata_error__": True,
                "__error_message__": error_msg
            }]

        # Example: Centralized path resolution for other attributes (extend as needed)
        # If you want to resolve other file attributes, use:
        # case['expected_response_schema'] = resolve_testcase_path(case.get('expected_response_schema'), 'workitemnotification/schemas')
        # case['expected_response'] = resolve_testcase_path(case.get('expected_response'), 'WorkItemNotification/payloads')
        # case['payload'] = resolve_testcase_path(case.get('payload'), 'WorkItemNotification/payloads')

        ext = os.path.splitext(resolved_path)[1].lower()
        loader = self.plugins.get(ext)
        if not loader:
            logger.error(f"No loader for file type: {ext}. Test FAIL.")
            raise ValueError(f"No loader for file type: {ext}")

        data = loader(resolved_path)

        # Filter by environment value from .env (ENV_NAME)
        env_name = os.environ.get('ENV_NAME')
        if env_name:
            filtered_data = []
            for entry in data:
                # CSV: 'environment' column; JSON/YAML: 'environment' key
                entry_env = entry.get('environment')
                if entry_env == env_name:
                    filtered_data.append(entry)
            data = filtered_data
            logger.info(f"Filtered test data by ENV_NAME={env_name}, remaining entries: {len(data)}")

        if tags or version or kwargs:
            data = self._filter_data(data, tags=tags, version=version, **kwargs)

        for entry in data:
            src = entry.get('__source_file', 'unknown')
            self.registry[src].append(entry)

        logger.info(f"Total test data entries loaded: {len(data)}")
        return data

    def get_registry(self) -> Dict[str, List[Dict]]:
        return dict(self.registry)
