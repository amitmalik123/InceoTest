import json
import xml.etree.ElementTree as ET
import os
import base64
from datetime import datetime
from typing import List, Dict, Union
from framework.common.logger import get_logger

logger = get_logger(__name__)


def _encode_banner_image(is_data_comparison: bool = False):
    """Encode report banner as base64 for embedding in HTML reports."""
    try:
        if is_data_comparison:
            svg_banner = """
<svg xmlns='http://www.w3.org/2000/svg' width='1600' height='220' viewBox='0 0 1600 220'>
    <defs>
        <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
            <stop offset='0%' stop-color='#0f172a'/>
            <stop offset='60%' stop-color='#1e293b'/>
            <stop offset='100%' stop-color='#334155'/>
        </linearGradient>
        <linearGradient id='accent' x1='0' y1='0' x2='1' y2='0'>
            <stop offset='0%' stop-color='#06b6d4'/>
            <stop offset='100%' stop-color='#22d3ee'/>
        </linearGradient>
    </defs>
    <rect width='1600' height='220' fill='url(#bg)'/>
    <rect x='0' y='0' width='1600' height='10' fill='url(#accent)'/>
    <g opacity='0.18' fill='#38bdf8'>
        <circle cx='1450' cy='60' r='42'/>
        <circle cx='1520' cy='120' r='28'/>
        <circle cx='1400' cy='150' r='22'/>
    </g>
    <text x='70' y='102' font-family='Segoe UI, Arial, sans-serif' font-size='54' font-weight='700' fill='#e2e8f0'>
        Database Test Execution Report
    </text>
    <text x='72' y='150' font-family='Segoe UI, Arial, sans-serif' font-size='28' fill='#94a3b8'>
        Data Comparison Validation Dashboard
    </text>
</svg>
"""
            encoded_svg = base64.b64encode(svg_banner.encode('utf-8')).decode('utf-8')
            return f'data:image/svg+xml;base64,{encoded_svg}'

        banner_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'APITestBanner.png')
        if os.path.exists(banner_path):
            with open(banner_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                return f'data:image/png;base64,{encoded}'
        else:
            logger.warning(f"Banner image not found at: {banner_path}")
            return None
    except Exception as e:
        logger.warning(f"Failed to encode banner image: {e}")
        return None

def _safe_log(log_func, *args, **kwargs):
    logger_obj = log_func.__self__ if hasattr(log_func, '__self__') else None
    if logger_obj and getattr(logger_obj, 'handlers', None):
        if any(getattr(h, 'stream', None) and not getattr(h.stream, 'closed', False) for h in logger_obj.handlers):
            try:
                log_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in _safe_log: {e}")
    else:
        pass


class Reporter:
    _singleton_run_marker = None
    _singleton_run_dir = None
    _singleton_allure_dir = None
    _current_run_dir = None
    _current_allure_dir = None
    _current_run_marker = None
    def _organize_report_dirs(self):
        # Only use one timestamped directory per session
        if Reporter._singleton_run_marker is None:
            Reporter._singleton_run_marker = datetime.now().strftime('%Y%m%d_%H%M%S')
            reports_dir = self.report_dir
            target_dir = os.path.join(reports_dir, Reporter._singleton_run_marker)
            allure_target = os.path.join(target_dir, 'allure-results')
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(allure_target, exist_ok=True)
            Reporter._singleton_run_dir = target_dir
            Reporter._singleton_allure_dir = allure_target
        self._current_run_marker = Reporter._singleton_run_marker
        self._current_run_dir = Reporter._singleton_run_dir
        self._current_allure_dir = Reporter._singleton_allure_dir
        return self._current_run_dir

    def _is_timestamp_folder(self, name):
        import re
        return re.match(r'^\d{8}_\d{6}$', name) is not None

    def _resolve_path(self, filename: str, timestamped: bool = False) -> str:
        return os.path.join(self._current_run_dir, filename)

    def __init__(self, report_dir='reports'):
        self.report_dir = report_dir
        self.archive_dir = os.path.join(report_dir, 'archive')
        os.makedirs(report_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        self._archive_old_reports()
        self._organize_report_dirs()  

    def write_html_report(self, testcases: List[Dict], results: List[Dict], filename='html_report.html', timestamped=False, main_url=None):
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{self._current_run_marker}{ext}"
        path = self._resolve_path(filename, True)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        merged = []
        iteration_counters = {}
        for result in results:
            test_id = result.get('test_id') or result.get('test_name') or ''
            if test_id not in iteration_counters:
                iteration_counters[test_id] = 1
            else:
                iteration_counters[test_id] += 1
            iteration_label = f"Iteration {iteration_counters[test_id]}"
            tc = next((tc for tc in testcases if tc.get('test_id') == result.get('test_id')), {})
            error_msg = result.get('error') or result.get('reason') or result.get('summary', '')
            summary = tc.get('test_summary') if tc.get('test_summary') else result.get('summary', '')
            status = result.get('status', result.get('outcome', '')).upper() if result.get('status') or result.get('outcome') else ''
            if status == 'FAIL' and error_msg:
                if summary and error_msg not in summary:
                    summary = f"{summary}\nError: {error_msg}"
                else:
                    summary = f"Error: {error_msg}" if not summary else summary
            merged.append({
                'iteration': iteration_label,
                'test_name': result.get('test_name') or tc.get('test_name') or result.get('test_id', ''),
                'service_name': result.get('service_name') or tc.get('service_name') or tc.get('workflow_mode', 'API'),
                'endpoint': result.get('endpoint') or tc.get('endpoint', ''),
                'method': result.get('method') or tc.get('method', ''),
                'main_url': result.get('main_url') or main_url or '',
                'status': status,
                'response_time': result.get('response_time') if result.get('response_time') is not None else result.get('duration', ''),
                'contract_check': result.get('contract_check', 'FAIL'),
                'security_checks': result.get('security_checks', 'PASS'),
                'custom_validations': result.get('custom_validations', 'PASS'),
                'data_comparison': result.get('data_comparison', 'N/A'),
                'summary': summary,
            })
        # Fallback: if merged is empty, add a minimal row
        if not merged:
            merged.append({
                'iteration': 'N/A',
                'test_name': 'No tests run',
                'service_name': '',
                'endpoint': '',
                'method': '',
                'main_url': '',
                'status': 'SKIPPED',
                'response_time': '',
                'contract_check': '',
                'security_checks': '',
                'custom_validations': '',
                'data_comparison': '',
                'summary': 'No test results available.'
            })
        total = len(merged)
        passed = sum(1 for entry in merged if entry.get("status", "").upper() == "PASS")
        failed = sum(1 for entry in merged if entry.get("status", "").upper() == "FAIL")
        skipped = sum(1 for entry in merged if entry.get("status", "").upper() == "SKIPPED")
        xfailed = sum(1 for entry in merged if entry.get("status", "").upper() == "XFAILED")
        xpassed = sum(1 for entry in merged if entry.get("status", "").upper() == "XPASSED")
        try:
            html = []
            html.append('<!DOCTYPE html>')
            html.append('<html lang="en">')
            html.append('<head>')
            html.append('<meta charset="UTF-8">')
            # html.append('<title>API Test Results Report</title>')
            html.append('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">')
            html.append('<style>')
            html.append('body { background: #f8f9fa; }')
            html.append('.table-success { background-color: #d4edda; }')
            html.append('.table-danger { background-color: #f8d7da; }')
            html.append('.table-warning { background-color: #fff3cd; }')
            html.append('/* Service grouping - apply to both tr and td for full coverage */')
            html.append('tr.table-success.service-group-light, tr.table-success.service-group-light > td { background-color: #d4edda !important; }')
            html.append('tr.table-success.service-group-dark, tr.table-success.service-group-dark > td { background-color: #85c995 !important; }')
            html.append('tr.table-danger.service-group-light, tr.table-danger.service-group-light > td { background-color: #f8d7da !important; }')
            html.append('tr.table-danger.service-group-dark, tr.table-danger.service-group-dark > td { background-color: #e8a1a8 !important; }')
            html.append('tr.table-warning.service-group-light, tr.table-warning.service-group-light > td { background-color: #fff3cd !important; }')
            html.append('tr.table-warning.service-group-dark, tr.table-warning.service-group-dark > td { background-color: #ffd966 !important; }')
            html.append('/* Disable Bootstrap hover effects for service grouped rows */')
            html.append('tr.service-group-light:hover, tr.service-group-dark:hover { background-color: inherit !important; }')
            html.append('tr.service-group-light:hover > td, tr.service-group-dark:hover > td { background-color: inherit !important; }')
            html.append('.summary { font-size: 1.1em; word-break: break-word; white-space: pre-wrap; }')
            html.append('table { table-layout: auto; width: 100%; overflow-x: auto; }')
            html.append('td, th { word-break: break-word; white-space: pre-wrap; max-width: 350px; }')
            html.append('.container { max-width: 100vw; }')
            html.append('.summary-box { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 1em 2em; margin-bottom: 1.5em; }')
            html.append('.banner-container { width: 100%; margin: -20px 0 2em 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }')
            html.append('.banner-container img { width: 100%; height: auto; display: block; }')
            html.append('</style>')
            html.append('</head>')
            html.append('<body>')
            html.append('<div class="container mt-5">')
            
            # Add banner image if available
            is_data_comparison = 'data_comparison' in str(self.report_dir).lower()
            banner_data = _encode_banner_image(is_data_comparison)
            if banner_data:
                html.append('<div class="banner-container">')
                banner_alt = 'Database Test Execution Report' if is_data_comparison else 'API Test Automation Banner'
                html.append(f'<img src="{banner_data}" alt="{banner_alt}"/>')
                html.append('</div>')
            
            # html.append('<h2 class="mb-4">API Test Results Report</h2>')
            html.append('<div class="summary-box">')
            html.append('<h4>Test Summary</h4>')
            html.append('<ul class="list-group list-group-horizontal">')
            html.append(f'<li class="list-group-item">Total: <strong>{total}</strong></li>')
            html.append(f'<li class="list-group-item">Passed: <strong>{passed}</strong></li>')
            html.append(f'<li class="list-group-item">Failed: <strong>{failed}</strong></li>')
            html.append(f'<li class="list-group-item">Skipped: <strong>{skipped}</strong></li>')
            html.append(f'<li class="list-group-item">Xfailed: <strong>{xfailed}</strong></li>')
            html.append(f'<li class="list-group-item">Xpassed: <strong>{xpassed}</strong></li>')
            html.append('</ul>')
            html.append('</div>')
            html.append('<div class="mb-3"><strong>Legend:</strong> <span class="table-success px-2">PASS</span> <span class="table-danger px-2">FAIL</span> <span class="table-warning px-2">SKIPPED</span></div>')
            html.append('<table class="table table-bordered table-hover">')
            html.append('<thead class="table-dark"><tr>')
            columns = ["Iteration", "Test Name", "Service Name", "Endpoint", "Method", "Main URL", "Status", "Response Time (ms)", "Contract Check", "Security Checks", "Custom Validations", "Comparison", "Summary"]
            for col in columns:
                html.append(f'<th>{col}</th>')
            html.append('</tr></thead><tbody>')
            current_service = None
            service_group_toggle = False
            for entry in merged:
                # Check if service_name changed
                if current_service != entry.get("service_name", ""):
                    current_service = entry.get("service_name", "")
                    service_group_toggle = not service_group_toggle
                
                # Determine status-based class
                status = entry.get("status", "")
                if status == "PASS":
                    row_class = "table-success"
                elif status == "FAIL":
                    row_class = "table-danger"
                elif status == "SKIPPED":
                    row_class = "table-warning"
                else:
                    row_class = ""
                
                # Add service grouping class
                service_class = "service-group-dark" if service_group_toggle else "service-group-light"
                full_class = f"{row_class} {service_class}".strip()
                
                html.append(f'<tr class="{full_class}">')
                html.append(f'<td>{entry.get("iteration", "")}</td>')
                html.append(f'<td>{entry.get("test_name", "")}</td>')
                html.append(f'<td>{entry.get("service_name", "")}</td>')
                html.append(f'<td>{entry.get("endpoint", "")}</td>')
                html.append(f'<td>{entry.get("method", "")}</td>')
                html.append(f'<td>{entry.get("main_url", "")}</td>')
                html.append(f'<td>{status}</td>')
                html.append(f'<td>{entry.get("response_time", "")}</td>')
                html.append(f'<td>{entry.get("contract_check", "")}</td>')
                html.append(f'<td>{entry.get("security_checks", "")}</td>')
                html.append(f'<td>{entry.get("custom_validations", "")}</td>')
                html.append(f'<td>{entry.get("data_comparison", "N/A")}</td>')
                html.append(f'<td class="summary">{entry.get("summary", "")}</td>')
                html.append('</tr>')
            html.append('</tbody></table>')
            html.append('</div></body></html>')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(html))
            print(f"[REPORT] HTML report written to {path}")
        except Exception as e:
            _safe_log(logger.error, f"Failed to write HTML report: {e}")

    def _archive_old_reports(self):
        """
        Moves only the previous run's timestamped folder from reports/ to reports/archive/.
        Keeps the current run folder in reports/.
        """
        import shutil
        reports_dir = self.report_dir
        archive_dir = self.archive_dir
        try:
            all_folders = [f for f in os.listdir(reports_dir)
                          if os.path.isdir(os.path.join(reports_dir, f))
                          and self._is_timestamp_folder(f)]
            for folder in all_folders:
                if folder != Reporter._singleton_run_marker:
                    src = os.path.join(reports_dir, folder)
                    dst = os.path.join(archive_dir, folder)
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    if os.path.exists(src):
                        shutil.move(src, dst)
                        logger.info(f"Archived previous run folder {folder} to {archive_dir}")
        except Exception as e:
            logger.error(f"Failed to archive previous run folders: {e}")

    def _resolve_path(self, filename: str, timestamped: bool = True) -> str:
        if self._current_run_dir is None:
            self._organize_report_dirs()
        return os.path.join(self._current_run_dir, filename)

    def write_junit_xml(self, results: List[Dict], filename=None, timestamped=True):
        if filename is None or not filename:
            filename = f"junit_report_{self._current_run_marker}.xml"
        path = self._resolve_path(filename, True)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Filter to include only 'call' phase results, excluding setup and teardown
        call_phase_results = [r for r in results if r.get('phase') == 'call']
        
        testsuite = ET.Element('testsuite')
        # Enhance: add summary statistics as attributes
        total = len(call_phase_results)
        passed = sum(1 for entry in call_phase_results if entry.get("outcome", "").upper() == "PASSED")
        failed = sum(1 for entry in call_phase_results if entry.get("outcome", "").upper() == "FAILED")
        skipped = sum(1 for entry in call_phase_results if entry.get("outcome", "").upper() == "SKIPPED")
        xfailed = sum(1 for entry in call_phase_results if entry.get("outcome", "").upper() == "XFAILED")
        xpassed = sum(1 for entry in call_phase_results if entry.get("outcome", "").upper() == "XPASSED")
        testsuite.attrib['total'] = str(total)
        testsuite.attrib['passed'] = str(passed)
        testsuite.attrib['failed'] = str(failed)
        testsuite.attrib['skipped'] = str(skipped)
        testsuite.attrib['xfailed'] = str(xfailed)
        testsuite.attrib['xpassed'] = str(xpassed)
        try:
            for result in call_phase_results:
                name = result.get('name', result.get('test_id', 'UnnamedTest'))
                classname = result.get('classname', 'TestClass')
                time_val = str(result.get('duration', '0'))
                outcome = result.get('outcome', '').upper()
                testcase = ET.SubElement(testsuite, 'testcase', name=name, classname=classname, time=time_val, outcome=outcome)
                if outcome == 'FAILED':
                    error_msg = result.get('error', result.get('reason', ''))
                    ET.SubElement(testcase, 'failure', message=error_msg)
                elif outcome == 'SKIPPED':
                    ET.SubElement(testcase, 'skipped')
                elif outcome == 'XFAILED':
                    ET.SubElement(testcase, 'xfailed')
                elif outcome == 'XPASSED':
                    ET.SubElement(testcase, 'xpassed')
            tree = ET.ElementTree(testsuite)
            tree.write(path, encoding='utf-8', xml_declaration=True)
            logger.info(f"JUnit XML report written to {path} (call phase only, {total} tests)")
        except Exception as e:
            logger.error(f"Failed to write JUnit XML report: {e}")

    def write_custom(self, data: List[Dict], filename=None, timestamped=True):
        if filename is None or not filename:
            filename = f"custom_report_{self._current_run_marker}.txt"
        try:
            from tabulate import tabulate
        except ImportError:
            logger.error("tabulate library is required for pretty custom reports. Please install it.")
            return
        path = self._resolve_path(filename, True)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        headers = [
            "Test Case",
            "Outcome",
            "Duration (s)",
            "Markers",
            "Parameters",
            "Phase",
            "Reason/Error"
        ]
        table = []
        for entry in data:
            test_id = entry.get("test_id", "")
            summary = entry.get("summary", "")
            # Combine test_id and summary for clarity
            if test_id and summary:
                test_case = f"{test_id} {summary}"
            elif test_id:
                test_case = test_id
            elif summary:
                test_case = summary
            else:
                test_case = entry.get("name", "")
            row = [
                test_case,
                entry.get("outcome", ""),
                entry.get("duration", ""),
                entry.get("markers", ""),
                entry.get("parameters", ""),
                entry.get("phase", ""),
                entry.get("reason", "")
            ]
            table.append(row)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(tabulate(table, headers=headers, tablefmt="grid", stralign="center", numalign="center"))
                f.write("\n\n")
                # Count all phases for summary statistics
                total = len(data)
                passed = sum(1 for entry in data if entry.get("outcome", "").upper() == "PASSED")
                failed = sum(1 for entry in data if entry.get("outcome", "").upper() == "FAILED")
                skipped = sum(1 for entry in data if entry.get("outcome", "").upper() == "SKIPPED")
                xfailed = sum(1 for entry in data if entry.get("outcome", "").upper() == "XFAILED")
                xpassed = sum(1 for entry in data if entry.get("outcome", "").upper() == "XPASSED")
                f.write("Summary:\n")
                f.write(f"Total: {total}\n")
                f.write(f"Passed: {passed}\n")
                f.write(f"Failed: {failed}\n")
                f.write(f"Skipped: {skipped}\n")
                f.write(f"Xfailed: {xfailed}\n")
                f.write(f"Xpassed: {xpassed}\n")
            logger.info(f"Custom report written to {path}")
        except Exception as e:
            logger.error(f"Failed to write custom report: {e}")

    def write_allure(self, results: List[Dict]):
        """
        Generates Allure-compatible JSON result files for each test result.
        Handles various status mappings, includes error details, parameters, and attachments if present.
        """
        import uuid
        import json
        if not self._current_allure_dir:
            self._organize_report_dirs()
            if not self._current_allure_dir:
                logger.error("_current_allure_dir is not set. Reporter must be initialized properly before writing allure results.")
                return
        allure_dir = self._current_allure_dir
        os.makedirs(allure_dir, exist_ok=True)
        allure_dir = self._current_allure_dir
        os.makedirs(allure_dir, exist_ok=True)
        status_map = {
            "PASSED": "passed",
            "FAILED": "failed",
            "SKIPPED": "skipped",
            "BROKEN": "broken",
            "XFAILED": "failed",
            "XPASSED": "passed"
        }

        for result in results:
            # Determine test name
            name = result.get('name') or result.get('test_name') or result.get('test_id') or 'UnnamedTest'
            test_uuid = result.get('uuid') if result.get('uuid') else str(uuid.uuid4())

            # Map status robustly
            outcome = str(result.get('outcome', '')).upper()
            status = status_map.get(outcome, None)
            if not status:
                # Fallback to 'success' or 'status' keys
                if result.get('success') is True or (isinstance(result.get('success'), str) and result.get('success').lower() == 'true'):
                    status = "passed"
                elif result.get('success') is False or (isinstance(result.get('success'), str) and result.get('success').lower() == 'false'):
                    status = "failed"
                else:
                    status = str(result.get('status', 'unknown')).lower()

            # Timestamps (milliseconds)
            start = int(float(result.get('start_time', 0)) * 1000)
            stop = int(float(result.get('end_time', 0)) * 1000)
            if not stop and result.get('duration'):
                stop = start + int(float(result.get('duration')) * 1000)

            # Status details
            status_details = {}
            error_msg = result.get('error') or result.get('reason') or result.get('summary', '')
            if error_msg:
                status_details['message'] = error_msg
            trace = result.get('traceback') or result.get('stacktrace')
            if trace:
                status_details['trace'] = trace

            # Parameters
            parameters = []
            params = result.get('parameters', {})
            if isinstance(params, dict):
                for k, v in params.items():
                    parameters.append({"name": k, "value": str(v)})
            elif isinstance(params, list):
                for param in params:
                    if isinstance(param, dict) and "name" in param and "value" in param:
                        parameters.append(param)

            # Attachments
            attachments = []
            attach_list = result.get('attachments', [])
            for attach in attach_list:
                if isinstance(attach, dict) and "name" in attach and "source" in attach:
                    attachments.append({
                        "name": attach["name"],
                        "source": attach["source"],
                        "type": attach.get("type", "text/plain")
                    })

            allure_result = {
                "uuid": test_uuid,
                "name": name,
                "status": status,
                "statusDetails": status_details,
                "stage": "finished",
                "start": start,
                "stop": stop,
                "steps": result.get('steps', []),
                "attachments": attachments,
                "parameters": parameters,
            }

            file_path = os.path.join(allure_dir, f"{test_uuid}-result.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(allure_result, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to write Allure result for {name}: {e}")

        logger.info(f"Allure results written to {allure_dir}")

    def write_json(self, data: Union[Dict, List], filename='json_report.json', timestamped=True):
        # Always append timestamp to filename
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{self._current_run_marker}{ext}"
        path = self._resolve_path(filename, True)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Enhance: add summary statistics like custom_report.txt
        try:
            report = {}
            report['results'] = data
            total = len(data)
            passed = sum(1 for entry in data if entry.get("outcome", "").upper() == "PASSED")
            failed = sum(1 for entry in data if entry.get("outcome", "").upper() == "FAILED")
            skipped = sum(1 for entry in data if entry.get("outcome", "").upper() == "SKIPPED")
            xfailed = sum(1 for entry in data if entry.get("outcome", "").upper() == "XFAILED")
            xpassed = sum(1 for entry in data if entry.get("outcome", "").upper() == "XPASSED")
            report['summary'] = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'xfailed': xfailed,
                'xpassed': xpassed
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"JSON report written to {path}")
        except Exception as e:
            logger.error(f"Failed to write JSON report: {e}")
        # Also generate allure-results for this test results report
        try:
            import uuid
            allure_dir = self._current_allure_dir
            os.makedirs(allure_dir, exist_ok=True)
            for entry in data:
                name = entry.get('name') or entry.get('test_name') or entry.get('test_id') or 'UnnamedTest'
                test_uuid = entry.get('uuid') if entry.get('uuid') else str(uuid.uuid4())
                status = 'passed' if entry.get('outcome', '').upper() == 'PASSED' else 'failed'
                start = int((entry.get('start_time', 0) or 0) * 1000)
                stop = int((entry.get('end_time', 0) or 0) * 1000)
                allure_result = {
                    "uuid": test_uuid,
                    "name": name,
                    "status": status,
                    "statusDetails": {
                        "message": entry.get('error', '')
                    },
                    "stage": "finished",
                    "start": start,
                    "stop": stop,
                    "steps": [],
                    "attachments": [],
                    "parameters": [],
                }
                file_path = os.path.join(allure_dir, f"{test_uuid}-result.json")
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(allure_result, f, indent=2)
                except Exception as e:
                    logger.error(f"Failed to write Allure result for {name}: {e}")
            logger.info(f"Allure results written to {allure_dir} for test results report JSON")
        except Exception as e:
            logger.error(f"Failed to generate allure-results for test results report JSON: {e}")
