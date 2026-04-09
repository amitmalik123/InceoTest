"""
Test Data Fixtures

Provides fixtures for loading and managing test data with scalable query capabilities.
"""

from typing import Dict, List, Optional

import pytest

from config.settings import settings


class TestDataManager:
    """
    Scalable test data manager with flexible query capabilities.

    Query by ANY field, filter multiple rows, and easily access test data.
    """

    def __init__(self, data_rows: List[Dict[str, str]]):
        """Initialize with all test data rows."""
        self._data = data_rows

    def get_by(self, **criteria) -> Optional[Dict[str, str]]:
        """
        Get FIRST row matching ALL criteria.

        Args:
            **criteria: Field-value pairs to match

        Returns:
            dict: First matching row, or None

        Examples:
            data.get_by(test_scenario="add_ach")
            data.get_by(user_type="advisor", test_scenario="add_ach")
            data.get_by(username="T11_User2_Test")
        """
        for row in self._data:
            if all(row.get(key) == value for key, value in criteria.items()):
                return row
        return None

    def filter_by(self, **criteria) -> List[Dict[str, str]]:
        """
        Get ALL rows matching ALL criteria.

        Args:
            **criteria: Field-value pairs to match

        Returns:
            list[dict]: All matching rows

        Examples:
            data.filter_by(user_type="advisor")  # All advisor users
            data.filter_by(test_scenario="roth_conversion")
        """
        matches = []
        for row in self._data:
            if all(row.get(key) == value for key, value in criteria.items()):
                matches.append(row)
        return matches

    def get_all(self) -> List[Dict[str, str]]:
        """Get all test data rows"""
        return self._data

    def get_scenarios(self) -> List[str]:
        """Get list of unique test scenarios"""
        return list(
            {row.get("test_scenario", "") for row in self._data if row.get("test_scenario")}
        )

    def get_user_types(self) -> List[str]:
        """Get list of unique user types"""
        return list({row.get("user_type", "") for row in self._data if row.get("user_type")})

    def __len__(self):
        """Return number of data rows"""
        return len(self._data)

    def __getitem__(self, index):
        """Allow indexing: data[0], data[1], etc."""
        return self._data[index]


# NOTE: test_context fixture moved to tests/bdd/steps/conftest.py
# to properly include test_data. Do not redefine here.


@pytest.fixture(scope="session")
def test_data_manager(excel_data_manager: "ExcelDataManager") -> TestDataManager:
    """
    Scalable test data manager backed by Excel data (session scope - loaded once).

    Returns:
        TestDataManager: Manager with query capabilities

    Examples:
        # Get by any field
        data.get_by(test_scenario="add_ach")
        data.get_by(user_type="advisor")
        data.get_by(username="T11_User2_Test")

        # Filter multiple rows
        advisors = data.filter_by(user_type="advisor")

        # Get all scenarios
        scenarios = data.get_scenarios()
    """
    from utils.logger import setup_logger

    logger = setup_logger(__name__)
    data_rows: List[Dict[str, str]] = []

    for sheet_name in excel_data_manager.sheet_names:
        for row_number, row_data in enumerate(excel_data_manager.get_sheet(sheet_name), start=2):
            enriched_row = dict(row_data)
            enriched_row.setdefault("SheetName", sheet_name)
            enriched_row.setdefault("RowNumber", row_number)
            data_rows.append(enriched_row)

    logger.info(
        f"[SESSION SCOPE] Loaded {len(data_rows)} Excel-backed test data row(s) "
        f"from sheets: {excel_data_manager.sheet_names}"
    )

    # Show available scenarios and user types
    manager = TestDataManager(data_rows)
    logger.info(f"[SESSION SCOPE] Available scenarios: {manager.get_scenarios()}")
    logger.info(f"[SESSION SCOPE] Available user types: {manager.get_user_types()}")

    return manager


class ExcelDataManager:
    """
    Manages Excel test data loaded once at session scope.
    Loads all sheets from the Excel file and provides dict-based access.
    """

    def __init__(self, excel_path: str):
        """Load all sheets from the Excel file."""
        import openpyxl

        self._sheets: Dict[str, List[Dict]] = {}
        wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            if rows:
                headers = [str(h).strip() for h in rows[0]]
                data = [
                    dict(zip(headers, row)) for row in rows[1:] if any(v is not None for v in row)
                ]
                self._sheets[sheet_name] = data

        wb.close()

    @property
    def sheet_names(self) -> List[str]:
        """Get all available sheet names."""
        return list(self._sheets.keys())

    def get_sheet(self, sheet_name: str) -> List[Dict]:
        """Get all rows from a sheet as list of dicts."""
        if sheet_name not in self._sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available: {self.sheet_names}")
        return self._sheets[sheet_name]

    def get_row(self, sheet_name: str, index: int = 0) -> Dict:
        """Get a specific row from a sheet by index."""
        sheet = self.get_sheet(sheet_name)
        if index >= len(sheet):
            raise IndexError(
                f"Row index {index} out of range. Sheet '{sheet_name}' has {len(sheet)} rows."
            )
        return sheet[index]

    def get_value(self, sheet_name: str, row_index: int, column_name: str):
        """Get a specific cell value by sheet, row index, and column name."""
        row = self.get_row(sheet_name, row_index)
        if column_name not in row:
            raise KeyError(f"Column '{column_name}' not found. Available: {list(row.keys())}")
        return row[column_name]


@pytest.fixture(scope="session")
def excel_data_manager() -> ExcelDataManager:
    """
    Session-scoped fixture that loads the Excel file once per test session.
    File path is resolved from environment config (data.test_data_excel).

    Usage:
        def step(excel_data_manager):
            shell_data = excel_data_manager.get_sheet("Shell")
            value = excel_data_manager.get_value("Shell", 0, "ColumnName")
    """
    from utils.logger import setup_logger

    logger = setup_logger(__name__)

    excel_path = settings.test_data_excel
    if not excel_path or not excel_path.exists():
        raise FileNotFoundError(
            f"Excel test data file not found: {excel_path}. "
            "Add 'test_data_excel' to data section in env config."
        )

    logger.info(f"[SESSION SCOPE] Loading Excel data from: {excel_path}")
    manager = ExcelDataManager(str(excel_path))
    logger.info(f"[SESSION SCOPE] Loaded sheets: {manager.sheet_names}")

    for sheet in manager.sheet_names:
        rows = manager.get_sheet(sheet)
        logger.info(f"[SESSION SCOPE] Sheet '{sheet}': {len(rows)} rows")

    return manager
