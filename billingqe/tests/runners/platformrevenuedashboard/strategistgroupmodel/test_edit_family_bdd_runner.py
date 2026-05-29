"""BDD runner for Edit Family scenario.

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
		/ "edit_family_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = [
			row
			for row in csv.DictReader(file)
			if any(str(value or "").strip() for value in row.values())
		]
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def edit_family_data_row(request):
	return request.param


@pytest.mark.edit
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize(
	"edit_family_data_row",
	_ROWS,
	ids=[row.get("search_family_name", f"row-{idx}") for idx, row in enumerate(_ROWS, start=1)],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "edit_family.feature"), "Edit Family with valid data")
def test_edit_family_with_valid_data(edit_family_data_row):
	pass
