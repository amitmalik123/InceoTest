import json
import os
import glob
from typing import List, Dict, Optional
from framework.common.logger import get_logger

logger = get_logger(__name__)

class TestCaseLoader:
    def __init__(self, testcase_file: Optional[str] = None):
        """
        Initialize the loader with a file pattern or specific file.
        If no file is provided, defaults to 'testdata/TestCase*.json'.
        """
        self.testcase_pattern = testcase_file or os.path.join('testdata', 'TestCase*.json')

    def load(self) -> List[Dict]:
        """
        Load and parse all matching test case files.
        Returns a list of validated test case dictionaries.
        """
        files = glob.glob(self.testcase_pattern)
        if not files:
            logger.warning(f"No test case files found matching: {self.testcase_pattern}")
            return []

        all_cases = []
        seen_ids = set()

        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Support new structure: top-level test_data_file and testcases array
                    if isinstance(data, dict) and 'testcases' in data:
                        cases = data['testcases']
                    elif isinstance(data, list):
                        cases = data
                    else:
                        logger.warning(f"Unexpected format in {file}, skipping.")
                        continue

                    for case in cases:
                        if not isinstance(case, dict):
                            logger.warning(f"Invalid test case format in {file}, skipping entry.")
                            continue

                        case_id = case.get('id') or case.get('name') or case.get('test_id') or case.get('test_name')
                        if not case_id:
                            logger.warning(f"Test case missing identifier (id/name/test_id/test_name) in {file}, skipping.")
                            continue

                        if case_id in seen_ids:
                            logger.debug(f"Duplicate test case '{case_id}' skipped.")
                            continue

                        case['source_file'] = file
                        all_cases.append(case)
                        seen_ids.add(case_id)

                    logger.info(f"Loaded {len(cases)} test cases from {file}")

            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

        logger.info(f"Total test cases loaded: {len(all_cases)}")
        return all_cases
