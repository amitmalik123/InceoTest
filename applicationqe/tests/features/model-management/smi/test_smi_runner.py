"""
BDD test runner for Model Management (SMI) feature files.

Registers all .feature files in this directory as pytest tests and imports
all step definitions so pytest-bdd can resolve them.
"""
from pathlib import Path
import sys

from pytest_bdd import scenarios

# ---------------------------------------------------------------------------
# Ensure step definition packages are on sys.path
# ---------------------------------------------------------------------------
# Resolve applicationqe/ root (5 levels up from this file:
#   tests/features/model-management/smi/test_smi_runner.py → applicationqe/)
REPO_ROOT = Path(__file__).resolve().parents[4]
MM_STEPS_ROOT = REPO_ROOT / "tests" / "steps" / "model-management"
MM_SMI_ROOT = MM_STEPS_ROOT / "smi"
MM_FLOWS_DIR = MM_SMI_ROOT / "flows"
MM_VALIDATIONS_DIR = MM_SMI_ROOT / "validations"

for path in (REPO_ROOT, MM_STEPS_ROOT, MM_SMI_ROOT, MM_FLOWS_DIR, MM_VALIDATIONS_DIR):
    sys.path.insert(0, str(path))

# ---------------------------------------------------------------------------
# Import all step definition functions into this module's namespace so
# pytest-bdd can resolve them when generating scenario test functions.
# ---------------------------------------------------------------------------
from flows.smi_login_flow import *       # noqa: F401, F403, E402
from validations.smi_validations import * # noqa: F401, F403, E402

# ---------------------------------------------------------------------------
# Register every .feature file in this directory as a set of pytest tests
# ---------------------------------------------------------------------------
FEATURE_DIR = Path(__file__).parent
for _feature_file in sorted(FEATURE_DIR.glob("*.feature")):
    scenarios(_feature_file)
