"""BDD runner for Approve/Reject Family scenario.

Fixtures and step definitions are auto-provided by tests/conftest.py.
This runner only owns: CSV data loading + scenario/parametrize binding.
"""

import csv
from pathlib import Path

import pytest
from pytest_bdd import scenario

REPO_ROOT = Path(__file__).resolve().parents[4]  # billingqe/
FEATURE_DIR = (
    REPO_ROOT
    / "tests"
    / "features"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
)


def _load_rows():
	data_file = (
		REPO_ROOT
		/ "data"
		/ "platformrevenuedashboard"
		/ "strategistgroupmodel"
		/ "approve_reject_family_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def approve_reject_family_data_row(request):
	return request.param


@pytest.mark.approve_reject
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize(
	"approve_reject_family_data_row",
	_ROWS,
	ids=[
		f"{row.get('family_name', f'row-{idx}')}-{row.get('action', 'unknown')}"
		for idx, row in enumerate(_ROWS, start=1)
	],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "approve_reject_family.feature"), "Approve/Reject Family with valid data")
def test_approvereject_family_with_valid_data(approve_reject_family_data_row):
	pass
