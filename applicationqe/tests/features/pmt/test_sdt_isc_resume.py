"""Test runner for the SDT ISC BAW-portal-only resume flow.

Reuses the step definitions in ``tests/steps/pmt/sdt_isc_steps.py`` and the
fixtures from ``tests/features/pmt/conftest.py``. Starts at the
"User launches SDT ISC process portal login page" step using the
``DEFAULT_B_NUMBER`` configured in ``sdt_isc_steps``.
"""

from pathlib import Path

from pytest_bdd import scenarios

# Import step definitions so pytest-bdd can resolve them
from tests.steps.pmt.sdt_isc_steps import *  # noqa: F401,F403

FEATURE_FILE = Path(__file__).resolve().parent / "sdt_isc_resume.feature"

scenarios(str(FEATURE_FILE))
