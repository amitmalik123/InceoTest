from flask import Flask, render_template, request, redirect, url_for, flash, Response
import os
import glob
import json
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'testcase_secret_key'



# Recursively get all subfolders under testdata

def get_testdata_folders(base=None):
    if base is None:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testdata'))
    folders = []
    for root, dirs, _ in os.walk(base):
        for d in dirs:
            rel = os.path.relpath(os.path.join(root, d), base)
            folders.append(rel)
    return folders



# Get all files (not just testcases) for a given folder (relative to testdata)

def get_files_for_folder(folder):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testdata'))
    folder_path = os.path.join(base, folder) if folder else base
    files = []
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            files.append(os.path.join(root, f))
    return files

def get_all_testcase_files():
    # For backward compatibility, return all files in all folders
    files = []
    for folder in get_testdata_folders():
        files.extend(get_testcase_files_for_folder(folder))
    return files

def load_testcases(file_path):
    if not file_path or not os.path.exists(file_path):
        return [], file_path
    ext = os.path.splitext(file_path)[1].lower()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if ext == '.json':
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]
                    return data, file_path
                except Exception:
                    f.seek(0)
                    content = f.read()
                    return [content], file_path
            elif ext == '.csv':
                import csv
                reader = csv.DictReader(f)
                data = list(reader)
                return data, file_path
            elif ext in ['.txt', '.sql']:
                lines = f.readlines()
                return [line.rstrip('\n') for line in lines], file_path
            else:
                content = f.read()
                return [content], file_path
    except Exception:
        return [], file_path

def save_testcases(file_path, testcases):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.json':
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(testcases, f, indent=4)
    elif ext == '.csv':
        import csv
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            if testcases and isinstance(testcases[0], dict):
                writer = csv.DictWriter(f, fieldnames=testcases[0].keys())
                writer.writeheader()
                writer.writerows(testcases)
            else:
                for row in testcases:
                    f.write(str(row) + '\n')
    elif ext in ['.txt', '.sql']:
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in testcases:
                f.write(str(line) + '\n')
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in testcases:
                f.write(str(line) + '\n')

    
    

# Home page with file selection and test case table for selected file



@app.route('/', methods=['GET', 'POST'])
def index():
    folders = get_testdata_folders()
    folder_options = [{'value': f, 'label': f.replace(os.sep, ' / ')} for f in folders]
    selected_folder = request.args.get('folder') or (folders[0] if folders else None)
    files = get_files_for_folder(selected_folder) if selected_folder else []
    selected_file = request.args.get('file') or (files[0] if files else None)
    testcases, _ = load_testcases(selected_file) if selected_file else ([], None)
    return render_template('index.html', testcases=testcases, files=files, selected_file=selected_file, folders=folder_options, selected_folder=selected_folder)




@app.route('/testcase/<path:file>/<test_id>')
def view_testcase(file, test_id):
    file = file.rstrip('/\\')
    cases, _ = load_testcases(file)
    # Try to find by test_id for dicts, else fallback to index
    case = None
    if cases and isinstance(cases[0], dict):
        case = next((c for c in cases if str(c.get('test_id')) == str(test_id)), None)
    if case is None:
        try:
            idx = int(test_id)
            if 0 <= idx < len(cases):
                case = cases[idx]
        except Exception:
            pass
    if case is None:
        flash('Row not found.', 'danger')
        return redirect(url_for('index', file=file))
    return render_template('view.html', testcase=case, file=file)




@app.route('/testcase/<path:file>/<test_id>/edit', methods=['GET', 'POST'])
def edit_testcase(file, test_id):
    file = file.rstrip('/\\')
    cases, _ = load_testcases(file)
    idx = None
    if cases and isinstance(cases[0], dict):
        idx = next((i for i, c in enumerate(cases) if str(c.get('test_id')) == str(test_id)), None)
    if idx is None:
        try:
            idx = int(test_id)
            if not (0 <= idx < len(cases)):
                idx = None
        except Exception:
            idx = None
    if idx is None:
        flash('Row not found.', 'danger')
        return redirect(url_for('index', file=file))
    if request.method == 'POST':
        if isinstance(cases[idx], dict):
            for key in cases[idx]:
                if key != '__file' and key != 'test_id':
                    cases[idx][key] = request.form.get(key, cases[idx][key])
        else:
            cases[idx] = request.form.get('row_value', cases[idx])
        save_testcases(file, cases)
        flash('Row updated.', 'success')
        return redirect(url_for('view_testcase', file=file, test_id=test_id))
    # Pass as 'row' for non-dict, 'testcase' for dict for template compatibility
    if isinstance(cases[idx], dict):
        return render_template('edit.html', testcase=cases[idx], file=file)
    else:
        return render_template('edit.html', row=cases[idx], row_id=idx, file=file)


@app.route('/testcase/<path:file>/new', methods=['GET', 'POST'])
def new_testcase(file):
    cases, _ = load_testcases(file)
    ext = os.path.splitext(file)[1].lower()
    if request.method == 'POST':
        if ext == '.json':
            new_case = {k: v for k, v in request.form.items()}
            # Generate unique test_id
            existing_ids = {str(c.get('test_id')) for c in cases if isinstance(c, dict)}
            i = 1
            while True:
                new_id = f"TC{i:03d}"
                if new_id not in existing_ids:
                    break
                i += 1
            new_case['test_id'] = new_id
            cases.append(new_case)
        elif ext == '.csv':
            # Add a new row as dict or string
            if cases and isinstance(cases[0], dict):
                new_case = {k: v for k, v in request.form.items()}
                cases.append(new_case)
            else:
                cases.append(request.form.get('row_value', ''))
        elif ext in ['.txt', '.sql']:
            cases.append(request.form.get('row_value', ''))
        else:
            cases.append(request.form.get('row_value', ''))
        save_testcases(file, cases)
        flash('Test case created.', 'success')
        return redirect(url_for('index', file=file))
    # Template for new row
    if ext == '.json' and cases and isinstance(cases[0], dict):
        template = cases[0]
    elif ext == '.csv' and cases and isinstance(cases[0], dict):
        template = cases[0]
    else:
        template = {}
    return render_template('edit.html', testcase=template, file=file, new=True)




@app.route('/testcase/<path:file>/<test_id>/delete', methods=['POST'])
def delete_testcase(file, test_id):
    file = file.rstrip('/\\')
    cases, _ = load_testcases(file)
    idx = None
    if cases and isinstance(cases[0], dict):
        idx = next((i for i, c in enumerate(cases) if str(c.get('test_id')) == str(test_id)), None)
    if idx is None:
        try:
            idx = int(test_id)
            if not (0 <= idx < len(cases)):
                idx = None
        except Exception:
            idx = None
    if idx is not None:
        del cases[idx]
        save_testcases(file, cases)
        flash('Row deleted.', 'success')
    else:
        flash('Row not found.', 'danger')
    return redirect(url_for('index', file=file))

# Import/Export CSV
@app.route('/import_csv/<path:file>', methods=['POST'])
def import_csv(file):
    if 'csv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index', file=file))
    f = request.files['csv_file']
    if f.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index', file=file))
    ext = os.path.splitext(file)[1].lower()
    stream = StringIO(f.stream.read().decode('utf-8'))
    if ext in ['.txt', '.sql']:
        # Import as single column CSV
        reader = csv.reader(stream)
        cases = [row[0] for row in reader if row]
    else:
        reader = csv.DictReader(stream)
        cases = list(reader)
    save_testcases(file, cases)
    flash('CSV imported successfully.', 'success')
    return redirect(url_for('index', file=file))

@app.route('/export_csv/<path:file>')
def export_csv(file): 
    cases, _ = load_testcases(file)
    if not cases:
        flash('No test cases to export.', 'danger')
        return redirect(url_for('index', file=file))
    ext = os.path.splitext(file)[1].lower()
    si = StringIO()
    if ext in ['.txt', '.sql']:
        writer = csv.writer(si)
        for row in cases:
            writer.writerow([row])
    else:
        writer = csv.DictWriter(si, fieldnames=cases[0].keys())
        writer.writeheader()
        writer.writerows(cases)
    output = si.getvalue()
    # Use the selected file's base name (without extension) for the CSV file name
    base_name = os.path.splitext(os.path.basename(file))[0]
    csv_file_name = f"{base_name}.csv"
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={csv_file_name}"}
    )

# @app.route('/dashboard')
# def dashboard():
#     # ...existing dashboard logic...
#     return render_template('dashboard.html', results=[])

# @app.route('/testmanagement')
# def test_management():
#     # List files and folders in testdata directory
#     testdata_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testdata'))
#     items = []
#     if os.path.exists(testdata_dir):
#         for entry in os.listdir(testdata_dir):
#             entry_path = os.path.join(testdata_dir, entry)
#             items.append({
#                 'name': entry,
#                 'is_dir': os.path.isdir(entry_path)
#             })
#     return render_template('testManagement.html', items=items)

if __name__ == '__main__':
    app.run(debug=False)
