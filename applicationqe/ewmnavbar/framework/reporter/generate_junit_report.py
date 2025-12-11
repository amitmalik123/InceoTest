#!/usr/bin/env python3
"""
Generate JUnit XML report from Allure test results.
Converts Allure JSON results to standards-compliant JUnit XML format with enhanced details.

Enhanced Details Included:
- Test identification: UUID, testCaseId, description
- Test organization: package, suite, parentSuite, subSuite
- Test classification: epic, feature, story, severity, tags
- Test execution: retry info, timing details, execution mode
- Environment: Node.js, Playwright, browser, OS versions
- Pipeline: build info, CI system, agent details
- Test artifacts: attachments, links, parameters
- Performance: duration categories, stability scores
- Error analysis: detailed failure types, system output
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def parse_allure_results(results_dir):
    """Parse all Allure JSON result files."""
    results = []
    
    if not os.path.exists(results_dir):
        print(f"Warning: Results directory not found: {results_dir}")
        return results
    
    # Track test names to detect retries
    test_names_seen = {}
    
    for file in os.listdir(results_dir):
        if file.endswith('-result.json'):
            file_path = os.path.join(results_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    
                    # Check for retries
                    test_name = result.get('name', '')
                    if test_name in test_names_seen:
                        result['_is_retry'] = True
                        test_names_seen[test_name] += 1
                    else:
                        result['_is_retry'] = False
                        test_names_seen[test_name] = 1
                    
                    result['_retry_count'] = test_names_seen[test_name]
                    
                    results.append(result)
            except Exception as e:
                print(f"Warning: Failed to parse {file}: {e}")
    
    return results


def calculate_duration(result):
    """Calculate test duration from start and stop timestamps (in seconds)."""
    if 'start' in result and 'stop' in result:
        duration = (result['stop'] - result['start']) / 1000.0  # Convert ms to seconds
        return max(0, duration)  # Ensure non-negative
    return 0


def extract_test_details(result):
    """Extract detailed information from test result."""
    details = {
        'name': result.get('name', 'Unknown'),
        'status': result.get('status', 'unknown'),
        'duration': calculate_duration(result),
        'file': result.get('source', result.get('testCaseId', '')),
        'uuid': result.get('uuid', ''),
        'testCaseId': result.get('testCaseId', ''),
        'description': result.get('description', ''),
        'error_message': '',
        'error_trace': '',
        'labels': [],
        'steps': len(result.get('steps', [])),
        'step_details': [],
        'attachments': len(result.get('attachments', [])),
        'parameters': result.get('parameters', []),
        'links': result.get('links', []),
        'retry': result.get('_is_retry', False),
        'retry_count': result.get('_retry_count', 1),
    }

    # Extract error details
    if 'statusDetails' in result:
        status_details = result['statusDetails']
        if 'message' in status_details:
            details['error_message'] = status_details['message']
        if 'trace' in status_details:
            details['error_trace'] = status_details['trace']

    # Extract labels with more detail
    if 'labels' in result:
        for label in result['labels']:
            label_name = label.get('name', '')
            label_value = label.get('value', '')
            details['labels'].append(f"{label_name}={label_value}")

            # Extract specific label information
            if label_name == 'package':
                details['package'] = label_value
            elif label_name == 'suite':
                details['suite'] = label_value
            elif label_name == 'parentSuite':
                details['parent_suite'] = label_value
            elif label_name == 'subSuite':
                details['sub_suite'] = label_value
            elif label_name == 'epic':
                details['epic'] = label_value
            elif label_name == 'feature':
                details['feature'] = label_value
            elif label_name == 'story':
                details['story'] = label_value
            elif label_name == 'severity':
                details['severity'] = label_value
            elif label_name == 'tag':
                if 'tags' not in details:
                    details['tags'] = []
                details['tags'].append(label_value)

    # Extract step details
    if 'steps' in result:
        for step in result['steps']:
            step_info = {
                'name': step.get('name', ''),
                'status': step.get('status', ''),
                'duration': calculate_duration(step)
            }
            details['step_details'].append(step_info)

    # Extract attachment information
    if 'attachments' in result:
        details['attachment_details'] = []
        for attachment in result['attachments']:
            attachment_info = {
                'name': attachment.get('name', ''),
                'type': attachment.get('type', ''),
                'source': attachment.get('source', '')
            }
            details['attachment_details'].append(attachment_info)

    return details


def generate_junit_xml(results, output_file):
    """Generate JUnit XML from Allure results."""
    
    # Group results by test suite
    suites = defaultdict(list)
    for result in results:
        suite_name = result.get('source', 'All Tests')
        suites[suite_name].append(result)
    
    # Calculate metrics
    total_tests = len(results)
    passed = sum(1 for r in results if r.get('status') == 'passed')
    failed = sum(1 for r in results if r.get('status') == 'failed')
    skipped = sum(1 for r in results if r.get('status') == 'skipped')
    total_duration = sum(calculate_duration(r) for r in results)
    
    # Create root testsuites element
    testsuites = ET.Element('testsuites')
    testsuites.set('id', '')
    testsuites.set('name', 'Playwright Test Results')
    testsuites.set('tests', str(total_tests))
    testsuites.set('failures', str(failed))
    testsuites.set('skipped', str(skipped))
    testsuites.set('errors', '0')  # JUnit standard
    testsuites.set('time', f'{total_duration:.6f}')  # More precision like Playwright
    testsuites.set('timestamp', datetime.now().isoformat())
    
    # Create testsuite for each file
    for suite_name, suite_results in suites.items():
        suite_passed = sum(1 for r in suite_results if r.get('status') == 'passed')
        suite_failed = sum(1 for r in suite_results if r.get('status') == 'failed')
        suite_skipped = sum(1 for r in suite_results if r.get('status') == 'skipped')
        suite_duration = sum(calculate_duration(r) for r in suite_results)
        
        testsuite = ET.SubElement(testsuites, 'testsuite')
        testsuite.set('name', suite_name)
        testsuite.set('tests', str(len(suite_results)))
        testsuite.set('failures', str(suite_failed))
        testsuite.set('skipped', str(suite_skipped))
        testsuite.set('errors', '0')  # JUnit standard
        testsuite.set('time', f'{suite_duration:.6f}')  # More precision
        testsuite.set('timestamp', datetime.now().isoformat())
        testsuite.set('hostname', os.getenv('COMPUTERNAME', os.getenv('HOSTNAME', 'localhost')))
        
        # Add individual test cases
        for result in suite_results:
            details = extract_test_details(result)
            
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', details['name'])
            testcase.set('classname', suite_name)
            testcase.set('time', f'{details["duration"]:.6f}')  # Match Playwright precision
            
            # Add additional attributes for better pipeline integration
            if details.get('uuid'):
                testcase.set('uuid', details['uuid'])
            if details.get('testCaseId'):
                testcase.set('testcaseid', details['testCaseId'])
            
            # Add properties
            properties = ET.SubElement(testcase, 'properties')
            
            # Add detailed properties
            props = [
                ('file', details['file']),
                ('status', details['status']),
                ('steps', str(details['steps'])),
                ('duration_ms', str(int(details['duration'] * 1000))),
                ('attachments', str(details['attachments'])),
            ]
            
            # Add UUID and test case ID as properties
            if details.get('uuid'):
                props.append(('uuid', details['uuid']))
            if details.get('testCaseId'):
                props.append(('testCaseId', details['testCaseId']))
            
            # Add description if available
            if details.get('description'):
                props.append(('description', details['description']))
            
            # Add structured label information
            if details.get('package'):
                props.append(('package', details['package']))
            if details.get('suite'):
                props.append(('suite', details['suite']))
            if details.get('parent_suite'):
                props.append(('parentSuite', details['parent_suite']))
            if details.get('sub_suite'):
                props.append(('subSuite', details['sub_suite']))
            if details.get('epic'):
                props.append(('epic', details['epic']))
            if details.get('feature'):
                props.append(('feature', details['feature']))
            if details.get('story'):
                props.append(('story', details['story']))
            if details.get('severity'):
                props.append(('severity', details['severity']))
            
            # Add tags if available
            if details.get('tags'):
                props.append(('tags', ', '.join(details['tags'])))
            
            # Add all labels as a single property
            if details['labels']:
                props.append(('labels', ', '.join(details['labels'])))
            
            # Add parameters if available
            if details.get('parameters'):
                for i, param in enumerate(details['parameters']):
                    props.append((f'parameter_{i}_name', param.get('name', '')))
                    props.append((f'parameter_{i}_value', param.get('value', '')))
            
            # Add links if available
            if details.get('links'):
                for i, link in enumerate(details['links']):
                    props.append((f'link_{i}_name', link.get('name', '')))
                    props.append((f'link_{i}_url', link.get('url', '')))
                    props.append((f'link_{i}_type', link.get('type', '')))
            
            # Add step details
            if details.get('step_details'):
                for i, step in enumerate(details['step_details']):
                    props.append((f'step_{i}_name', step['name']))
                    props.append((f'step_{i}_status', step['status']))
                    props.append((f'step_{i}_duration', f"{step['duration']:.3f}s"))
            
            # Add attachment details
            if details.get('attachment_details'):
                for i, attachment in enumerate(details['attachment_details']):
                    props.append((f'attachment_{i}_name', attachment['name']))
                    props.append((f'attachment_{i}_type', attachment['type']))
                    props.append((f'attachment_{i}_source', attachment['source']))
            
            # Add retry information
            if details.get('retry'):
                props.append(('retry', 'true'))
            props.append(('retry_count', str(details.get('retry_count', 1))))
            
            # Add build and environment info if available
            build_id = os.getenv('BUILD_ID', '')
            environment = os.getenv('ENVIRONMENT', '')
            build_reason = os.getenv('BUILD_REASON', '')
            
            if build_id:
                props.append(('build_id', build_id))
            if environment:
                props.append(('environment', environment))
            if build_reason:
                props.append(('build_reason', build_reason))
            
            # Add test execution environment details
            node_version = os.getenv('NODE_VERSION', '')
            playwright_version = os.getenv('PLAYWRIGHT_VERSION', '')
            browser_name = os.getenv('BROWSER_NAME', '')
            browser_version = os.getenv('BROWSER_VERSION', '')
            os_name = os.getenv('RUNNER_OS', os.getenv('OS', ''))
            ci_system = os.getenv('CI', os.getenv('TF_BUILD', ''))
            
            if node_version:
                props.append(('node_version', node_version))
            if playwright_version:
                props.append(('playwright_version', playwright_version))
            if browser_name:
                props.append(('browser_name', browser_name))
            if browser_version:
                props.append(('browser_version', browser_version))
            if os_name:
                props.append(('os', os_name))
            if ci_system:
                props.append(('ci_system', 'true' if ci_system else 'false'))
            
            # Add test timing details
            if 'start' in result:
                start_time = datetime.fromtimestamp(result['start'] / 1000).isoformat()
                props.append(('start_time', start_time))
            if 'stop' in result:
                stop_time = datetime.fromtimestamp(result['stop'] / 1000).isoformat()
                props.append(('stop_time', stop_time))
            
            # Add test execution mode details
            execution_mode = 'headed' if not os.getenv('CI', '').lower() == 'true' else 'headless'
            parallel_execution = 'false'  # Since workers: 1 in config
            retries_config = '2' if os.getenv('CI', '').lower() == 'true' else '0'
            
            props.append(('execution_mode', execution_mode))
            props.append(('parallel_execution', parallel_execution))
            props.append(('retries_config', retries_config))
            
            # Add test classification details
            test_type = 'automated'
            test_category = 'e2e'
            test_priority = details.get('severity', 'normal')
            
            props.append(('test_type', test_type))
            props.append(('test_category', test_category))
            props.append(('test_priority', test_priority))
            
            # Add performance metrics if available
            if details['duration'] > 0:
                duration_category = 'fast' if details['duration'] < 5 else 'medium' if details['duration'] < 30 else 'slow'
                props.append(('duration_category', duration_category))
            
            # Add test stability indicators
            stability_score = 'high' if not details.get('retry') else 'medium' if details.get('retry_count', 1) <= 2 else 'low'
            props.append(('stability_score', stability_score))
            
            # Add test metadata
            test_framework = 'Playwright'
            test_language = 'TypeScript'
            test_runner = 'playwright/test'
            
            props.append(('test_framework', test_framework))
            props.append(('test_language', test_language))
            props.append(('test_runner', test_runner))
            
            # Add pipeline-specific information
            pipeline_name = os.getenv('BUILD_DEFINITIONNAME', '')
            pipeline_stage = os.getenv('SYSTEM_STAGENAME', '')
            agent_name = os.getenv('AGENT_NAME', '')
            
            if pipeline_name:
                props.append(('pipeline_name', pipeline_name))
            if pipeline_stage:
                props.append(('pipeline_stage', pipeline_stage))
            if agent_name:
                props.append(('agent_name', agent_name))
            
            for prop_name, prop_value in props:
                if prop_value:
                    prop = ET.SubElement(properties, 'property')
                    prop.set('name', prop_name)
                    prop.set('value', str(prop_value))
            
            # Add failure/error elements for failed tests
            if details['status'] == 'failed':
                failure = ET.SubElement(testcase, 'failure')
                failure.set('type', 'AssertionError')
                if details['error_message']:
                    failure.set('message', details['error_message'])
                if details['error_trace']:
                    failure.text = details['error_trace']
                
                # Add additional failure analysis
                if details.get('error_message'):
                    error_type = 'AssertionError'
                    if 'timeout' in details['error_message'].lower():
                        error_type = 'TimeoutError'
                    elif 'network' in details['error_message'].lower():
                        error_type = 'NetworkError'
                    elif 'element' in details['error_message'].lower() and 'not found' in details['error_message'].lower():
                        error_type = 'ElementNotFoundError'
                    failure.set('type', error_type)
            
            # Add skipped for skipped tests
            elif details['status'] == 'skipped':
                skipped_elem = ET.SubElement(testcase, 'skipped')
                # Add skip reason if available
                if details.get('error_message'):
                    skipped_elem.set('message', details['error_message'])
            
            # Add system-out for additional test output if available
            if details.get('step_details'):
                system_out = ET.SubElement(testcase, 'system-out')
                output_lines = []
                for step in details['step_details']:
                    output_lines.append(f"Step: {step['name']} - {step['status']} ({step['duration']:.3f}s)")
                system_out.text = '\n'.join(output_lines)
            
            # Add system-err for error details
            if details['status'] == 'failed' and details.get('error_trace'):
                system_err = ET.SubElement(testcase, 'system-err')
                system_err.text = details['error_trace']
    
    # Write XML to file
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    tree = ET.ElementTree(testsuites)
    ET.indent(tree, space='  ')  # Pretty print (Python 3.9+)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print(f"✓ JUnit XML report generated: {output_file}")
    print(f"  - Total Tests: {total_tests}")
    print(f"  - Passed: {passed}")
    print(f"  - Failed: {failed}")
    print(f"  - Skipped: {skipped}")
    print(f"  - Duration: {total_duration:.2f}s")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python3 generate_junit_report.py <allure_results_dir> <output_file>")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    # Parse Allure results
    results = parse_allure_results(results_dir)
    
    if not results:
        print(f"Warning: No Allure results found in {results_dir}")
        print("Creating empty JUnit report...")
    
    # Generate JUnit XML
    generate_junit_xml(results, output_file)
    print("✓ Done!")


if __name__ == '__main__':
    main()
