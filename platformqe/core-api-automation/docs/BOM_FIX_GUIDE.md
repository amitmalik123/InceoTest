# UTF-8 BOM Fix - Complete Solution

## The Problem
When editing JSON test case files in your editor, it saves them with a UTF-8 BOM (Byte Order Mark).
This causes pytest to fail with: `SKIPPED (got empty parameter set for (case))`

## ✅ AUTOMATIC FIX (RECOMMENDED)
**I've already implemented this for you!**

The `conftest.py` file now **automatically removes the BOM** before every test run.

**You don't need to do anything!** Just edit your test cases and run pytest normally:

```bash
pytest tests/test_api_generic.py --testcase-file testdata/models/testcases/TestCase_model_id_PATCH.json --env TSADEV
```

The BOM will be automatically removed before tests run.

## Manual Fix (If Needed)
If you ever need to manually fix the BOM issue:

```bash
python fix_json_bom.py
```

## Prevent BOM in VS Code (Optional)
To stop VS Code from adding BOM in the first place:

1. **Open Settings**: Press `Ctrl + ,`
2. **Search for**: `encoding`
3. **Find**: `Files: Encoding`
4. **Set to**: `utf8` (NOT `utf8bom`)

OR edit `.vscode/settings.json` (already created):
```json
{
    "files.encoding": "utf8"
}
```

## How to Check for BOM
Run this PowerShell command:
```powershell
$bytes = Get-Content -Path "testdata\models\testcases\TestCase_model_id_PATCH.json" -Encoding Byte -TotalCount 3
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "File HAS BOM" -ForegroundColor Red
} else {
    Write-Host "File is OK" -ForegroundColor Green
}
```

## usage examples:
```bash
# Fix single file
python -c "from framework.common.bom_utils import fix_bom; fix_bom('testdata/parties/testcases/test.json')"

# Fix all JSON files recursively
python -c "from framework.common.bom_utils import fix_bom_recursive; fix_bom_recursive('testdata')"

# CLI usage
python framework/common/bom_utils.py fix testdata/test.json
python framework/common/bom_utils.py fix-all testdata
```

## Summary
✅ **Auto-fix enabled in conftest.py** - Tests will always work, even with BOM
✅ **VS Code settings configured** - Prevents BOM from being added
✅ **Manual fix script available** - `fix_json_bom.py` for emergency use

**You can now edit your test cases freely and tests will always run!**
