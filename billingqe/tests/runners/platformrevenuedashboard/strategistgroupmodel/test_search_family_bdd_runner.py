"""BDD runner for Search Family scenario.

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
		/ "search_family_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def search_family_data_row(request):
	return request.param


@pytest.mark.search
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize(
	"search_family_data_row",
	_ROWS,
	ids=[row.get("case_id", f"row-{idx}") for idx, row in enumerate(_ROWS, start=1)],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "search_family.feature"), "Search Family matrix with ALL/Pending/Rejected filters")
def test_search_family_matrix_with_allpendingrejected_filters(search_family_data_row):
	pass
