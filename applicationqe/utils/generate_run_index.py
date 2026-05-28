"""Generate an HTML index for browsing all timestamped runs."""

import json
from pathlib import Path
from typing import List, Dict, Any
from utils.allure_run_manager import AllureRunManager


def generate_run_index_html(output_path: Path = None) -> None:
    """
    Generate an HTML index of all runs at reports/runs/index.html
    
    Args:
        output_path: Optional custom output path; defaults to reports/runs/index.html
    """
    if output_path is None:
        output_path = AllureRunManager.RUNS_BASE_DIR / "index.html"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load all runs and latest
    runs = AllureRunManager.list_all_runs()
    latest = AllureRunManager.load_latest_run()
    
    # Build HTML
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "  <title>All Test Runs</title>",
        "  <style>",
        "    * { margin: 0; padding: 0; box-sizing: border-box; }",
        "    body {",
        "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;",
        "      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
        "      min-height: 100vh;",
        "      padding: 20px;",
        "    }",
        "    .container {",
        "      max-width: 1200px;",
        "      margin: 0 auto;",
        "    }",
        "    header {",
        "      background: rgba(255, 255, 255, 0.95);",
        "      border-radius: 8px;",
        "      padding: 30px;",
        "      margin-bottom: 30px;",
        "      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);",
        "    }",
        "    h1 {",
        "      color: #333;",
        "      font-size: 28px;",
        "      margin-bottom: 10px;",
        "    }",
        "    .subtitle {",
        "      color: #666;",
        "      font-size: 14px;",
        "    }",
        "    .latest-section {",
        "      background: rgba(255, 255, 255, 0.95);",
        "      border-radius: 8px;",
        "      padding: 20px;",
        "      margin-bottom: 30px;",
        "      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);",
        "      border-left: 4px solid #667eea;",
        "    }",
        "    .latest-section h2 {",
        "      color: #333;",
        "      font-size: 18px;",
        "      margin-bottom: 15px;",
        "    }",
        "    .latest-row {",
        "      display: grid;",
        "      grid-template-columns: 1fr 1fr 1fr 1fr;",
        "      gap: 15px;",
        "      margin-bottom: 10px;",
        "      font-size: 13px;",
        "    }",
        "    .latest-stat {",
        "      display: flex;",
        "      flex-direction: column;",
        "    }",
        "    .latest-stat .label {",
        "      color: #999;",
        "      font-size: 11px;",
        "      text-transform: uppercase;",
        "      letter-spacing: 0.5px;",
        "      margin-bottom: 5px;",
        "    }",
        "    .latest-stat .value {",
        "      color: #333;",
        "      font-weight: 600;",
        "      font-size: 14px;",
        "    }",
        "    .pass { color: #10b981; }",
        "    .fail { color: #ef4444; }",
        "    .runs-section {",
        "      background: rgba(255, 255, 255, 0.95);",
        "      border-radius: 8px;",
        "      overflow: hidden;",
        "      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);",
        "    }",
        "    .runs-header {",
        "      background: #f3f4f6;",
        "      padding: 15px 20px;",
        "      border-bottom: 1px solid #e5e7eb;",
        "    }",
        "    .runs-header h2 {",
        "      color: #333;",
        "      font-size: 16px;",
        "    }",
        "    .runs-list {",
        "      max-height: 600px;",
        "      overflow-y: auto;",
        "    }",
        "    .run-item {",
        "      display: grid;",
        "      grid-template-columns: 150px 1fr 80px 120px;",
        "      gap: 15px;",
        "      align-items: center;",
        "      padding: 15px 20px;",
        "      border-bottom: 1px solid #e5e7eb;",
        "      font-size: 13px;",
        "      transition: background 0.2s;",
        "    }",
        "    .run-item:hover {",
        "      background: #f9fafb;",
        "    }",
        "    .run-item:last-child {",
        "      border-bottom: none;",
        "    }",
        "    .run-timestamp {",
        "      font-family: 'Monaco', 'Courier New', monospace;",
        "      color: #333;",
        "      font-weight: 500;",
        "    }",
        "    .run-time {",
        "      color: #999;",
        "    }",
        "    .run-flows {",
        "      color: #666;",
        "    }",
        "    .run-scenario-count {",
        "      text-align: right;",
        "      color: #999;",
        "    }",
        "    .run-link {",
        "      display: inline-block;",
        "      padding: 6px 12px;",
        "      background: #667eea;",
        "      color: white;",
        "      border-radius: 4px;",
        "      text-decoration: none;",
        "      font-size: 12px;",
        "      font-weight: 500;",
        "      transition: background 0.2s;",
        "    }",
        "    .run-link:hover {",
        "      background: #764ba2;",
        "    }",
        "    .empty-state {",
        "      text-align: center;",
        "      padding: 40px 20px;",
        "      color: #999;",
        "    }",
        "    .footer {",
        "      text-align: center;",
        "      color: rgba(255, 255, 255, 0.8);",
        "      font-size: 12px;",
        "      margin-top: 20px;",
        "    }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='container'>",
        "    <header>",
        "      <h1>📊 All Test Runs</h1>",
        "      <p class='subtitle'>Timestamped Scenario-Based Allure Reports</p>",
        "    </header>",
    ]
    
    # Latest section
    if latest:
        html_lines.extend([
            "    <div class='latest-section'>",
            "      <h2>⭐ Latest Run</h2>",
            "      <div class='latest-row'>",
            f"        <div class='latest-stat'><div class='label'>Timestamp</div><div class='value'>{latest.get('display_timestamp', 'N/A')}</div></div>",
            f"        <div class='latest-stat'><div class='label'>Flows</div><div class='value'>{', '.join(latest.get('flows', []))}</div></div>",
            f"        <div class='latest-stat'><div class='label'>Scenarios</div><div class='value pass'>{latest.get('passed_scenarios', 0)} ✓</div></div>",
            f"        <div class='latest-stat'><div class='label'>Failed</div><div class='value fail'>{latest.get('failed_scenarios', 0)} ✗</div></div>",
            "      </div>",
            f"      <a href='{latest.get('manifest_path')}' class='run-link'>View Manifest</a>",
            "    </div>",
        ])
    
    # Runs list
    if runs:
        html_lines.extend([
            "    <div class='runs-section'>",
            "      <div class='runs-header'><h2>All Runs</h2></div>",
            "      <div class='runs-list'>",
        ])
        
        for run in runs:
            manifest = AllureRunManager.load_run_manifest(run["timestamp"])
            if manifest:
                passed = sum(
                    len([s for s in scenarios if s.get("status") == "passed"])
                    for scenarios in manifest.get("flows", {}).values()
                )
                failed = sum(
                    len([s for s in scenarios if s.get("status") == "failed"])
                    for scenarios in manifest.get("flows", {}).values()
                )
                flows = ", ".join(manifest.get("flows", {}).keys())
                total = passed + failed
                
                html_lines.extend([
                    "        <div class='run-item'>",
                    f"          <div class='run-timestamp'>{run['timestamp']}</div>",
                    f"          <div class='run-flows'>{flows}</div>",
                    f"          <div class='run-scenario-count'>{total} tests</div>",
                    f"          <a href='{run['manifest_path']}' class='run-link'>Details →</a>",
                    "        </div>",
                ])
        
        html_lines.append("      </div>")
        html_lines.append("    </div>")
    else:
        html_lines.extend([
            "    <div class='empty-state'>",
            "      <p>No runs found yet. Execute:</p>",
            "      <p><code>python tests/e2e/run_journal_flows.py test11</code></p>",
            "    </div>",
        ])
    
    html_lines.extend([
        "    <div class='footer'>",
        "      <p>Generated at " + AllureRunManager.generate_run_timestamp().replace("_", " at ") + "</p>",
        "    </div>",
        "  </div>",
        "</body>",
        "</html>",
    ])
    
    # Write file
    html_content = "\n".join(html_lines)
    output_path.write_text(html_content, encoding="utf-8")
    print(f"✓ Generated run index at {output_path}")


if __name__ == "__main__":
    generate_run_index_html()
    print(f"\nOpen in browser: {AllureRunManager.RUNS_BASE_DIR / 'index.html'}")
