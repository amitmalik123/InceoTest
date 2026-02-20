"""
Log Analytics Reporter

Pushes test results to Azure Log Analytics for monitoring and visualization in Grafana.
Uses HTTP Data Collector API with Shared Key authentication.
"""

import json
import os
import hashlib
import hmac
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from framework.loaders.config_loader import get_config
from framework.loaders.path_loader import get_project_path
from framework.common.logger import get_logger

logger = get_logger(__name__)


class LogAnalyticsReporter:
    """Reporter for pushing test results to Azure Log Analytics"""
    
    def __init__(self, workspace_id: str, shared_key: str):
        """
        Initialize Log Analytics Reporter
        
        Args:
            workspace_id: Azure Log Analytics Workspace ID (GUID)
            shared_key: Primary or Secondary Shared Key (base64 encoded)
        """
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = "TestResults"  # Creates TestResults_CL table
        self.api_version = "2016-04-01"
        
    def _build_signature(self, date: str, content_length: int, method: str, 
                        content_type: str, resource: str) -> str:
        """
        Build the authorization signature for Log Analytics API
        
        Args:
            date: RFC 1123 formatted date string
            content_length: Length of the JSON payload
            method: HTTP method (POST)
            content_type: Content type (application/json)
            resource: API resource (/api/logs)
        
        Returns:
            Authorization header value
        """
        x_headers = f"x-ms-date:{date}"
        string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = f"SharedKey {self.workspace_id}:{encoded_hash}"
        return authorization
    
    def _post_data(self, body: str, log_type: str) -> bool:
        """
        Post data to Log Analytics using HTTP Data Collector API
        
        Args:
            body: JSON string payload
            log_type: Custom log type name (creates {log_type}_CL table)
        
        Returns:
            True if successful, False otherwise
        """
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"
        rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        
        signature = self._build_signature(
            rfc1123date, content_length, method, content_type, resource
        )
        
        uri = f"https://{self.workspace_id}.ods.opinsights.azure.com{resource}?api-version={self.api_version}"
        
        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date
        }
        
        try:
            response = requests.post(uri, data=body, headers=headers, timeout=30)
            
            if response.status_code >= 200 and response.status_code <= 299:
                logger.info(f"[Log Analytics] Data accepted for {log_type}_CL table (Status: {response.status_code})")
                return True
            else:
                logger.error(f"[Log Analytics] Failed to post data: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"[Log Analytics] Request timeout while posting to {log_type}_CL")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"[Log Analytics] Request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"[Log Analytics] Unexpected error: {e}")
            return False
    
    def push_test_results(self, data: Dict) -> bool:
        """
        Push aggregated test results to Log Analytics
        
        Args:
            data: Test results data dictionary with summary and results
        
        Returns:
            True if successful, False otherwise
        """
        try:
            summary = data.get('summary', {})
            test_results = data.get('results', [])
            
            # Calculate aggregated metrics
            total_tests = summary.get('total', 0)
            passed_tests = summary.get('passed', 0)
            failed_tests = summary.get('failed', 0)
            skipped_tests = summary.get('skipped', 0)
            
            # Calculate pass rate
            pass_rate = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0
            
            # Calculate average response time from test results
            response_times = [r.get('response_time', 0) for r in test_results if r.get('response_time')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Get failed test names
            failed_test_names = [r.get('test_name', 'unknown') for r in test_results if r.get('status') == 'FAIL']
            
            # Aggregate validation statistics
            def aggregate_validation_stats(results: List[Dict]) -> Dict:
                """Aggregate validation statistics across all tests"""
                aggregated = {
                    'status_code_checks': {'total': 0, 'passed': 0, 'failed': 0},
                    'assertions': {'total': 0, 'passed': 0, 'failed': 0},
                    'contract_checks': {'total': 0, 'passed': 0, 'failed': 0},
                    'security_checks': {'total': 0, 'passed': 0, 'failed': 0},
                    'performance_checks': {'total': 0, 'passed': 0, 'failed': 0}
                }
                
                for result in results:
                    vstats = result.get('validation_stats', {})
                    for category in aggregated.keys():
                        cat_stats = vstats.get(category, {})
                        aggregated[category]['total'] += cat_stats.get('total', 0)
                        aggregated[category]['passed'] += cat_stats.get('passed', 0)
                        aggregated[category]['failed'] += cat_stats.get('failed', 0)
                
                return aggregated
            
            validation_aggregates = aggregate_validation_stats(test_results)
            
            # Prepare aggregated test result record
            test_record = {
                "RunTimestamp": data.get('timestamp', datetime.utcnow().strftime('%Y%m%d_%H%M%S')),
                "Environment": data.get('environment', 'unknown'),
                "ServiceName": data.get('service_name', 'unknown'),
                "BuildId": os.environ.get('BUILD_BUILDID', 'local'),
                "BuildNumber": os.environ.get('BUILD_BUILDNUMBER', 'local'),
                "PipelineId": os.environ.get('SYSTEM_DEFINITIONID', 'unknown'),
                "PipelineName": os.environ.get('BUILD_DEFINITIONNAME', 'unknown'),
                # Test Metrics
                "TotalTests": total_tests,
                "PassedTests": passed_tests,
                "FailedTests": failed_tests,
                "SkippedTests": skipped_tests,
                "PassRate": round(pass_rate, 2),
                # Timing
                "Duration": data.get('duration', '00:00:00'),
                "StartTime": data.get('start_time', ''),
                "EndTime": data.get('end_time', ''),
                "AvgResponseTime": round(avg_response_time, 2),
                # Failed Test Details
                "FailedTestNames": ', '.join(failed_test_names[:10]) if failed_test_names else '',  # Limit to 10
                "FailedTestCount": len(failed_test_names),
                # Validation Statistics Aggregates
                "StatusCodeChecksTotal": validation_aggregates['status_code_checks']['total'],
                "StatusCodeChecksPassed": validation_aggregates['status_code_checks']['passed'],
                "StatusCodeChecksFailed": validation_aggregates['status_code_checks']['failed'],
                "AssertionsTotal": validation_aggregates['assertions']['total'],
                "AssertionsPassed": validation_aggregates['assertions']['passed'],
                "AssertionsFailed": validation_aggregates['assertions']['failed'],
                "ContractChecksTotal": validation_aggregates['contract_checks']['total'],
                "ContractChecksPassed": validation_aggregates['contract_checks']['passed'],
                "ContractChecksFailed": validation_aggregates['contract_checks']['failed'],
                "SecurityChecksTotal": validation_aggregates['security_checks']['total'],
                "SecurityChecksPassed": validation_aggregates['security_checks']['passed'],
                "SecurityChecksFailed": validation_aggregates['security_checks']['failed'],
                "PerformanceChecksTotal": validation_aggregates['performance_checks']['total'],
                "PerformanceChecksPassed": validation_aggregates['performance_checks']['passed'],
                "PerformanceChecksFailed": validation_aggregates['performance_checks']['failed']
            }
            
            # Convert to JSON array (Log Analytics expects an array)
            json_payload = json.dumps([test_record])
            
            # Post to Log Analytics
            success = self._post_data(json_payload, self.log_type)
            
            if success:
                logger.info(f"[Log Analytics] Successfully pushed test results: {total_tests} total, {passed_tests} passed, {failed_tests} failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to push test results to Log Analytics: {e}")
            return False


def push_to_log_analytics() -> bool:
    """
    Push aggregated test results to Azure Log Analytics
    
    Returns:
        True if successful, False otherwise
    
    Environment Variables Required:
        LOG_ANALYTICS_WORKSPACE_ID: Azure Log Analytics Workspace ID
        LOG_ANALYTICS_SHARED_KEY: Primary or Secondary Shared Key
        LOG_ANALYTICS_ENABLED: Enable/disable Log Analytics reporting (default: true)
    
    Example:
        >>> push_to_log_analytics()
        True
    """
    try:
        # Check if Log Analytics is enabled
        enabled = os.environ.get('LOG_ANALYTICS_ENABLED', 'true').lower()
        if enabled not in ['true', '1', 'yes']:
            logger.info("[Log Analytics] Reporting is disabled (LOG_ANALYTICS_ENABLED != true)")
            return True  # Return True to not fail the pipeline
        
        # Get credentials from environment
        workspace_id = os.environ.get('LOG_ANALYTICS_WORKSPACE_ID')
        shared_key = os.environ.get('LOG_ANALYTICS_SHARED_KEY')
        
        if not workspace_id or not shared_key:
            logger.error("[Log Analytics] Missing credentials: LOG_ANALYTICS_WORKSPACE_ID or LOG_ANALYTICS_SHARED_KEY")
            return False
        
        logger.info(f"[Log Analytics] Connecting to workspace: {workspace_id}")
        
        # Find latest test results
        reports_dir = get_project_path('reports')
        
        if not reports_dir.exists():
            logger.error(f"Reports directory not found: {reports_dir}")
            return False
        
        # Get latest report folder
        folders = [
            f for f in reports_dir.iterdir()
            if f.is_dir() and f.name != 'archive' and not f.name.startswith('.')
        ]
        
        if not folders:
            logger.error("No report folders found in reports directory")
            return False
        
        latest_folder = max(folders, key=lambda f: f.stat().st_mtime)
        test_summary_path = latest_folder / 'test_results_summary.json'
        
        if not test_summary_path.exists():
            logger.error(f"test_results_summary.json not found in {latest_folder}")
            return False
        
        # Load test results
        with open(test_summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"[Log Analytics] Loaded test results from {test_summary_path}")
        
        # Add environment info if not present
        if 'environment' not in data:
            config = get_config()
            data['environment'] = config.get('env_name', 'unknown')
        
        # Add service name if not present
        if 'service_name' not in data:
            data['service_name'] = os.environ.get('SERVICE_NAME', 'unknown')
        
        # Initialize reporter
        reporter = LogAnalyticsReporter(workspace_id, shared_key)
        
        # Push aggregated test results
        logger.info("[Log Analytics] Pushing aggregated test results...")
        success = reporter.push_test_results(data)
        
        if success:
            logger.info("[Log Analytics] ✅ Test results pushed successfully")
            logger.info("[Log Analytics] Note: Table may take 5-15 minutes to appear in Log Analytics")
            logger.info("[Log Analytics] Table name: TestResults_CL")
        else:
            logger.warning("[Log Analytics] ⚠️ Failed to push test results")
        
        return success
        
    except FileNotFoundError as e:
        logger.error(f"Report file not found: {e}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in report file: {e}")
        return False
    except Exception as e:
        logger.error(f"Error pushing to Log Analytics: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Allow running standalone for testing
    import sys
    
    success = push_to_log_analytics()
    
    if success:
        print("✅ Log Analytics push completed successfully")
        sys.exit(0)
    else:
        print("❌ Log Analytics push failed")
        sys.exit(1)
