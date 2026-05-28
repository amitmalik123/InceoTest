"""BDD runner for Search Model scenario.

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
		/ "search_model_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def search_model_data_row(request):
	return request.param


@pytest.mark.search_model
@pytest.mark.search
@pytest.mark.regression
@pytest.mark.parametrize(
	"search_model_data_row",
	_ROWS,
	ids=[row.get("case_id") or row.get("model_id") or f"row-{idx}" for idx, row in enumerate(_ROWS, start=1)],
	indirect=True,
)
@scenario(str(FEATURE_DIR / "search_model.feature"), "Search Model with status-action validation and no-record handling")
def test_search_model_with_statusaction_validation_and_norecord_handling(search_model_data_row):
	pass
