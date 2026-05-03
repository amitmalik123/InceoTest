"""
Locust Performance Testing - Integrated with Framework Components

This locustfile uses the centralized framework infrastructure:

Framework Components Used:
- framework.common.logger: Centralized logging with LOG_LEVEL support
- framework.common.template_utils: Template rendering (Jinja2 + placeholders)
- framework.loaders.path_loader: Cross-platform path resolution
- framework.loaders.config_loader: Environment-specific config management
- framework.loaders.testcase_loader: JSON testcase loading with glob support
- framework.loaders.testdata_loader: CSV/JSON/YAML data loading with env filtering
- framework.clients.api_client: HTTP client with SSL verification disabled (verify=False)
- framework.validators.validators: Response validation (status code, schema, fields)
- framework.test_helpers.test_result_collector: Result collection for reporting
- framework.reporter.influx_reporter: InfluxDB metrics pushing (when enabled)

Validation Levels:
- Status code validation: ALWAYS enabled (lightweight, critical for perf testing)
- Full validation (schema, fields): Set LOCUST_ENABLE_FULL_VALIDATION=true
  (disabled by default for maximum performance)

InfluxDB Integration:
- Real-time metrics: Automatically pushed if influxdb.default.enabled=true in config
- Uses centralized InfluxDB configuration from config.{ENV_NAME}.yaml
- Metrics: request_count, response_time, failure_rate, user_count, RPS

Usage:
  locust --file testdata/service/testcases/TestCase_*.json --test_type Performance --env TSADEV
"""

from framework.common.logger import get_logger

# Initialize logger using .env LOG_LEVEL and LOG_TO_CONSOLE
logger = get_logger(__name__)


from locust import HttpUser, task, between, constant_throughput, events
import os
import time
import psutil
from datetime import datetime
from framework.common.template_utils import render_hybrid
from framework.loaders.path_loader import get_project_path
from framework.loaders.testcase_loader import TestCaseLoader
from framework.clients.api_client import ApiClient
from framework.validators.validators import Validators
from framework.test_helpers.test_result_collector import TestResultCollector

# InfluxDB integration - check availability
try:
    from influxdb_client import Point, WritePrecision
    from framework.clients.db_client import DatabaseClientFactory
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False
    logger.warning("InfluxDB client not available. Install with: pip install influxdb-client")

# System monitoring globals
initial_network_io = psutil.net_io_counters()
initial_memory = psutil.virtual_memory().used
test_start_time = None
test_parameters = {}  # Store test parameters for metadata

def get_args():
    import sys
    # Extract custom args before Locust processes them
    custom_args = {'--folder': None, '--test_type': None, '--file': None, '--env': None, '--run_once': None, '--target_rps': None}
    locust_users = None
    for i, arg in enumerate(sys.argv):
        if arg in ('-u', '--users') and i + 1 < len(sys.argv):
            try:
                locust_users = int(sys.argv[i + 1])
            except (TypeError, ValueError):
                locust_users = None
        elif arg.startswith('--users='):
            try:
                locust_users = int(arg.split('=', 1)[1])
            except (TypeError, ValueError):
                locust_users = None

    new_argv = []
    skip_next = False
    for i, arg in enumerate(sys.argv):
        if skip_next:
            skip_next = False
            continue
        if arg in custom_args:
            if i + 1 < len(sys.argv):
                custom_args[arg] = sys.argv[i + 1]
                skip_next = True
        else:
            new_argv.append(arg)
    sys.argv = new_argv
    class Args:
        pass
    args = Args()
    args.folder = custom_args['--folder'] or os.environ.get('LOCUST_FOLDER', None)
    args.test_type = custom_args['--test_type'] or os.environ.get('LOCUST_TEST_TYPE', None)
    args.file = custom_args['--file'] or os.environ.get('LOCUST_FILE', None)
    args.env = custom_args['--env']
    args.users = locust_users or int(os.environ.get('LOCUST_USERS', '1'))

    run_once_raw = custom_args['--run_once'] or os.environ.get('LOCUST_RUN_ONCE', 'true')
    args.run_once = str(run_once_raw).strip().lower() in ('true', '1', 'yes', 'y')

    target_rps_raw = custom_args['--target_rps'] or os.environ.get('LOCUST_TARGET_RPS')
    try:
        args.target_rps = float(target_rps_raw) if target_rps_raw else None
    except (TypeError, ValueError):
        logger.warning(f"Invalid --target_rps value '{target_rps_raw}', using default wait_time")
        args.target_rps = None
    
    # Set ENV_NAME from --env argument if provided, otherwise use existing environment variable or .env
    if args.env:
        os.environ['ENV_NAME'] = args.env
        logger.info(f"ENV_NAME set to '{args.env}' from --env argument")
    elif 'ENV_NAME' not in os.environ:
        # Load from .env file if not already set
        from dotenv import load_dotenv
        load_dotenv()
        env_name = os.environ.get('ENV_NAME')
        if env_name:
            logger.info(f"ENV_NAME loaded from .env file: '{env_name}'")
        else:
            logger.warning("ENV_NAME not found in --env argument, environment variable, or .env file")
    else:
        logger.info(f"ENV_NAME already set in environment: '{os.environ.get('ENV_NAME')}'")
    
    return args

def build_wait_time(args):
    """Build Locust wait_time from optional aggregate target RPS."""
    if args.target_rps and args.target_rps > 0 and args.users > 0:
        per_user_rps = args.target_rps / args.users
        logger.info(
            f"Target aggregate RPS enabled: {args.target_rps} RPS across {args.users} users "
            f"(~{per_user_rps:.4f} RPS/user)"
        )
        return constant_throughput(per_user_rps)

    logger.info("No target RPS configured; using default wait_time between 1 and 3 seconds")
    return between(1, 3)

def load_testcases(folder=None, test_type=None, file=None):
    """Load testcases using framework's TestCaseLoader"""
    logger.info(f"Loading testcases with folder={folder}, test_type={test_type}, file={file}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Project root: {get_project_path()}")
    
    # Determine the testcase pattern using framework's centralized path handling
    if file:
        # Specific file - use framework's path resolution
        testcase_pattern = str(get_project_path(file))
    elif folder:
        # Folder - normalize path separators first, then remove testdata prefix
        folder_normalized = folder.replace('\\', '/')
        if folder_normalized.startswith('testdata/'):
            folder_normalized = folder_normalized[9:]  # Remove 'testdata/' prefix
        folder_normalized = folder_normalized.strip('/')
        
        # Split into parts and use framework's path resolution
        if folder_normalized:
            parts = folder_normalized.split('/')
            folder_path = get_project_path('testdata', *parts)
        else:
            folder_path = get_project_path('testdata')
        
        # CRITICAL: glob.glob() requires absolute path with forward slashes on Linux
        # Use os.path.join to ensure correct path separators
        testcase_pattern = os.path.join(str(folder_path), '*.json')
        
        # Debug: Check if directory exists and list files
        logger.info(f"Folder path: {folder_path}")
        logger.info(f"Folder path (absolute): {folder_path.absolute()}")
        logger.info(f"Folder exists: {folder_path.exists()}")
        logger.info(f"Testcase pattern: {testcase_pattern}")
        if folder_path.exists():
            import glob
            files = glob.glob(testcase_pattern)
            logger.info(f"Glob matched {len(files)} files: {files}")
            # Also try direct listdir
            try:
                direct_files = [f.name for f in folder_path.iterdir() if f.suffix == '.json']
                logger.info(f"Direct listdir found {len(direct_files)} .json files: {direct_files}")
            except Exception as e:
                logger.error(f"Error listing directory: {e}")
        else:
            logger.error(f"Folder does not exist! Cannot load testcases.")
    else:
        # Default pattern - use framework's path resolution
        testcase_pattern = str(get_project_path('testdata') / 'TestCase*.json')
    
    logger.info(f"Testcase pattern: {testcase_pattern}")
    
    # Load testcases directly without using TestCaseLoader to avoid duplicate ID filtering
    # This allows all test cases to be loaded even if they have duplicate test_id across files
    import json
    import glob
    
    files = glob.glob(testcase_pattern)
    logger.info(f"Found {len(files)} test case files to load")
    
    all_testcases = []
    internal_id_counter = 1
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Support new structure: top-level test_data_file and testcases array
                if isinstance(data, dict) and 'testcases' in data:
                    cases = data['testcases']
                elif isinstance(data, list):
                    cases = data
                else:
                    logger.warning(f"Unexpected format in {file_path}, skipping.")
                    continue
                
                for case in cases:
                    if not isinstance(case, dict):
                        logger.warning(f"Invalid test case format in {file_path}, skipping entry.")
                        continue
                    
                    # Add unique internal ID to avoid conflicts with duplicate test_id
                    case['_internal_id'] = f"LOCUST_{internal_id_counter}"
                    case['source_file'] = file_path
                    all_testcases.append(case)
                    internal_id_counter += 1
                
                logger.info(f"Loaded {len(cases)} test cases from {file_path}")
        
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
    
    logger.info(f"Total {len(all_testcases)} testcases loaded (with unique internal IDs)")
    
    # Filter by test_type if specified
    if test_type:
        # Debug: Log what we're looking for and what we have
        logger.info(f"Filtering for test_type='{test_type}'")
        for idx, case in enumerate(all_testcases):
            case_test_type = case.get('test_type', 'NOT_FOUND')
            logger.info(f"  Case {idx}: test_type={case_test_type}, type={type(case_test_type)}")
        
        testcases = [
            case for case in all_testcases 
            if 'test_type' in case and test_type in case['test_type']
        ]
        logger.info(f"Filtered {len(testcases)} testcases matching test_type='{test_type}' from {len(all_testcases)} total")
    else:
        testcases = all_testcases
        logger.info(f"Loaded {len(testcases)} testcases (no test_type filter)")
    
    return testcases

args = get_args()
TESTCASES = load_testcases(folder=args.folder, test_type=args.test_type, file=args.file)

# Store test parameters for metadata
test_parameters = {
    'folder': args.folder,
    'test_type': args.test_type,
    'file': args.file,
    'env': args.env,
    'run_once': args.run_once,
    'target_rps': args.target_rps,
    'users': args.users,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# Load configuration using ConfigManager (automatically detects ENV_NAME)
# Force reload to pick up ENV_NAME from --env argument (overrides .env file)
from framework.loaders.config_loader import get_config
config = get_config(reload=True)

# Log which environment config was loaded
current_env = os.environ.get('ENV_NAME', 'default')
logger.info(f"[CONFIG] Using environment: {current_env} (from --env argument or .env file)")

# Determine host URL from testcases - get service_name from first testcase
api_base_url = None
if TESTCASES:
    # Get service name from first testcase
    service_name = TESTCASES[0].get('service_name')
    if service_name:
        # Try to get service-specific URL from api_endpoints
        api_endpoints = config.get('api_endpoints', {})
        service_config = api_endpoints.get(service_name, {})
        api_base_url = service_config.get('base_url')
        logger.info(f"Using service '{service_name}' with base_url: {api_base_url}")
    
# Fallback to legacy api_base_url if service-specific URL not found
if not api_base_url:
    api_base_url = config.get('api_base_url', None)
    logger.warning(f"No service-specific URL found, using legacy api_base_url: {api_base_url}")

# Initialize InfluxDB client if enabled in config
influx_client = None
influx_enabled = False
influx_batch_buffer = []  # Buffer for batching InfluxDB points
influx_batch_size = 50  # Batch size for InfluxDB writes (configurable)
influx_batch_lock = None  # Thread lock for batch buffer

try:
    # Check if InfluxDB is enabled in configuration
    from framework.loaders.config_loader import substitute_env_vars
    db_connections = config.get('db_connections', {})
    influx_config = db_connections.get('influxdb', {}).get('default', {})
    
    # Substitute environment variables to properly evaluate enabled flag
    influx_config = substitute_env_vars(influx_config)
    
    # Handle enabled flag - can be bool or string
    influx_enabled = influx_config.get('enabled', False)
    if isinstance(influx_enabled, str):
        influx_enabled = influx_enabled.lower() in ('true', '1', 'yes')
    
    # DEBUG: Print to console to verify execution
    print(f"[DEBUG] InfluxDB config check - enabled: {influx_enabled}, INFLUX_AVAILABLE: {INFLUX_AVAILABLE}")
    print(f"[DEBUG] InfluxDB config: {influx_config}")
    
    if influx_enabled and INFLUX_AVAILABLE:
        try:
            print("[DEBUG] Attempting to initialize InfluxDB client...")
            # Use framework's DatabaseClientFactory for centralized connection management
            influx_client = DatabaseClientFactory.get_client('influxdb', 'default', auto_connect=True)
            print(f"[DEBUG] InfluxDB client initialized: {influx_client}")
            
            # Initialize thread lock for batch buffer
            import threading
            influx_batch_lock = threading.Lock()
            
            # Get batch size from config or use default
            influx_batch_size = influx_config.get('batch_size', 50)
            
            print(f"[DEBUG] InfluxDB batch_size: {influx_batch_size}")
            logger.info(f"[InfluxDB] Integration enabled - pushing metrics to {influx_config.get('url')} / bucket: {influx_config.get('bucket')} (batch_size: {influx_batch_size})")
        except Exception as e:
            print(f"[DEBUG] InfluxDB client initialization FAILED: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to initialize InfluxDB client: {e}")
            influx_client = None
            influx_enabled = False
    elif influx_enabled and not INFLUX_AVAILABLE:
        print("[DEBUG] InfluxDB enabled but library not available")
        logger.warning("InfluxDB enabled in config but influxdb-client library not installed. Install with: pip install influxdb-client")
        influx_enabled = False
    else:
        print("[DEBUG] InfluxDB integration disabled in config")
        logger.info("[InfluxDB] Integration disabled (set influxdb.default.enabled=true to enable)")
        
except Exception as e:
    print(f"[DEBUG] Error during InfluxDB config check: {e}")
    import traceback
    traceback.print_exc()
    logger.error(f"Error checking InfluxDB configuration: {e}")
    influx_enabled = False

class APIPerformanceUser(HttpUser):
    wait_time = build_wait_time(args)
    host = api_base_url

    def on_start(self):
        """Initialize framework's ApiClient, validators, and result collector"""
        self.api_client = ApiClient(base_url=self.host or api_base_url, verify=False)
        self.validators = Validators()
        self.result_collector = TestResultCollector()
        
        # Status code validation is always enabled (lightweight, critical for performance testing)
        # Full validation (schema, fields) can be enabled via LOCUST_ENABLE_FULL_VALIDATION=true
        self.enable_full_validation = os.environ.get('LOCUST_ENABLE_FULL_VALIDATION', 'false').lower() == 'true'
        if self.enable_full_validation:
            logger.info("Full response validation (schema, fields) enabled for Locust tests")
        else:
            logger.info("Basic status code validation enabled (set LOCUST_ENABLE_FULL_VALIDATION=true for schema/field validation)")

    @task
    def run_performance_tests(self):
        from framework.loaders.testdata_loader import TestDataLoader
        from framework.loaders.testdata_loader import resolve_testcase_path
        
        logger.info(f"Loaded {len(TESTCASES)} testcases.")
        
        # Optional run-once mode preserves the legacy behavior.
        # Set --run_once false to let each Locust user loop continuously until -t ends.
        if args.run_once:
            if not hasattr(self, '_tests_executed'):
                self._tests_executed = True
            else:
                return  # Skip if tests already executed
        env_name = os.environ.get('ENV_NAME')
        
        for case in TESTCASES:
            logger.info(f"Running testcase: {case.get('test_name', case.get('endpoint'))}")
            context = dict(os.environ)
            context.update(case)
            
            # Add base_url to context based on service_name (with environment variable substitution)
            service_name = case.get('service_name')
            if service_name:
                from framework.loaders.config_loader import ConfigManager
                api_endpoints = config.get('api_endpoints', {})
                service_config = api_endpoints.get(service_name, {})
                service_base_url = service_config.get('base_url')
                if service_base_url:
                    # Substitute environment variables in base_url (e.g., ${ANALYTICS_BASE_URL})
                    service_base_url = ConfigManager.substitute_env_vars(service_base_url)
                    context['base_url'] = service_base_url
                    logger.debug(f"Added base_url to context: {service_base_url} for service: {service_name}")
            
            # Load test data using framework's TestDataLoader
            test_data_file = case.get('test_data_file')
            data_rows = [{}]
            
            if test_data_file:
                try:
                    # Resolve path using framework's path resolution
                    resolved_test_data_file = resolve_testcase_path(test_data_file, base_dir='testdata')
                    logger.debug(f"Resolved test data file: {resolved_test_data_file}")
                    
                    # Use TestDataLoader to load data
                    loader = TestDataLoader(testdata_file=resolved_test_data_file)
                    all_rows = loader.load()
                    
                    # Filter by environment if ENV_NAME is set
                    if env_name:
                        data_rows = [row for row in all_rows if row.get('environment') == env_name]
                        logger.debug(f"Loaded {len(data_rows)} data rows for ENV_NAME={env_name} from {resolved_test_data_file} (total rows: {len(all_rows)})")
                        if not data_rows:
                            logger.warning(f"No test data found for ENV_NAME={env_name} in {resolved_test_data_file}. Stopping all Locust execution.")
                            import sys
                            sys.exit(0)
                    else:
                        data_rows = all_rows
                        logger.debug(f"Loaded {len(data_rows)} data rows (no environment filter)")
                        
                except Exception as e:
                    logger.error(f"Failed to load test data file {test_data_file}: {e}")
                    
            for data_row in data_rows:
                context.update(data_row)
                main_url = render_hybrid(case.get("mainURL", api_base_url), context)
                endpoint = render_hybrid(case.get("endpoint", "/"), context)
                headers = render_hybrid(case.get("headers_additional", {"Content-Type": "application/json"}), context)
                payload = render_hybrid(case.get("payload", None), context)
                method = case.get("method", "GET").upper()
                # Build full URL from mainURL and endpoint
                full_url = main_url.rstrip("/") + "/" + endpoint.lstrip("/")
                logger.info(f"Full URL: {full_url}, Method: {method}, Headers: {headers}, Payload: {payload}")
                if not endpoint or "{" in endpoint:
                    logger.warning(f"Skipping testcase due to unresolved endpoint: {endpoint}")
                    continue
                
                # Use framework's ApiClient and fire Locust events for metrics
                request_name = case.get("test_name", endpoint)
                start_time = time.time()
                response_length = 0
                exception = None
                
                try:
                    # Use framework's ApiClient which has verify=False already configured
                    kwargs = {'headers': headers}
                    if method in ['POST', 'PUT', 'PATCH'] and payload:
                        kwargs['json'] = payload
                    
                    response = self.api_client.request(method, full_url, **kwargs)
                    response_length = len(response.content) if response.content else 0
                    logger.info(f"Response status: {response.status_code}")
                    
                    # ALWAYS validate status code (lightweight and critical for performance testing)
                    expected_status = case.get('expected_status')
                    if expected_status:
                        try:
                            # Convert to int if it's a string
                            expected_status_int = int(expected_status) if expected_status else None
                            if expected_status_int and response.status_code != expected_status_int:
                                exception = AssertionError(f"Status code mismatch: expected {expected_status_int}, got {response.status_code}")
                                logger.warning(f"Status code validation failed: {exception}")
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid expected_status format: {expected_status}, error: {e}")
                    
                    # Full validation (schema, fields) - only if explicitly enabled
                    if self.enable_full_validation:
                        try:
                            # Validate response schema if expected_response_schema is defined
                            expected_schema = case.get('expected_response_schema')
                            if expected_schema and response.content:
                                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                                self.validators.validate_json_schema(response_data, expected_schema, context)
                            
                            # Collect result for reporting (if full validation is enabled)
                            result_entry = self.result_collector.create_result_entry(case, full_url)
                            result_entry['actual_status'] = response.status_code
                            result_entry['response_data'] = response.text[:500] if response.text else ""  # Truncate for performance
                            result_entry['validation_passed'] = True
                            self.result_collector.add_result(result_entry)
                            
                        except Exception as validation_error:
                            logger.warning(f"Full validation failed: {validation_error}")
                            # Don't fail the load test due to validation errors
                            if self.result_collector:
                                result_entry = self.result_collector.create_result_entry(case, full_url)
                                result_entry['actual_status'] = response.status_code
                                result_entry['validation_passed'] = False
                                result_entry['validation_error'] = str(validation_error)
                                self.result_collector.add_result(result_entry)
                    
                except Exception as e:
                    exception = e
                    logger.error(f"Exception during API call: {e}")
                
                finally:
                    # Fire Locust request event for metrics tracking
                    total_time = int((time.time() - start_time) * 1000)
                    events.request.fire(
                        request_type=method,
                        name=request_name,
                        response_time=total_time,
                        response_length=response_length,
                        exception=exception,
                        context={}
                    )


# InfluxDB Helper Functions
def flush_influx_batch():
    """Flush the current batch buffer to InfluxDB"""
    global influx_batch_buffer
    
    if not influx_batch_buffer:
        return
    
    with influx_batch_lock:
        if not influx_batch_buffer:  # Double-check after acquiring lock
            return
        
        try:
            # Copy buffer and clear it immediately to minimize lock time
            points_to_write = influx_batch_buffer.copy()
            influx_batch_buffer.clear()
            
            # Batch write outside the lock
            if points_to_write:
                influx_client.write_points(points_to_write)
                logger.info(f"[InfluxDB] Flushed batch of {len(points_to_write)} metrics")
        except Exception as e:
            logger.error(f"[InfluxDB] Failed to flush batch: {e}")


# InfluxDB Event Handlers - Batch metrics for efficient push
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Buffer request metrics for batch push to InfluxDB"""
    global influx_batch_buffer
    
    if not influx_enabled or not influx_client:
        return
    
    try:
        env_name = os.environ.get('ENV_NAME', 'unknown')
        
        # Determine success/failure
        success = 1 if exception is None else 0
        failure = 0 if exception is None else 1
        
        # Create InfluxDB point with Locust metrics
        point = Point("locust_requests") \
            .tag("environment", env_name) \
            .tag("request_type", request_type) \
            .tag("request_name", name) \
            .tag("success", str(success)) \
            .field("response_time", int(response_time)) \
            .field("response_length", int(response_length)) \
            .field("success_count", success) \
            .field("failure_count", failure) \
            .time(datetime.utcnow(), WritePrecision.MS)
        
        # Add error information if request failed
        if exception:
            error_message = str(exception)[:200]  # Truncate for storage
            point.field("error_message", error_message)
        
        # Add to batch buffer
        with influx_batch_lock:
            influx_batch_buffer.append(point)
            buffer_size = len(influx_batch_buffer)
        
        # Flush batch if it reaches the configured size
        if buffer_size >= influx_batch_size:
            flush_influx_batch()
        
        logger.debug(f"[InfluxDB] Buffered request metric - {request_type} {name} ({response_time}ms) | Buffer: {buffer_size}/{influx_batch_size}")
        
    except Exception as e:
        logger.error(f"[InfluxDB] Failed to buffer request metric: {e}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start event to InfluxDB"""
    if not influx_enabled or not influx_client:
        return
    
    try:
        env_name = os.environ.get('ENV_NAME', 'unknown')
        
        point = Point("locust_test_lifecycle") \
            .tag("environment", env_name) \
            .tag("event", "test_start") \
            .field("user_count", environment.runner.user_count if environment.runner else 0) \
            .field("spawn_rate", getattr(environment.runner, 'spawn_rate', 0) if environment.runner else 0) \
            .time(datetime.utcnow(), WritePrecision.S)
        
        influx_client.write_point(point)
        logger.info(f"InfluxDB: Test started - environment={env_name}")
        
    except Exception as e:
        logger.error(f"Failed to log test start to InfluxDB: {e}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Flush remaining batched metrics and push test summary to InfluxDB"""
    if not influx_enabled or not influx_client:
        return
    
    try:
        # Flush any remaining buffered metrics first
        flush_influx_batch()
        
        env_name = os.environ.get('ENV_NAME', 'unknown')
        stats = environment.stats
        
        # Collect all summary points for batch write
        summary_points = []
        
        # Push overall summary metrics
        point = Point("locust_test_summary") \
            .tag("environment", env_name) \
            .tag("event", "test_stop") \
            .field("total_requests", stats.total.num_requests) \
            .field("total_failures", stats.total.num_failures) \
            .field("avg_response_time", stats.total.avg_response_time) \
            .field("min_response_time", stats.total.min_response_time or 0) \
            .field("max_response_time", stats.total.max_response_time or 0) \
            .field("median_response_time", stats.total.median_response_time or 0) \
            .field("requests_per_second", stats.total.total_rps) \
            .field("failure_rate", stats.total.fail_ratio) \
            .time(datetime.utcnow(), WritePrecision.S)
        
        # Add percentile metrics if available
        if hasattr(stats.total, 'get_response_time_percentile'):
            point.field("p50_response_time", stats.total.get_response_time_percentile(0.50) or 0)
            point.field("p90_response_time", stats.total.get_response_time_percentile(0.90) or 0)
            point.field("p95_response_time", stats.total.get_response_time_percentile(0.95) or 0)
            point.field("p99_response_time", stats.total.get_response_time_percentile(0.99) or 0)
        
        summary_points.append(point)
        
        logger.info(f"[InfluxDB] Test completed - Total Requests: {stats.total.num_requests}, "
                   f"Failures: {stats.total.num_failures}, "
                   f"Avg Response Time: {stats.total.avg_response_time:.2f}ms, "
                   f"RPS: {stats.total.total_rps:.2f}")
        
        # Collect per-endpoint summary metrics
        for name, stat in stats.entries.items():
            endpoint_point = Point("locust_endpoint_summary") \
                .tag("environment", env_name) \
                .tag("endpoint", name) \
                .field("total_requests", stat.num_requests) \
                .field("total_failures", stat.num_failures) \
                .field("avg_response_time", stat.avg_response_time) \
                .field("min_response_time", stat.min_response_time or 0) \
                .field("max_response_time", stat.max_response_time or 0) \
                .field("median_response_time", stat.median_response_time or 0) \
                .field("requests_per_second", stat.total_rps) \
                .field("failure_rate", stat.fail_ratio) \
                .time(datetime.utcnow(), WritePrecision.S)
            
            # Add percentile metrics per endpoint
            if hasattr(stat, 'get_response_time_percentile'):
                endpoint_point.field("p50_response_time", stat.get_response_time_percentile(0.50) or 0)
                endpoint_point.field("p90_response_time", stat.get_response_time_percentile(0.90) or 0)
                endpoint_point.field("p95_response_time", stat.get_response_time_percentile(0.95) or 0)
                endpoint_point.field("p99_response_time", stat.get_response_time_percentile(0.99) or 0)
            
            summary_points.append(endpoint_point)
        
        # Batch write all summary metrics at once
        if summary_points:
            influx_client.write_points(summary_points)
            logger.info(f"[InfluxDB] Pushed test summary and {len(stats.entries)} endpoint summaries as batch ({len(summary_points)} total points)")
        
    except Exception as e:
        logger.error(f"[InfluxDB] Failed to push test summary: {e}")


# Event handlers for memory and network monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Capture initial system state when test starts"""
    global test_start_time, initial_network_io, initial_memory
    test_start_time = time.time()
    initial_network_io = psutil.net_io_counters()
    initial_memory = psutil.virtual_memory().used
    logger.info(f"[MONITOR] Test started - Initial Memory: {initial_memory / (1024**3):.2f} GB, Network I/O captured")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Calculate and log system resource usage and add to CSV/HTML reports"""
    global test_start_time, initial_network_io, initial_memory, test_parameters
    
    try:
        # Calculate test duration
        test_duration = time.time() - test_start_time
        
        # Memory usage
        current_memory = psutil.virtual_memory().used
        memory_delta = (current_memory - initial_memory) / (1024**3)  # GB
        
        # Network usage
        current_network_io = psutil.net_io_counters()
        bytes_sent = (current_network_io.bytes_sent - initial_network_io.bytes_sent) / (1024**2)  # MB
        bytes_recv = (current_network_io.bytes_recv - initial_network_io.bytes_recv) / (1024**2)  # MB
        
        # CPU usage average
        cpu_percent = psutil.cpu_percent(interval=1)
        
        monitoring_data = {
            'test_duration_sec': f'{test_duration:.2f}',
            'memory_delta_gb': f'{memory_delta:.3f}',
            'network_sent_mb': f'{bytes_sent:.2f}',
            'network_recv_mb': f'{bytes_recv:.2f}',
            'cpu_avg_percent': f'{cpu_percent:.1f}'
        }
        
        logger.info(f"[MONITOR] Test completed - Duration: {test_duration:.2f}s, "
                   f"Memory Δ: {memory_delta:.3f} GB, "
                   f"Network Sent: {bytes_sent:.2f} MB, Recv: {bytes_recv:.2f} MB, "
                   f"CPU Avg: {cpu_percent:.1f}%")
        
        # Add monitoring data and test parameters to CSV stats
        stats = environment.stats
        stats.monitoring_data = monitoring_data
        stats.test_parameters = test_parameters
        
        # Write enhanced metadata to CSV file if CSV reporting is enabled
        # Try to determine CSV file path from stats writer or check if CSV flag was passed
        csv_base = None
        
        # Method 1: Check for csv_prefix (Locust 2.x)
        if hasattr(environment.parsed_options, 'csv_prefix') and environment.parsed_options.csv_prefix:
            csv_base = environment.parsed_options.csv_prefix
        
        # Method 2: Check if stats has CSV writer configured
        elif hasattr(environment.runner, 'stats') and hasattr(environment.runner.stats, 'csv_writer'):
            csv_writer = environment.runner.stats.csv_writer
            if csv_writer and hasattr(csv_writer, 'stats_filename'):
                # Remove the _stats.csv suffix to get base name
                csv_base = csv_writer.stats_filename.replace('_stats.csv', '')
        
        # Method 3: Check parsed_options for csvfilebase (Locust 2.x)
        elif hasattr(environment.parsed_options, 'csvfilebase') and environment.parsed_options.csvfilebase:
            csv_base = environment.parsed_options.csvfilebase
        
        # Method 4: Check for csv attribute (older Locust)
        elif hasattr(environment.parsed_options, 'csv') and environment.parsed_options.csv:
            csv_base = environment.parsed_options.csv
        
        # If we have a CSV base path, write the metadata file
        if csv_base:
            metadata_file = f"{csv_base}_metadata.txt"
            
            try:
                with open(metadata_file, 'w') as f:
                    f.write("# Locust Performance Test Metadata\n\n")
                    f.write("## Test Parameters\n")
                    for key, value in test_parameters.items():
                        f.write(f"{key}: {value}\n")
                    
                    f.write("\n## System Monitoring\n")
                    for key, value in monitoring_data.items():
                        f.write(f"{key}: {value}\n")
                    
                    f.write(f"\n## Command Line Arguments\n")
                    # Extract user, spawn rate, and run time from parsed options
                    f.write(f"users (-u): {getattr(environment.parsed_options, 'num_users', 'N/A')}\n")
                    f.write(f"spawn_rate (-r): {getattr(environment.parsed_options, 'spawn_rate', 'N/A')}\n")
                    f.write(f"run_time (-t): {getattr(environment.parsed_options, 'run_time', 'N/A')}\n")
                
                logger.info(f"[REPORT] Enhanced metadata written to: {metadata_file}")
            except Exception as write_error:
                logger.error(f"[REPORT] Failed to write metadata file: {write_error}")

            # Generate the custom executive summary HTML next to performance_report.html
            try:
                from framework.reporter.perf_summary_reporter import generate_executive_summary

                # SLA threshold (seconds): env override → config → default 1.0
                sla_seconds = 1.0
                try:
                    sla_env = os.environ.get('LOCUST_SLA_SECONDS')
                    if sla_env:
                        sla_seconds = float(sla_env)
                    else:
                        perf_cfg = config.get('performance', {}) if isinstance(config, dict) else {}
                        sla_seconds = float(perf_cfg.get('sla_seconds', 1.0))
                except (TypeError, ValueError):
                    sla_seconds = 1.0

                # Derive service / objective from first testcase if available
                svc_name = None
                objective_text = None
                try:
                    if TESTCASES:
                        svc_name = TESTCASES[0].get('service_name')
                        first_endpoint = TESTCASES[0].get('endpoint') or ''
                        first_method = TESTCASES[0].get('method', 'GET')
                        first_name = TESTCASES[0].get('test_name', first_endpoint)
                        objective_text = (
                            f"Evaluate the performance of {first_method} {first_endpoint} "
                            f"({first_name}) for {svc_name or 'service'}."
                        )
                except Exception:
                    pass

                summary_path = generate_executive_summary(
                    csv_base=csv_base,
                    test_parameters=test_parameters,
                    monitoring_data=monitoring_data,
                    sla_seconds=sla_seconds,
                    service_name=svc_name,
                    objective=objective_text,
                    azure_devops_url=os.environ.get('BUILD_BUILDURI') or os.environ.get('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI'),
                )
                logger.info(f"[REPORT] Executive summary written to: {summary_path}")
            except Exception as summary_error:
                logger.error(f"[REPORT] Failed to generate executive summary: {summary_error}")
        else:
            logger.info("[REPORT] CSV reporting not enabled - metadata file not created")
    
    except Exception as e:
        logger.error(f"[MONITOR] Failed to collect system metrics: {e}")
