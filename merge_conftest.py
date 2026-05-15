import subprocess

r = subprocess.run(['git', 'show', 'ES2PlaywrightPython:tests/conftest.py'], capture_output=True)
content = r.stdout.decode('utf-8')

# 1. Fix fixtures import path: tests.fixtures -> fixtures.STP
content = content.replace(
    'from tests.fixtures import *  # noqa: F401, F403',
    'from fixtures.STP import *  # noqa: F401, F403',
)

# 2. Insert sys.path setup after logger line so STP monorepo root is on path
stp_path_setup = (
    '\n'
    '# Ensure applicationqe root is in path for STP monorepo structure\n'
    '_APP_ROOT = Path(__file__).resolve().parent.parent\n'
    'if str(_APP_ROOT) not in __import__("sys").path:\n'
    '    __import__("sys").path.insert(0, str(_APP_ROOT))\n'
)
marker = 'logger = logging.getLogger(__name__)'
content = content.replace(marker, marker + stp_path_setup, 1)

# 3. Append vcr_config fixture (present in STP original, not in ES2)
vcr_fixture = (
    '\n\n'
    '@pytest.fixture\n'
    'def vcr_config():\n'
    '    """VCR configuration for recording HTTP interactions"""\n'
    '    return {"filter_headers": ["authorization"]}\n'
)
content = content.rstrip() + vcr_fixture

with open('applicationqe/tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(content)

lines = content.count('\n')
fix = [l for l in content.split('\n') if 'fixtures' in l and 'import' in l]
print('Lines written:', lines)
print('Fixtures import line:', fix)
print('sys.path setup present:', '_APP_ROOT' in content)
print('vcr_config present:', 'vcr_config' in content)
