#!/usr/bin/env python3
"""
InfluxDB Reporter: Parses Allure JSON results and pushes metrics to InfluxDB
"""

import json
import os
import sys
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class AllureToInfluxDB:
    """Convert Allure test results to InfluxDB metrics"""
    
    def __init__(self):
        self.influx_url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.influx_token = os.getenv('INFLUXDB_TOKEN', '')
        self.influx_org = os.getenv('INFLUXDB_ORG', 'default')
        self.influx_bucket = os.getenv('INFLUXDB_BUCKET', 'test-results')
        self.allure_results_dir = os.getenv('ALLURE_RESULTS_DIR', './allure-results')
        self.build_id = os.getenv('BUILD_ID', 'local')
        self.build_reason = os.getenv('BUILD_REASON', 'Manual')
        self.environment = os.getenv('ENVIRONMENT', 'test11')
        
        # Azure Pipelines variables for artifact links
        self.system_team_foundation_collection_uri = os.getenv('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI', '')
        self.system_team_project = os.getenv('SYSTEM_TEAMPROJECT', '')
        self.build_buildid = os.getenv('BUILD_BUILDID', self.build_id)
        
    def get_artifact_urls(self) -> Dict[str, str]:
        """Generate artifact download URLs for Azure Pipelines"""
        urls = {}
        
        if not self.system_team_foundation_collection_uri or not self.system_team_project:
            return urls
        
        base_url = f"{self.system_team_foundation_collection_uri.rstrip('/')}/{self.system_team_project}/_build/results"
        artifacts = ['PlaywrightReport', 'AllureReport', 'AllureResults', 'TestResults']
        
        for artifact in artifacts:
            urls[artifact] = f"{base_url}?buildId={self.build_buildid}&artifactName={artifact}"
        
        return urls
        
    def read_allure_results(self) -> Dict[str, Any]:
        """Read Allure results from JSON files - use Allure's native summary for accurate counts"""
        results = {
            'tests': [],
            'containers': [],
            'groups': [],
            'test_names': [],
            'allure_summary': {}  # Store Allure's own summary
        }
        
        if not os.path.exists(self.allure_results_dir):
            print(f"⚠️  Allure results directory not found: {self.allure_results_dir}")
            return results
        
        # First, try to read Allure's summary-results.json if it exists
        summary_file = os.path.join(self.allure_results_dir, 'summary-results.json')
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    results['allure_summary'] = json.load(f)
                    print(f"📊 Found Allure summary: {results['allure_summary']}")
            except Exception as e:
                print(f"Error reading summary: {e}")
        
        # Read ALL test result files (including retries)
        json_files = glob.glob(os.path.join(self.allure_results_dir, '*-result.json'))
        print(f"📂 Found {len(json_files)} total test result files")
        
        # Store ALL test executions
        test_names_seen = {}
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    test_name = test_data.get('name', '')
                    test_uuid = test_data.get('uuid', '')
                    status = test_data.get('status', 'unknown')
                    
                    # Get labels to extract spec file and package info
                    labels = test_data.get('labels', [])
                    spec_file = ''
                    package_name = ''
                    
                    for label in labels:
                        label_name = label.get('name', '')
                        label_value = label.get('value', '')
                        if label_name == 'package':
                            package_name = label_value
                        elif label_name == 'suite':
                            spec_file = label_value
                    
                    # Create unique identifier: package/spec_file::test_name
                    if package_name and spec_file:
                        unique_id = f"{package_name}/{spec_file}::{test_name}"
                    elif spec_file:
                        unique_id = f"{spec_file}::{test_name}"
                    else:
                        unique_id = test_name
                    
                    print(f"  📄 {os.path.basename(json_file)}")
                    print(f"      test_name='{test_name}'")
                    print(f"      package='{package_name}'")
                    print(f"      spec_file='{spec_file}'")
                    print(f"      unique_id='{unique_id}'")
                    print(f"      status={status}")
                    
                    if test_name:
                        results['tests'].append(test_data)
                        # Track unique test identifiers per spec file
                        if unique_id not in test_names_seen:
                            test_names_seen[unique_id] = True
                            results['test_names'].append(unique_id)
                        print(f"      ✓ Added with unique_id: {unique_id}")
                    else:
                        print(f"      ⚠️  WARNING: No 'name' field found in test data!")
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        # Print detailed results
        print(f"\n📊 Test Execution Summary:")
        print(f"  Total test executions (including retries): {len(results['tests'])}")
        print(f"  Unique test names: {len(results['test_names'])}")
        print(f"  Unique test names list: {results['test_names']}")
        if len(results['tests']) > len(results['test_names']):
            print(f"  Tests that were retried: {len(results['tests']) - len(results['test_names'])}")
        
        print(f"\n📋 All Test Executions (including retries):")
        for i, test_data in enumerate(results['tests'], 1):
            test_name = test_data.get('name', 'unknown')
            status = test_data.get('status', 'unknown')
            print(f"  [{i}] {status.upper()}: {test_name}")
        
        # Read containers
        for json_file in glob.glob(os.path.join(self.allure_results_dir, '*-container.json')):
            try:
                with open(json_file, 'r') as f:
                    container_data = json.load(f)
                    results['containers'].append(container_data)
                    print(f"  📦 Container: {container_data.get('name', 'unknown')}")
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        # Read groups
        for json_file in glob.glob(os.path.join(self.allure_results_dir, 'groups.json')):
            try:
                with open(json_file, 'r') as f:
                    results['groups'].append(json.load(f))
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        return results
    
    def analyze_test_steps(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract step-level metrics from a single test"""
        steps = test_data.get('steps', [])
        step_count = 0
        passed_steps = 0
        failed_steps = 0
        fixture_setup_time = 0
        fixture_teardown_time = 0
        
        for step in steps:
            # Count main steps (not nested)
            if step.get('name', '').startswith('Before Hooks'):
                fixture_setup_time = step.get('stop', 0) - step.get('start', 0)
            elif step.get('name', '').startswith('After Hooks'):
                fixture_teardown_time = step.get('stop', 0) - step.get('start', 0)
            else:
                step_count += 1
                if step.get('status') == 'passed':
                    passed_steps += 1
                elif step.get('status') == 'failed':
                    failed_steps += 1
        
        # Count attachments
        attachments = test_data.get('attachments', [])
        screenshot_count = sum(1 for a in attachments if 'image' in a.get('type', ''))
        log_count = sum(1 for a in attachments if 'text' in a.get('type', ''))
        
        return {
            'step_count': step_count,
            'passed_steps': passed_steps,
            'failed_steps': failed_steps,
            'fixture_setup_time': fixture_setup_time,
            'fixture_teardown_time': fixture_teardown_time,
            'screenshot_count': screenshot_count,
            'log_count': log_count,
            'total_attachments': len(attachments)
        }
    
    def extract_test_metadata(self, test_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract test metadata from labels"""
        labels = test_data.get('labels', [])
        metadata = {
            'host': '',
            'suite': '',
            'sub_suite': '',
            'package': '',
            'thread': '',
            'parent_suite': ''
        }
        
        for label in labels:
            name = label.get('name', '')
            value = label.get('value', '')
            if name == 'host':
                metadata['host'] = value
            elif name == 'suite':
                metadata['suite'] = value
            elif name == 'subSuite':
                metadata['sub_suite'] = value
            elif name == 'package':
                metadata['package'] = value
            elif name == 'thread':
                metadata['thread'] = value
            elif name == 'parentSuite':
                metadata['parent_suite'] = value
        
        return metadata

    def calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test metrics from Allure results - Use Allure's summary if available"""
        allure_summary = results.get('allure_summary', {})
        all_tests = results.get('tests', [])
        test_names = results.get('test_names', [])
        
        # Check if we have Allure's official summary
        if allure_summary:
            print(f"\n✓ Using Allure's official summary statistics")
            metrics = {
                'total': allure_summary.get('total', 0),
                'passed': allure_summary.get('passed', 0),
                'failed': allure_summary.get('failed', 0),
                'skipped': allure_summary.get('skipped', 0),
                'broken': allure_summary.get('broken', 0),
                'flaky': 0,
                'retried': 0,
                'total_duration': allure_summary.get('duration', 0),
                'avg_duration': 0,
                'max_duration': 0,
                'min_duration': 0,
                'pass_rate': 0
            }
            
            # Calculate pass rate
            testable_total = metrics['total'] - metrics['skipped']
            if testable_total > 0:
                metrics['pass_rate'] = (metrics['passed'] / testable_total) * 100
            
            # Calculate average duration
            if metrics['total'] > 0 and metrics['total_duration'] > 0:
                metrics['avg_duration'] = int(metrics['total_duration'] / metrics['total'])
            
            print(f"📊 Metrics from Allure Summary:")
            print(f"  Total tests: {metrics['total']}")
            print(f"  Passed: {metrics['passed']}")
            print(f"  Failed: {metrics['failed']}")
            print(f"  Skipped: {metrics['skipped']}")
            print(f"  Broken: {metrics['broken']}")
            print(f"  Duration: {metrics['total_duration']}ms")
            print(f"  Pass rate: {metrics['pass_rate']:.1f}%")
            
            return metrics
        
        # Fallback to manual calculation if no Allure summary
        print(f"\n⚠️  No Allure summary found, using manual calculation")
        print(f"  all_tests count: {len(all_tests)}")
        print(f"  test_names count: {len(test_names)}")
        print(f"  test_names list: {test_names}")
        
        metrics = {
            'total': len(test_names),  # Total UNIQUE tests
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'broken': 0,
            'flaky': 0,
            'retried': len(all_tests) - len(test_names),  # Count of tests that were retried
            'total_duration': 0,
            'avg_duration': 0,
            'max_duration': 0,
            'min_duration': 0,
            'pass_rate': 0,
            'total_steps': 0,
            'avg_steps_per_test': 0,
            'total_screenshots': 0,
            'total_logs': 0,
            'avg_fixture_setup': 0,
            'hosts': set(),
            'suites': set(),
            'test_details': {}  # Detailed per-test metrics
        }
        
        # Build a dictionary of LATEST result for each unique test identifier
        latest_results_by_id = {}
        for test in all_tests:
            # Extract package and spec file from labels (same logic as read_allure_results)
            labels = test.get('labels', [])
            spec_file = ''
            package_name = ''
            
            for label in labels:
                label_name = label.get('name', '')
                label_value = label.get('value', '')
                if label_name == 'package':
                    package_name = label_value
                elif label_name == 'suite':
                    spec_file = label_value
            
            test_name = test.get('name', '')
            
            # Create unique identifier: package/spec_file::test_name
            if package_name and spec_file:
                unique_id = f"{package_name}/{spec_file}::{test_name}"
            elif spec_file:
                unique_id = f"{spec_file}::{test_name}"
            else:
                unique_id = test_name
            
            if unique_id:
                if unique_id not in latest_results_by_id:
                    latest_results_by_id[unique_id] = test
                else:
                    # Keep the result with the later stop time (latest execution)
                    current_stop = latest_results_by_id[unique_id].get('stop', 0)
                    new_stop = test.get('stop', 0)
                    if new_stop > current_stop:
                        latest_results_by_id[unique_id] = test
        
        print(f"  latest_results_by_id count: {len(latest_results_by_id)}")
        print(f"  latest_results_by_id keys: {list(latest_results_by_id.keys())}")
        
        durations = []
        fixture_setup_times = []
        test_details = []
        
        # Process UNIQUE tests only (latest status of each)
        for unique_id in test_names:
            test = latest_results_by_id.get(unique_id)
            if not test:
                print(f"  ⚠️  WARNING: test_id '{unique_id}' not found in latest_results_by_id")
                continue
                
            status = test.get('status', 'unknown')
            status_details = test.get('statusDetails', {})
            is_flaky = status_details.get('flaky', False)
            test_name = test.get('name', unique_id)
            
            # Analyze test steps and attachments
            step_metrics = self.analyze_test_steps(test)
            test_metadata = self.extract_test_metadata(test)
            
            # Track metadata
            if test_metadata['host']:
                metrics['hosts'].add(test_metadata['host'])
            if test_metadata['suite']:
                metrics['suites'].add(test_metadata['suite'])
            
            print(f"  Processing {unique_id}: {status}")
            
            # Count based on final status (UNIQUE tests only, no duplicates)
            if status == 'passed':
                metrics['passed'] += 1
                if is_flaky:
                    metrics['flaky'] += 1
                    test_details.append(f"  ✓ {test_name} [PASSED - FLAKY]")
                else:
                    test_details.append(f"  ✓ {test_name} [PASSED]")
            elif status == 'failed':
                metrics['failed'] += 1
                test_details.append(f"  ✗ {test_name} [FAILED]")
            elif status == 'broken':
                # Broken is tracked separately, not added to failed
                metrics['broken'] += 1
                test_details.append(f"  ✗ {test_name} [BROKEN]")
            elif status == 'skipped':
                metrics['skipped'] += 1
                test_details.append(f"  - {test_name} [SKIPPED]")
            else:
                # Unknown status
                test_details.append(f"  ? {test_name} [{status.upper()}]")
            
            # Track duration
            duration = test.get('stop', 0) - test.get('start', 0)
            metrics['total_duration'] += duration
            if duration > 0:
                durations.append(duration)
            
            # Accumulate step and attachment metrics
            metrics['total_steps'] += step_metrics['step_count']
            metrics['total_screenshots'] += step_metrics['screenshot_count']
            metrics['total_logs'] += step_metrics['log_count']
            if step_metrics['fixture_setup_time'] > 0:
                fixture_setup_times.append(step_metrics['fixture_setup_time'])
            
            # Store per-test details
            metrics['test_details'][unique_id] = {
                'status': status,
                'duration': duration,
                'steps': step_metrics['step_count'],
                'screenshots': step_metrics['screenshot_count'],
                'logs': step_metrics['log_count']
            }
        
        # Calculate duration statistics
        if durations:
            metrics['avg_duration'] = int(metrics['total_duration'] / len(durations))
            metrics['max_duration'] = max(durations)
            metrics['min_duration'] = min(durations)
        
        # Calculate step averages
        if metrics['total'] > 0:
            metrics['avg_steps_per_test'] = int(metrics['total_steps'] / metrics['total'])
        
        # Calculate fixture setup average
        if fixture_setup_times:
            metrics['avg_fixture_setup'] = int(sum(fixture_setup_times) / len(fixture_setup_times))
        
        # Convert sets to lists for JSON serialization
        metrics['hosts_list'] = list(metrics['hosts'])
        metrics['suites_list'] = list(metrics['suites'])
        metrics['host_count'] = len(metrics['hosts'])
        metrics['suite_count'] = len(metrics['suites'])
        
        # Calculate pass rate (excluding skipped tests from calculation)
        testable_total = metrics['total'] - metrics['skipped']
        if testable_total > 0:
            metrics['pass_rate'] = (metrics['passed'] / testable_total) * 100
        
        # Debug: Show metrics summary
        print(f"\n📊 Metrics Summary for InfluxDB:")
        print(f"  Total unique tests: {metrics['total']}")
        print(f"  Tests passed: {metrics['passed']}")
        print(f"  Tests failed: {metrics['failed']}")
        print(f"  Tests broken: {metrics['broken']}")
        print(f"  Tests skipped: {metrics['skipped']}")
        print(f"  Tests retried: {metrics['retried']}")
        print(f"  Pass rate: {metrics['pass_rate']:.1f}%")
        print(f"\n📋 Final Test Results (Unique Tests - LATEST outcome):")
        for detail in test_details:
            print(detail)
        
        return metrics
    
    def create_influx_points(self, metrics: Dict[str, Any], artifact_urls: Dict[str, str]) -> List[str]:
        """Create InfluxDB line protocol points from metrics"""
        timestamp = int(datetime.now().timestamp() * 1e9)  # nanoseconds
        
        # Build host and suite tags
        host_str = metrics['hosts_list'][0] if metrics['hosts_list'] else 'unknown'
        suite_str = metrics['suites_list'][0] if metrics['suites_list'] else 'all'
        
        tags = f'build_id="{self.build_id}",environment="{self.environment}",build_reason="{self.build_reason}",host="{host_str}",suite="{suite_str}"'
        
        # Main test execution metrics
        points = [
            f'test_execution2,{tags} '
            f'total={metrics["total"]}i,'
            f'passed={metrics["passed"]}i,'
            f'failed={metrics["failed"]}i,'
            f'skipped={metrics["skipped"]}i,'
            f'broken={metrics["broken"]}i,'
            f'flaky={metrics["flaky"]}i,'
            f'retried={metrics["retried"]}i,'
            f'pass_rate={metrics["pass_rate"]:.2f},'
            f'total_duration={metrics["total_duration"]}i,'
            f'avg_duration={metrics["avg_duration"]}i,'
            f'max_duration={metrics["max_duration"]}i,'
            f'min_duration={metrics["min_duration"]}i '
            f'{timestamp}'
        ]
        
        # Test execution details measurement (steps, attachments, fixtures)
        points.append(
            f'test_execution_details2,{tags} '
            f'total_steps={metrics["total_steps"]}i,'
            f'avg_steps_per_test={metrics["avg_steps_per_test"]}i,'
            f'total_screenshots={metrics["total_screenshots"]}i,'
            f'total_logs={metrics["total_logs"]}i,'
            f'avg_fixture_setup={metrics["avg_fixture_setup"]}i,'
            f'host_count={metrics["host_count"]}i,'
            f'suite_count={metrics["suite_count"]}i '
            f'{timestamp}'
        )
        
        # Flaky test quality metric
        if metrics['total'] > 0:
            flaky_rate = (metrics['flaky'] / metrics['total']) * 100
            retry_rate = (metrics['retried'] / metrics['total']) * 100
            
            points.append(
                f'test_quality2,{tags} '
                f'flaky_count={metrics["flaky"]}i,'
                f'flaky_rate={flaky_rate:.2f},'
                f'retried_count={metrics["retried"]}i,'
                f'retry_rate={retry_rate:.2f} '
                f'{timestamp}'
            )
        
        # Artifact URLs as a separate measurement
        if artifact_urls:
            artifact_tags = tags
            artifact_data = ','.join([f'{name}="{url}"' for name, url in artifact_urls.items()])
            points.append(
                f'test_artifacts2,{artifact_tags} '
                f'{artifact_data} '
                f'{timestamp}'
            )
        
        return points
    
    def push_to_influxdb(self, points: List[str]) -> bool:
        """Push metrics to InfluxDB"""
        if not self.influx_token:
            print("⚠️  INFLUXDB_TOKEN not set. Skipping InfluxDB push.")
            return False
        
        try:
            client = InfluxDBClient(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            print(f"📊 Pushing {len(points)} metric(s) to InfluxDB ({self.influx_url})...")
            for point in points:
                print(f"  - {point[:80]}...")
                write_api.write(bucket=self.influx_bucket, record=point)
            
            client.close()
            print("✓ Successfully pushed metrics to InfluxDB")
            return True
            
        except Exception as e:
            print(f"❌ Error pushing to InfluxDB: {e}")
            return False
    
    def run(self):
        """Main execution"""
        print("=" * 70)
        print(">>> Allure to InfluxDB Reporter")
        print("=" * 70)
        print(f"InfluxDB URL: {self.influx_url}")
        print(f"Allure Results Dir: {self.allure_results_dir}")
        print(f"Environment: {self.environment}")
        print(f"Build ID: {self.build_id}")
        print()
        
        # Read Allure results
        results = self.read_allure_results()
        if not results['tests']:
            print("[WARNING] No test results found. Skipping InfluxDB push.")
            return
        
        print(f"[INFO] Found {len(results['tests'])} test result(s)")
        
        # Calculate metrics
        metrics = self.calculate_metrics(results)
        print(f"\n[METRICS] Test Execution Metrics:")
        print(f"  Total Tests: {metrics['total']}")
        print(f"  Passed: {metrics['passed']}")
        print(f"  Failed: {metrics['failed']}")
        print(f"  Skipped: {metrics['skipped']}")
        print(f"  Broken: {metrics['broken']}")
        print(f"  Flaky Tests: {metrics['flaky']}")
        print(f"  Pass Rate: {metrics['pass_rate']:.2f}%")
        print(f"  Total Duration: {metrics['total_duration']}ms")
        print(f"  Avg Duration: {metrics['avg_duration']}ms")
        print(f"  Max Duration: {metrics['max_duration']}ms")
        print(f"  Min Duration: {metrics['min_duration']}ms")
        
        print(f"\n[DETAILS] Test Execution Details:")
        print(f"  Total Steps: {metrics['total_steps']}")
        print(f"  Avg Steps Per Test: {metrics['avg_steps_per_test']}")
        print(f"  Total Screenshots: {metrics['total_screenshots']}")
        print(f"  Total Logs: {metrics['total_logs']}")
        print(f"  Avg Fixture Setup Time: {metrics['avg_fixture_setup']}ms")
        print(f"  Host Count: {metrics['host_count']}")
        print(f"  Suite Count: {metrics['suite_count']}")
        if metrics['hosts_list']:
            print(f"  Hosts: {', '.join(metrics['hosts_list'])}")
        if metrics['suites_list']:
            print(f"  Suites: {', '.join(metrics['suites_list'][:3])}{'...' if len(metrics['suites_list']) > 3 else ''}")
        
        print(f"\n[QUALITY] Test Quality Metrics:")
        if metrics['total'] > 0:
            flaky_rate = (metrics['flaky'] / metrics['total']) * 100
            print(f"  Flaky Rate: {flaky_rate:.2f}%")
            retry_rate = (metrics['retried'] / metrics['total']) * 100
            print(f"  Retried Tests: {metrics['retried']}")
            print(f"  Retry Rate: {retry_rate:.2f}%")
        
        # Get artifact URLs
        artifact_urls = self.get_artifact_urls()
        if artifact_urls:
            print(f"\n🔗 Pipeline Artifacts:")
            for name, url in artifact_urls.items():
                print(f"  {name}: {url[:80]}...")
        print()
        
        # Create and push points
        points = self.create_influx_points(metrics, artifact_urls)
        self.push_to_influxdb(points)
        print("=" * 70)


if __name__ == '__main__':
    reporter = AllureToInfluxDB()
    reporter.run()
