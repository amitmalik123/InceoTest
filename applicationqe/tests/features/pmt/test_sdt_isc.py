"""Test runner for the PMT SDT ISC BDD scenario.

Bound to the feature file colocated in ``tests/features/pmt/`` and the step
definitions in ``tests/steps/pmt/`` so the PMT suite is self-contained and
does not depend on the BAW copies of these files.
"""

from pathlib import Path

from pytest_bdd import scenarios

# Import step definitions so pytest-bdd can resolve them
from tests.steps.pmt.sdt_isc_steps import *  # noqa: F401,F403

FEATURE_FILE = Path(__file__).resolve().parent / "sdt_isc.feature"

scenarios(str(FEATURE_FILE))
