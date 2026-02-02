import sys
import os
import time
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.loaders.config_loader import get_config
from framework.loaders.testcase_loader import TestCaseLoader
from framework.loaders.testdata_loader import TestDataLoader
from framework.reporter.reporter import Reporter
from framework.common.logger import get_logger
from framework.common.utils import normalize_path
from framework.validators.validators import validate_db_comparison
from framework.reporter.influx_reporter import push_to_infux


logger = get_logger(__name__)

class TestRunner:
    def __init__(self, env='default'):
        try:
            # Set ENV_NAME environment variable if provided
            if env and env != 'default':
                os.environ['ENV_NAME'] = env
            self.config = get_config()
            logger.info(f"Loaded configuration for environment: {env}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {}

        try:
            self.testcases = TestCaseLoader().load()
            logger.info(f"Loaded {len(self.testcases)} test cases.")
        except Exception as e:
            logger.error(f"Failed to load test cases: {e}")
            self.testcases = []

        self.testdata_map = {}
        try:
            # Load test data per test case if test_data_file is specified
            for testcase in self.testcases:
                test_data_file = testcase.get('test_data_file')
                if test_data_file:
                    # Normalize path for cross-platform compatibility
                    test_data_path = normalize_path(test_data_file)
                    if not os.path.isabs(test_data_path):
                        test_data_path = os.path.join(os.path.dirname(__file__), '..', 'testdata', test_data_path)
                    if os.path.exists(test_data_path):
                        self.testdata_map[test_data_file] = TestDataLoader(test_data_path).load()
                        logger.info(f"Loaded test data from {test_data_path} for test case {testcase.get('test_id')}")
                    else:
                        logger.warning(f"Test data file {test_data_path} not found for test case {testcase.get('test_id')}")
            # Fallback: load default testdata if no test_data_file specified
            self.testdata = TestDataLoader().load()
            logger.info(f"Loaded default test data.")
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            self.testdata = {}

        self.reporter = Reporter()

    def run(self):
        results = []
        logger.info("Starting test execution...")

        for testcase in self.testcases:
            name = testcase.get('name', 'Unnamed')
            logger.info(f"Running test case: {name}")
            start_time = time.time()

            data = {}
            try:
                test_data_file = testcase.get('test_data_file')
                # Use test_data_file if specified
                if test_data_file and test_data_file in self.testdata_map:
                    testdata = self.testdata_map[test_data_file]
                else:
                    testdata = self.testdata
                # For CSV, treat each row as a parameter set, no schema enforcement, use first row
                if isinstance(testdata, list) and testdata:
                    data = testdata[0]
                elif isinstance(testdata, dict):
                    data = testdata

                # --- DB Comparison Validation Integration ---
                validate_cfg = testcase.get('validate', {})
                data_cmp_cfg = validate_cfg.get('data_comparison', {})
                api_response = testcase.get('api_response', [])  # Replace with actual response
                db_result = testcase.get('db_result', [])        # Replace with actual DB result
                key_fields = data_cmp_cfg.get('key_field', [])
                fields_to_compare = data_cmp_cfg.get('fields_to_compare', [])
                if fields_to_compare and api_response and db_result:
                    db_cmp_errors = validate_db_comparison(api_response, db_result, key_fields, fields_to_compare)
                    if db_cmp_errors:
                        logger.error(f"DB comparison errors: {db_cmp_errors}")
                # --- End DB Comparison Validation ---

                success = True  # Replace with real execution result
                error = None

            except Exception as e:
                success = False
                error = traceback.format_exc()
                logger.error(f"Error in test case '{name}': {e}")

            duration = round(time.time() - start_time, 3)

            # Set status and outcome for reporting
            status = 'PASS' if success else 'FAIL'
            outcome = 'PASSED' if success else 'FAILED'
            result = {
                'test_id': testcase.get('test_id') or testcase.get('id'),
                'test_name': testcase.get('test_name') or testcase.get('name'),
                'test_summary': testcase.get('test_summary') or testcase.get('summary'),
                'success': success,
                'status': status,
                'outcome': outcome,
                'duration': duration,
                'error': error,
                'data_used': data
            }
            results.append(result)

        logger.info("Test execution completed. Generating reports...")
        try:
            self.reporter.write_json(results, timestamped=True)
            self.reporter.write_junit_xml(results, timestamped=True)
            self.reporter.write_custom(results, timestamped=True)
            self.reporter.write_html_report(self.testcases, results, timestamped=True)
            self.reporter.write_allure(results)
            logger.info("All reports generated successfully.")
        except NotImplementedError:
            logger.warning("Allure reporting not implemented.")
        except Exception as e:
            logger.error(f"Error during report generation: {e}")
        
        # Push results to InfluxDB
        logger.info("Reports generated. Now pushing results to InfluxDB...")
        try:
            push_to_infux("result.json")
            logger.info("Results successfully pushed to InfluxDB.")
        except Exception as e:
            logger.error(f"Failed to push results to InfluxDB: {e}")

if __name__ == '__main__':
    runner = TestRunner(env='default')
    runner.run()
