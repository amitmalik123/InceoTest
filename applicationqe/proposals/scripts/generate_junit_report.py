#!/usr/bin/env python3
"""
Generate JUnit XML report from Allure test results
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

def generate_junit_report(allure_dir, output_file):
    """Generate JUnit XML from Allure results"""
    
    # Initialize counters
    passed = 0
    failed = 0
    skipped = 0
    total_duration = 0  # in milliseconds
    test_cases = []
    slowest_tests = []
    test_labels = {}  # Track labels/tags
    test_files = {}  # Track test files
    
    # Parse Allure results
    if os.path.isdir(allure_dir):
        for filename in os.listdir(allure_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(allure_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        result = json.load(f)
                        
                    test_name = result.get('name', filename.replace('.json', ''))
                    status = result.get('status', 'passed')
                    duration = result.get('stop', 0) - result.get('start', 0)  # milliseconds
                    
                    # Convert milliseconds to seconds
                    duration_seconds = duration / 1000.0
                    total_duration += duration
                    
                    # Extract additional details
                    labels = result.get('labels', [])
                    steps = result.get('steps', [])
                    stage = result.get('stage', 'finished')
                    statusDetails = result.get('statusDetails', {})
                    
                    # Track test file/suite
                    test_file = 'Unknown'
                    for label in labels:
                        if label.get('name') == 'testClassPattern':
                            test_file = label.get('value', 'Unknown')
                            break
                    test_files[test_file] = test_files.get(test_file, 0) + 1
                    
                    # Track labels
                    for label in labels:
                        label_name = label.get('name')
                        if label_name:
                            if label_name not in test_labels:
                                test_labels[label_name] = []
                            test_labels[label_name].append(label.get('value'))
                    
                    # Track slowest tests
                    slowest_tests.append({
                        'name': test_name,
                        'duration': duration_seconds
                    })
                    
                    if status == 'passed':
                        passed += 1
                        test_cases.append({
                            'name': test_name,
                            'status': 'passed',
                            'classname': 'Playwright.Chromium',
                            'duration': duration_seconds,
                            'test_file': test_file,
                            'steps': len(steps),
                            'labels': labels
                        })
                    elif status == 'failed':
                        failed += 1
                        error_msg = statusDetails.get('message', 'Test failed')
                        trace = statusDetails.get('trace', '')
                        test_cases.append({
                            'name': test_name,
                            'status': 'failed',
                            'classname': 'Playwright.Chromium',
                            'duration': duration_seconds,
                            'test_file': test_file,
                            'error': error_msg,
                            'trace': trace,
                            'steps': len(steps),
                            'labels': labels
                        })
                    elif status == 'skipped':
                        skipped += 1
                        test_cases.append({
                            'name': test_name,
                            'status': 'skipped',
                            'classname': 'Playwright.Chromium',
                            'duration': duration_seconds,
                            'test_file': test_file,
                            'steps': len(steps),
                            'labels': labels
                        })
                except json.JSONDecodeError:
                    print(f"Error parsing {filepath}")
                    continue
    
    total = passed + failed + skipped
    total_duration_seconds = total_duration / 1000.0
    
    # Create JUnit XML structure
    testsuites = Element('testsuites')
    testsuites.set('name', 'Playwright Test Suite')
    testsuites.set('tests', str(total))
    testsuites.set('failures', str(failed))
    testsuites.set('skipped', str(skipped))
    testsuites.set('time', str(total_duration_seconds))
    
    testsuite = SubElement(testsuites, 'testsuite')
    testsuite.set('name', 'Playwright Chromium Tests')
    testsuite.set('tests', str(total))
    testsuite.set('failures', str(failed))
    testsuite.set('skipped', str(skipped))
    testsuite.set('time', str(total_duration_seconds))
    
    # Add properties with detailed information
    properties = SubElement(testsuite, 'properties')
    
    prop1 = SubElement(properties, 'property')
    prop1.set('name', 'allure.results.available')
    prop1.set('value', 'true')
    
    prop2 = SubElement(properties, 'property')
    prop2.set('name', 'allure.results.dir')
    prop2.set('value', allure_dir)
    
    prop3 = SubElement(properties, 'property')
    prop3.set('name', 'report.timestamp')
    prop3.set('value', datetime.utcnow().isoformat() + 'Z')
    
    # Calculate additional metrics
    avg_duration = total_duration_seconds / total if total > 0 else 0
    pass_percentage = (passed / total * 100) if total > 0 else 0
    
    # Add performance metrics
    prop4 = SubElement(properties, 'property')
    prop4.set('name', 'metrics.total.duration.seconds')
    prop4.set('value', str(round(total_duration_seconds, 2)))
    
    prop5 = SubElement(properties, 'property')
    prop5.set('name', 'metrics.average.duration.seconds')
    prop5.set('value', str(round(avg_duration, 2)))
    
    prop6 = SubElement(properties, 'property')
    prop6.set('name', 'metrics.pass.percentage')
    prop6.set('value', str(round(pass_percentage, 2)))
    
    # Add test counts
    prop7 = SubElement(properties, 'property')
    prop7.set('name', 'metrics.tests.passed')
    prop7.set('value', str(passed))
    
    prop8 = SubElement(properties, 'property')
    prop8.set('name', 'metrics.tests.failed')
    prop8.set('value', str(failed))
    
    prop9 = SubElement(properties, 'property')
    prop9.set('name', 'metrics.tests.skipped')
    prop9.set('value', str(skipped))
    
    prop10 = SubElement(properties, 'property')
    prop10.set('name', 'metrics.tests.total')
    prop10.set('value', str(total))
    
    # Add browser and test info
    prop11 = SubElement(properties, 'property')
    prop11.set('name', 'test.browser')
    prop11.set('value', 'Chromium')
    
    prop12 = SubElement(properties, 'property')
    prop12.set('name', 'test.framework')
    prop12.set('value', 'Playwright')
    
    # Add test file information
    if test_files:
        slowest_file = max(test_files, key=test_files.get)
        prop13 = SubElement(properties, 'property')
        prop13.set('name', 'test.files.count')
        prop13.set('value', str(len(test_files)))
        
        prop14 = SubElement(properties, 'property')
        prop14.set('name', 'test.files.primary')
        prop14.set('value', slowest_file)
    
    # Add slowest test info
    if slowest_tests:
        slowest_tests.sort(key=lambda x: x['duration'], reverse=True)
        slowest = slowest_tests[0]
        prop15 = SubElement(properties, 'property')
        prop15.set('name', 'test.slowest.name')
        prop15.set('value', slowest['name'][:255])
        
        prop16 = SubElement(properties, 'property')
        prop16.set('name', 'test.slowest.duration')
        prop16.set('value', str(round(slowest['duration'], 2)))
        
        if len(slowest_tests) > 1:
            fastest = slowest_tests[-1]
            prop17 = SubElement(properties, 'property')
            prop17.set('name', 'test.fastest.name')
            prop17.set('value', fastest['name'][:255])
            
            prop18 = SubElement(properties, 'property')
            prop18.set('name', 'test.fastest.duration')
            prop18.set('value', str(round(fastest['duration'], 2)))
    
    # Add label/tag information
    if test_labels:
        for label_name, label_values in list(test_labels.items())[:5]:  # Top 5 labels
            unique_values = set(label_values)
            prop = SubElement(properties, 'property')
            prop.set('name', f'test.labels.{label_name}')
            prop.set('value', ', '.join(str(v) for v in list(unique_values)[:3]))
    
    # Add test cases with detailed information
    for test_case in test_cases:
        tc = SubElement(testsuite, 'testcase')
        tc.set('name', test_case['name'][:255])  # Limit name length
        tc.set('classname', test_case['classname'])
        tc.set('time', str(test_case.get('duration', 0)))
        
        # Add test case properties
        tc_props = SubElement(tc, 'properties')
        
        status_prop = SubElement(tc_props, 'property')
        status_prop.set('name', 'test.status')
        status_prop.set('value', test_case['status'])
        
        duration_prop = SubElement(tc_props, 'property')
        duration_prop.set('name', 'test.duration.seconds')
        duration_prop.set('value', str(round(test_case.get('duration', 0), 2)))
        
        # Add test file
        file_prop = SubElement(tc_props, 'property')
        file_prop.set('name', 'test.file')
        file_prop.set('value', test_case.get('test_file', 'Unknown'))
        
        # Add step count
        steps_prop = SubElement(tc_props, 'property')
        steps_prop.set('name', 'test.steps.count')
        steps_prop.set('value', str(test_case.get('steps', 0)))
        
        # Add labels/tags
        if test_case.get('labels'):
            labels_list = ', '.join([f"{l.get('name')}:{l.get('value')}" for l in test_case.get('labels', [])[:3]])
            labels_prop = SubElement(tc_props, 'property')
            labels_prop.set('name', 'test.labels')
            labels_prop.set('value', labels_list)
        
        if test_case['status'] == 'failed':
            failure = SubElement(tc, 'failure')
            failure.set('message', test_case.get('error', 'Test failed')[:255])
            failure.text = test_case.get('error', 'Test failed')
        elif test_case['status'] == 'skipped':
            skipped_elem = SubElement(tc, 'skipped')
            skipped_elem.set('message', 'Test skipped')
    
    # Write XML file
    tree = ElementTree(testsuites)
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    
    print(f"✓ JUnit report generated: {output_file}")
    print(f"\n📊 Test Execution Summary:")
    print(f"  Total: {total}, Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
    print(f"  Duration: {total_duration_seconds:.2f}s (Avg: {avg_duration:.2f}s per test)")
    print(f"  Pass Rate: {pass_percentage:.2f}%")
    print(f"\n📈 Test Breakdown:")
    print(f"    - Passed: {passed} ({(passed/total*100):.1f}%)" if total > 0 else "    - Passed: 0")
    print(f"    - Failed: {failed} ({(failed/total*100):.1f}%)" if total > 0 else "    - Failed: 0")
    print(f"    - Skipped: {skipped} ({(skipped/total*100):.1f}%)" if total > 0 else "    - Skipped: 0")
    
    # Print slowest tests
    if slowest_tests:
        slowest_tests.sort(key=lambda x: x['duration'], reverse=True)
        print(f"\n⏱️  Performance Insights:")
        print(f"    - Slowest: {slowest_tests[0]['name'][:50]} ({slowest_tests[0]['duration']:.2f}s)")
        if len(slowest_tests) > 1:
            print(f"    - Fastest: {slowest_tests[-1]['name'][:50]} ({slowest_tests[-1]['duration']:.2f}s)")
    
    # Print test file info
    if test_files:
        print(f"\n📁 Test Files:")
        for file, count in sorted(test_files.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {file}: {count} tests")
    
    return True

if __name__ == '__main__':
    allure_dir = sys.argv[1] if len(sys.argv) > 1 else 'target/allure-results'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'test-results/junit-report.xml'
    
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    if generate_junit_report(allure_dir, output_file):
        sys.exit(0)
    else:
        sys.exit(1)
