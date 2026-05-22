"""BDD runner for Create Family scenario.

Fixtures and step definitions are auto-provided by conftest.py in this folder.
This runner only owns: CSV data loading + scenario/parametrize binding.
"""

import csv
from pathlib import Path

import pytest
from pytest_bdd import scenario

REPO_ROOT = Path(__file__).resolve().parents[5]


def _load_rows():
	data_file = (
		REPO_ROOT
		/ "data"
		/ "billing"
		/ "platformrevenuedashboard"
		/ "strategistgroupmodel"
		/ "create_family_data.csv"
	)
	with open(data_file, "r", encoding="utf-8") as file:
		rows = list(csv.DictReader(file))
	if not rows:
		raise ValueError(f"{data_file} has no data rows")
	return rows


_ROWS = _load_rows()


@pytest.fixture
def create_family_data_row(request):
	return request.param


@pytest.mark.create
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize(
	"create_family_data_row",
	_ROWS,
	ids=[row.get("family_name", f"row-{idx}") for idx, row in enumerate(_ROWS, start=1)],
	indirect=True,
)
@scenario("create_family.feature", "Create Model Family with valid data")
def test_create_model_family_with_valid_data(create_family_data_row):
	pass
