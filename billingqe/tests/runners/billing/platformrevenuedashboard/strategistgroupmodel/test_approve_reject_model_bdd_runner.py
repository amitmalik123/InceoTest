"""BDD runner for Approve/Reject Model scenario.

Fixtures and step definitions are auto-provided by tests/conftest.py.
This runner only owns: CSV data loading + scenario/parametrize binding.
"""

import csv
from pathlib import Path

import pytest
from pytest_bdd import scenario

REPO_ROOT = Path(__file__).resolve().parents[5]  # billingqe/
FEATURE_DIR = (
    REPO_ROOT
    / "tests"
    / "features"
    / "billing"
    / "platformrevenuedashboard"
    / "strategistgroupmodel"
)


def _load_rows():
	data_file = (
		REPO_ROOT
		/ "data"
		/ "billing"
		/ "platformrevenuedashboard"
		/ "strategistgroupmodel"
		/ "approve_reject_model_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def approve_reject_model_data_row(request):
	return request.param


@pytest.mark.approve_reject
@pytest.mark.model
@pytest.mark.regression
@pytest.mark.parametrize(
	"approve_reject_model_data_row",
	_ROWS,
	ids=[
		f"{row.get('model_id', f'row-{idx}')}-{row.get('action', 'unknown')}"
		for idx, row in enumerate(_ROWS, start=1)
	],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "approve_reject_model.feature"), "Approve/Reject Model with valid data")
def test_approve_reject_model_with_valid_data(approve_reject_model_data_row):
	pass
