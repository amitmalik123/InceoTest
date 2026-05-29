"""BDD runner for Edit Model scenario.

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
		/ "edit_model_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def edit_model_data_row(request):
	return request.param


@pytest.mark.edit_model
@pytest.mark.edit
@pytest.mark.regression
@pytest.mark.parametrize(
	"edit_model_data_row",
	_ROWS,
	ids=[row.get("case_id") or f"row-{idx}" for idx, row in enumerate(_ROWS, start=1)],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "edit_model.feature"), "Edit Model entry to update Family Name")
def test_edit_model_entry_to_update_family_name(edit_model_data_row):
	pass
