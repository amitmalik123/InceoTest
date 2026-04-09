from pathlib import Path
import shutil
import openpyxl

base = Path('data')
target = base / 'Test11_data.xlsx'
backup = base / 'Test11_data.backup_before_reset.xlsx'

if not target.exists():
    print(f"FAILURE: Target workbook not found: {target}")
    raise SystemExit(1)

shutil.copy2(target, backup)
print(f"Backup created: {backup}")

wb = openpyxl.load_workbook(target)
reset_summary = []
for ws in wb.worksheets:
    original_max = ws.max_row
    if original_max >= 2:
        ws.delete_rows(2, original_max - 1)
    reset_summary.append((ws.title, ws.max_row))

wb.save(target)
wb.close()

print('Reset summary (after save):')
for name, remaining in reset_summary:
    print(f"- {name}: remaining max_row={remaining}")

verify_wb = openpyxl.load_workbook(target)
verification = []
all_ok = True
for ws in verify_wb.worksheets:
    mr = ws.max_row
    row1_has_data = any(cell.value is not None for cell in ws[1])
    ok = (mr == 1 and row1_has_data) or (mr == 1 and not row1_has_data) or (mr == 0)
    # openpyxl usually reports at least 1 row even when empty; treat 1 as valid.
    verification.append((ws.title, mr, row1_has_data, ok))
    if not ok:
        all_ok = False

verify_wb.close()

print('Verification summary (re-opened workbook):')
for name, mr, row1_has_data, ok in verification:
    hdr = 'header-present' if row1_has_data else 'header-empty'
    status = 'OK' if ok else 'FAIL'
    print(f"- {name}: max_row={mr}, {hdr}, {status}")

print('SUCCESS' if all_ok else 'FAILURE')
raise SystemExit(0 if all_ok else 2)
