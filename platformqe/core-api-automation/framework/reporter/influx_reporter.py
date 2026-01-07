"""
InfluxDB Reporter

Pushes test results to InfluxDB for time-series metrics and dashboarding.
Uses centralized path loading and configuration management.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from framework.loaders.config_loader import get_config
from framework.loaders.path_loader import get_project_path, find_files
from framework.loaders.test_result_loader import load_test_summary_from_json
from framework.common.logger import get_logger
from framework.clients.db_client import DatabaseClientFactory

logger = get_logger(__name__)

# Import InfluxDB classes for type hints and Point creation
try:
    from influxdb_client import Point, WritePrecision
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False
    logger.warning("influxdb-client not installed. InfluxDB reporting disabled.")


def get_latest_report_file(report_filename: Optional[str] = None) -> Optional[str]:
    """
    Find the latest JSON report file in the reports directory.
    
    Args:
        report_filename: Specific report filename to look for (e.g., 'json_report_20251123_084658.json')
                        If None, finds the most recent JSON file
    
    Returns:
        Absolute path to the report file, or None if not found
    """
    try:
        reports_dir = get_project_path('reports')
        
        if not reports_dir.exists():
            logger.error(f"Reports directory not found: {reports_dir}")
            return None
        
        # Get all timestamped folders (exclude 'archive')
        folders = [
            f for f in reports_dir.iterdir()
            if f.is_dir() and f.name != 'archive' and not f.name.startswith('.')
        ]
        
        if not folders:
            logger.error("No report folders found in reports directory")
            return None
        
        # Get the latest folder by modification time
        latest_folder = max(folders, key=lambda f: f.stat().st_mtime)
        logger.debug(f"Latest report folder: {latest_folder}")
        
        # Find JSON files in the latest folder
        if report_filename:
            # Look for specific file
            report_path = latest_folder / report_filename
            if report_path.exists():
                return str(report_path)
            logger.warning(f"Specific report file not found: {report_filename}")
        
        # Find any JSON file (prefer json_report_*, report.json)
        json_files = list(latest_folder.glob('*.json'))
        
        if not json_files:
            logger.error(f"No JSON report files found in {latest_folder}")
            return None
        
        # Prioritize specific filenames (look for files starting with these names)
        priority_prefixes = ['json_report_', 'result', 'report', 'test_report']
        for prefix in priority_prefixes:
            for json_file in json_files:
                if json_file.name.startswith(prefix):
                    logger.info(f"Found report file: {json_file}")
                    return str(json_file)
        
        # Return the first JSON file found
        report_path = json_files[0]
        logger.info(f"Using report file: {report_path}")
        return str(report_path)
        
    except Exception as e:
        logger.error(f"Error finding latest report file: {e}")
        return None


def push_to_infux(report_filename: str = None) -> bool:
    """
    Push test results from JSON report to InfluxDB.
    
    Args:
        report_filename: Name of the report file to push (default: None, auto-detects latest)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> push_to_infux()
        True
    """
    try:
        # Check if InfluxDB client is available
        if not INFLUX_AVAILABLE:
            logger.error("InfluxDB client not available. Install with: pip install influxdb-client")
            return False
        
        # Load configuration using centralized config loader
        config = get_config()
        
        # Load test results using centralized loader
        # This uses test_summary.json with full validation statistics
        test_results, test_summary = load_test_summary_from_json()
        
        if not test_results:
            logger.error("No test results loaded from test_summary.json")
            return False
        
        logger.info(f"Loaded {len(test_results)} test results from centralized loader")
        logger.debug(f"Summary: {test_summary}")
        
        # Connect to InfluxDB using DatabaseClientFactory
        try:
            # Get InfluxDB client (uses db_connections.influxdb.default from config)
            influx_client = DatabaseClientFactory.get_client('influxdb', 'default', auto_connect=True)
            
            # Get configuration for tags
            env_name = config.get('env_name', 'unknown')
            
            # Get bucket and org from the client's config
            bucket = influx_client.bucket
            org = influx_client.org
            
            # Push summary metrics using loaded test_summary
            if test_summary:
                try:
                    total = int(test_summary.get('total', 0))
                    passed = int(test_summary.get('passed', 0))
                    failed = int(test_summary.get('failed', 0))
                    skipped = int(test_summary.get('skipped', 0))
                    # Note: xfailed and xpassed might not be in test_summary from centralized loader
                    xfailed = int(test_summary.get('xfailed', 0))
                    xpassed = int(test_summary.get('xpassed', 0))
                    
                    summary_point = Point("test_summary") \
                        .tag("environment", env_name) \
                        .field("total", total) \
                        .field("passed", passed) \
                        .field("failed", failed) \
                        .field("skipped", skipped) \
                        .field("xfailed", xfailed) \
                        .field("xpassed", xpassed) \
                        .time(datetime.utcnow(), WritePrecision.S)
                    
                    influx_client.write_point(summary_point)
                    logger.info(f"[InfluxDB] Summary metrics pushed | Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped} | XFailed: {xfailed} | XPassed: {xpassed}")
                except Exception as e:
                    logger.warning(f"Failed to push summary metrics: {e}")
            
            # Push individual test results - collect all points for batch write
            if not test_results:
                logger.warning("No test results available")
                influx_client.close()
                return False
            
            # Collect all points in a list for batch write
            points_to_write = []
            failed_count = 0
            
            for result in test_results:
                try:
                    # Extract test information
                    test_id = result.get('test_id', 'unknown')
                    test_name = result.get('test_name', 'unknown')
                    
                    # Map status to outcome for backward compatibility with existing dashboards
                    status = result.get('status', 'unknown')
                    outcome = status  # test_summary.json uses 'status', map to 'outcome' for InfluxDB
                    
                    # Create point with test result data
                    point = Point("test_results") \
                        .tag("environment", env_name) \
                        .tag("test_id", str(test_id)) \
                        .tag("test_name", str(test_name)) \
                        .tag("service_name", str(result.get('service_name', 'unknown'))) \
                        .tag("outcome", str(outcome)) \
                        .tag("status", str(status))
                    
                    logger.debug(f"Creating point for test: {test_id}")
                    
                    # Add numeric fields - response_time is in milliseconds
                    response_time = int(result.get('response_time', 0))
                    point.field("duration", float(response_time / 1000.0))  # Convert ms to seconds for duration
                    point.field("response_time", response_time)
                    
                    # Add optional fields - test_summary.json uses 'summary' not 'test_summary'
                    if 'summary' in result:
                        point.field("summary", str(result['summary']))
                    
                    if 'error' in result and result['error']:
                        point.field("error", str(result['error']))
                    
                    # Add validation statistics if available
                    # test_summary.json has 'validation_stats' with detailed counts
                    if 'validation_stats' in result:
                        vstats = result['validation_stats']
                        if isinstance(vstats, dict):
                            # Add aggregated validation counts for each check type
                            contract = vstats.get('contract_checks', {})
                            security = vstats.get('security_checks', {})
                            performance = vstats.get('performance_checks', {})
                            
                            point.field("validation_contract_total", int(contract.get('total', 0)))
                            point.field("validation_contract_passed", int(contract.get('passed', 0)))
                            point.field("validation_security_total", int(security.get('total', 0)))
                            point.field("validation_security_passed", int(security.get('passed', 0)))
                            point.field("validation_performance_total", int(performance.get('total', 0)))
                            point.field("validation_performance_passed", int(performance.get('passed', 0)))
                    
                    # Set timestamp
                    point.time(datetime.utcnow(), WritePrecision.S)
                    
                    # Validate point has at least one field
                    if not hasattr(point, '_fields') or not point._fields:
                        logger.warning(f"Point for test {test_id} has no fields, skipping")
                        failed_count += 1
                        continue
                    
                    # Add to batch list
                    points_to_write.append(point)
                    logger.debug(f"Point for test {test_id} added to batch (total: {len(points_to_write)})")
                    
                except Exception as e:
                    logger.error(f"Failed to create point for test {result.get('test_id', 'unknown')}: {e}")
                    failed_count += 1
                    continue
            
            # Batch write all points at once
            if points_to_write:
                try:
                    logger.info(f"[InfluxDB] Attempting to write {len(points_to_write)} points to bucket '{bucket}'")
                    influx_client.write_points(points_to_write)
                    logger.info(f"[InfluxDB] Successfully pushed {len(points_to_write)}/{len(test_results)} test results (failed: {failed_count})")
                except Exception as e:
                    logger.error(f"Failed to batch write test results to InfluxDB: {e}", exc_info=True)
                    return False
            else:
                logger.warning(f"[InfluxDB] No test results were pushed (0/{len(test_results)}, failed: {failed_count})")
                return False
            
            # Connection is managed by the factory, but we can close if needed
            # Note: Factory keeps connections in a pool for reuse
            return len(points_to_write) > 0
            
        except ConnectionError as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            return False
        except TimeoutError as e:
            logger.error(f"InfluxDB connection timed out: {e}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to InfluxDB: {e}")
            return False
    
    except FileNotFoundError as e:
        logger.error(f"Report file not found: {e}")
        return False
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in report file: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Error pushing to InfluxDB: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Allow running standalone for testing
    import sys
    
    report_file = sys.argv[1] if len(sys.argv) > 1 else None
    success = push_to_infux(report_file)
    
    if success:
        print("✅ InfluxDB push completed successfully")
        sys.exit(0)
    else:
        print("❌ InfluxDB push failed")
        sys.exit(1)
