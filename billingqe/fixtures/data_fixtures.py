"""CSV-backed data fixtures for Billing test scenarios."""

import csv
import logging
from pathlib import Path
from typing import Dict, Optional

import pytest


logger = logging.getLogger(__name__)


class TestDataManager:
    """Flexible CSV data manager for querying row-based test data."""

    def __init__(self, data_rows: list[Dict[str, str]]):
        self._data = data_rows

    def get_by(self, **criteria) -> Optional[Dict[str, str]]:
        for row in self._data:
            if all(str(row.get(k, "")).strip() == str(v).strip() for k, v in criteria.items()):
                return row
        return None

    def filter_by(self, **criteria) -> list[Dict[str, str]]:
        return [
            row
            for row in self._data
            if all(str(row.get(k, "")).strip() == str(v).strip() for k, v in criteria.items())
        ]

    def get_all(self) -> list[Dict[str, str]]:
        return list(self._data)

    def get_column_values(self, column: str) -> list[str]:
        return list({str(row.get(column, "")).strip() for row in self._data if row.get(column)})

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index) -> Dict[str, str]:
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    @classmethod
    def from_csv(cls, csv_path: Path, encoding: str = "utf-8") -> "TestDataManager":
        if not csv_path.exists():
            raise FileNotFoundError(f"Test data CSV not found: {csv_path}")
        with open(csv_path, "r", encoding=encoding) as fh:
            rows = list(csv.DictReader(fh))
        logger.info("Loaded %d rows from %s", len(rows), csv_path)
        return cls(rows)


@pytest.fixture
def csv_data_manager():
    """Factory fixture that returns a TestDataManager for a CSV path."""

    def _factory(csv_path: Path, encoding: str = "utf-8") -> TestDataManager:
        return TestDataManager.from_csv(csv_path, encoding=encoding)

    return _factory
