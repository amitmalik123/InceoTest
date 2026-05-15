import subprocess, os

BASE = 'applicationqe/tests/api/STP'

# source -> destination (relative to BASE)
files = [
    ('tests/api/__init__.py',                          '__init__.py'),
    ('tests/api/conftest.py',                          'conftest.py'),
    ('tests/api/client/__init__.py',                   'client/__init__.py'),
    ('tests/api/client/apiClient.py',                  'client/apiClient.py'),
    ('tests/api/models/__init__.py',                   'models/__init__.py'),
    ('tests/api/models/beneficiaryHouseholdModel.py',  'models/beneficiaryHouseholdModel.py'),
    ('tests/api/services/__init__.py',                 'services/__init__.py'),
    ('tests/api/services/beneficiaryHouseholdService.py', 'services/beneficiaryHouseholdService.py'),
    ('tests/api/test_api_contract_examples.py',        'test_api_contract_examples.py'),
]

for src, dst_rel in files:
    r = subprocess.run(['git', 'show', f'ES2PlaywrightPython:{src}'], capture_output=True)
    content = r.stdout.decode('utf-8')

    # Update import paths that reference old ES2 locations
    content = content.replace(
        'from tests.api.models.',
        'from tests.api.STP.models.'
    )
    content = content.replace(
        'from tests.api.services.',
        'from tests.api.STP.services.'
    )
    content = content.replace(
        'from tests.api.client.',
        'from tests.api.STP.client.'
    )
    content = content.replace(
        'from config.api_endpoints import',
        'from config.stp.api_endpoints import'
    )

    dst = os.path.join(BASE, dst_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'OK: {dst_rel} ({len(content)} bytes)')

print('\nDone. Contents:')
for root, dirs, fnames in os.walk(BASE):
    for fname in fnames:
        print(' ', os.path.join(root, fname).replace(BASE + os.sep, ''))
