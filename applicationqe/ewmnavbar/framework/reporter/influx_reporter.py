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
        self.allure_results_dir = os.getenv('ALLURE_RESULTS_DIR', './target/allure-results')
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
        """Read Allure results from JSON files"""
        results = {
            'tests': [],
            'containers': [],
            'groups': []
        }
        
        if not os.path.exists(self.allure_results_dir):
            print(f"⚠️  Allure results directory not found: {self.allure_results_dir}")
            return results
        
        # Read test results - track by test name to use only the latest result
        json_files = glob.glob(os.path.join(self.allure_results_dir, '*-result.json'))
        print(f"📂 Found {len(json_files)} total test result files")
        
        # Dictionary to store latest result for each test (by test name)
        latest_results = {}
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    test_data = json.load(f)
                    test_name = test_data.get('name', '')
                    test_uuid = test_data.get('uuid', '')
                    
                    if test_name:
                        # Keep the latest result (by timestamp/stop time)
                        if test_name not in latest_results:
                            latest_results[test_name] = test_data
                        else:
                            # Compare stop times to keep the latest
                            current_stop = latest_results[test_name].get('stop', 0)
                            new_stop = test_data.get('stop', 0)
                            if new_stop > current_stop:
                                latest_results[test_name] = test_data
            except Exception as e:
                print(f"Error reading {json_file}: {e}")
        
        # Add unique results to output
        results['tests'] = list(latest_results.values())
        duplicate_count = len(json_files) - len(results['tests'])
        print(f"⚠️  Deduplicated to {len(results['tests'])} unique test(s) by name (skipped {duplicate_count} duplicates/retries)")
        
        # Print unique tests
        for test_data in results['tests']:
            test_name = test_data.get('name', 'unknown')
            status = test_data.get('status', 'unknown')
            print(f"  - {status.upper()}: {test_name}")
        
        # Read containers
        for json_file in glob.glob(os.path.join(self.allure_results_dir, '*-container.json')):
            try:
                with open(json_file, 'r') as f:
                    results['containers'].append(json.load(f))
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
    
    def calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test metrics from Allure results"""
        tests = results.get('tests', [])
        
        metrics = {
            'total': len(tests),
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'broken': 0,
            'flaky': 0,
            'retried': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'max_duration': 0,
            'min_duration': 0,
            'pass_rate': 0
        }
        
        durations = []
        status_counts = {}
        test_details = []
        
        for test in tests:
            status = test.get('status', 'unknown')
            status_details = test.get('statusDetails', {})
            test_name = test.get('name', 'unknown')
            
            # Track raw statuses for debugging
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Check if test is flaky
            is_flaky = status_details.get('flaky', False)
            
            # Count based on final status
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
            
            # Check for retried tests (tests that were retried)
            history = test.get('historyId', '')
            if history:
                # Test has history - indicates retries
                metrics['retried'] += 1
            
            # Track duration
            duration = test.get('stop', 0) - test.get('start', 0)
            metrics['total_duration'] += duration
            if duration > 0:
                durations.append(duration)
        
        # Calculate duration statistics
        if durations:
            metrics['avg_duration'] = int(metrics['total_duration'] / len(durations))
            metrics['max_duration'] = max(durations)
            metrics['min_duration'] = min(durations)
        
        # Calculate pass rate (excluding skipped tests from calculation)
        testable_total = metrics['total'] - metrics['skipped']
        if testable_total > 0:
            metrics['pass_rate'] = (metrics['passed'] / testable_total) * 100
        
        # Debug: Show status distribution
        print(f"\n🔍 Raw Status Distribution: {status_counts}")
        print(f"\n📋 Test Details:")
        for detail in test_details:
            print(detail)
        
        return metrics
    
    def create_influx_points(self, metrics: Dict[str, Any], artifact_urls: Dict[str, str]) -> List[str]:
        """Create InfluxDB line protocol points from metrics"""
        timestamp = int(datetime.now().timestamp() * 1e9)  # nanoseconds
        
        tags = f'build_id="{self.build_id}",environment="{self.environment}",build_reason="{self.build_reason}"'
        
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
        print("🚀 Allure to InfluxDB Reporter")
        print("=" * 70)
        print(f"InfluxDB URL: {self.influx_url}")
        print(f"Allure Results Dir: {self.allure_results_dir}")
        print(f"Environment: {self.environment}")
        print(f"Build ID: {self.build_id}")
        print()
        
        # Read Allure results
        results = self.read_allure_results()
        if not results['tests']:
            print("⚠️  No test results found. Skipping InfluxDB push.")
            return
        
        print(f"📂 Found {len(results['tests'])} test result(s)")
        
        # Calculate metrics
        metrics = self.calculate_metrics(results)
        print(f"\n📈 Test Execution Metrics:")
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
        
        print(f"\n⚠️  Test Quality Metrics:")
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
