Allure Report - Generation and Troubleshooting
===========================================

This document explains how to generate and serve the Allure HTML report locally (Windows PowerShell) and in CI, and includes common troubleshooting tips.

1. Prerequisites
- Python test run has produced Allure results under `reports/allure-results/`.
- Node/npm is available if you plan to install the Allure CLI via npm.
- Alternatively, the Allure Commandline binary is installed and available on PATH.

2. Common commands (Windows PowerShell)

- Generate the report (non-interactive):

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
```

- Generate and immediately open in default browser:

```powershell
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

- Serve the report (single command that generates and starts a local server):

```powershell
allure serve reports/allure-results
```

Notes:
- `allure serve` will generate a temporary report and start a local web server, then open a browser. The command requires the `allure` CLI on PATH.

3. If `allure` is not recognized

- Install via npm (requires node + npm):

```powershell
npm install -g allure-commandline --no-fund --no-audit
```

- If you installed via npm and PowerShell still says `allure` is not recognized, either open a new terminal (so the PATH is refreshed) or run the binary directly by locating it. On Windows the npm global binaries are commonly under `%AppData%\npm`.

Example (run directly from npm global folder):

```powershell
& "$env:APPDATA\npm\allure" generate reports/allure-results -o reports/allure-report --clean
```

4. CI / Non-interactive usage

- In CI you will typically generate the report artifacts and either publish the `reports/allure-report` folder as an artifact or use a static-site host.
- Example CI step (bash):

```bash
pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
# then publish reports/allure-report as an artifact
```

5. Troubleshooting

- No `reports/allure-results` produced: make sure pytest ran with the `--alluredir=reports/allure-results` option in `pyproject.toml` or CI command.
- Missing `allure` on PATH: either install the CLI (recommended via npm) or call the binary using the full path like shown above.
- Permission errors writing `reports/allure-report`: verify the folder isn't open in a program that locks files and that you have write permission.
- Old results are mixed with new ones: use `--clean` with `allure generate` to overwrite the destination.
- Browser doesn't open on `allure open` or `allure serve`: the commands will still generate the report; open `reports/allure-report/index.html` manually in a browser.

6. Local helper script

- This repo contains `generate_allure_report.bat` that runs the typical commands on Windows. If `allure` isn't found, follow the npm install step above and re-run the script in a new terminal.

7. Useful paths in this repo

- Allure results: `reports/allure-results/`
- Generated HTML report: `reports/allure-report/` (open `index.html`)
- Pytest HTML report (alternate): `reports/pytest_report.html`

8. Quick checklist

- [ ] Run tests with Allure directory: `pytest --alluredir=reports/allure-results`
- [ ] Generate: `allure generate reports/allure-results -o reports/allure-report --clean`
- [ ] Open: `allure open reports/allure-report` or open `reports/allure-report/index.html` manually
