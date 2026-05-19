"""
Excel utility module for comprehensive Excel file operations.
"""

import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from utils.logger import setup_logger


class ExcelUtils:
    """Comprehensive utility class for Excel file operations."""

    # --- Test Execution Report ---
    _REPORT_COLUMNS = [
        "Test Case Id", "Title", "Last Run", "Run By", "B#",
        "hrcNumber", "nNumber", "parentBNumber", "activationNumber",
        "Status", "Feature", "Cause Of Failure",
        "Environment", "Start Time", "End Time", "Total Time",
    ]
    _BORDER = Border(*(Side(style="thin"),) * 4)
    _HDR_STYLE = {"font": Font(bold=True, size=11, color="FFFFFF"),
                  "fill": PatternFill("solid", fgColor="4472C4"),
                  "alignment": Alignment(horizontal="center", vertical="center", wrap_text=True)}
    _PASS_STYLE = {"fill": PatternFill("solid", fgColor="C6EFCE"), "font": Font(size=11, color="006100")}
    _FAIL_STYLE = {"fill": PatternFill("solid", fgColor="FFC7CE"), "font": Font(size=11, color="9C0006")}

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.workbook = None
        self.file_path = None
        self.test_results: List[dict] = []

    def create_workbook(self, file_path: str, sheet_names: Optional[List[str]] = None) -> bool:
        """
        Create a new Excel workbook.

        Args:
            file_path: Path for the new workbook
            sheet_names: Optional list of sheet names to create

        Returns:
            True if successful
        """
        try:
            wb = Workbook()

            # Remove default sheet
            if "Sheet" in wb.sheetnames:
                wb.remove(wb["Sheet"])

            # Create sheets
            if sheet_names:
                for sheet_name in sheet_names:
                    wb.create_sheet(title=sheet_name)
            else:
                wb.create_sheet(title="Sheet1")

            # Create directories if needed
            os.makedirs(
                os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True
            )

            wb.save(file_path)
            self.logger.info(f"Created new workbook: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating workbook: {str(e).splitlines()[0]}")
            raise

    def load_workbook(self, file_path: str, data_only: bool = False) -> Workbook:
        """
        Load an existing Excel workbook.

        Args:
            file_path: Path to the Excel file
            data_only: If True, formulas are converted to their values

        Returns:
            Workbook object
        """
        try:
            self.file_path = file_path
            self.workbook = load_workbook(file_path, data_only=data_only)
            self.logger.info(f"Loaded workbook: {file_path}")
            return self.workbook
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading workbook: {str(e).splitlines()[0]}")
            raise

    def save_workbook(self, file_path: Optional[str] = None) -> bool:
        """
        Save the current workbook.

        Args:
            file_path: Optional path to save to (uses loaded path if not provided)

        Returns:
            True if successful
        """
        try:
            if not self.workbook:
                raise ValueError("No workbook loaded")

            save_path = file_path or self.file_path
            if not save_path:
                raise ValueError("No file path specified")

            self.workbook.save(save_path)
            self.logger.info(f"Saved workbook: {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving workbook: {str(e).splitlines()[0]}")
            raise

    def close_workbook(self) -> bool:
        """
        Close the current workbook.

        Returns:
            True if successful
        """
        try:
            if self.workbook:
                self.workbook.close()
                self.workbook = None
                self.file_path = None
                self.logger.info("Closed workbook")
            return True
        except Exception as e:
            self.logger.error(f"Error closing workbook: {str(e).splitlines()[0]}")
            raise

    def read_sheet(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        header_row: int = 0,
        use_pandas: bool = False,
    ) -> Union[List[List], pd.DataFrame]:
        """
        Read data from a sheet.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name (uses first sheet if not provided)
            header_row: Row number for headers (0-indexed)
            use_pandas: Return pandas DataFrame instead of list

        Returns:
            List of rows or DataFrame
        """
        try:
            if use_pandas:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                self.logger.info(f"Read sheet with pandas: {sheet_name or 'first sheet'}")
                return df
            else:
                wb = load_workbook(file_path, data_only=True)
                sheet = wb[sheet_name] if sheet_name else wb.active

                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(list(row))

                wb.close()
                self.logger.info(f"Read {len(data)} rows from sheet: {sheet.title}")
                return data
        except Exception as e:
            self.logger.error(f"Error reading sheet: {str(e).splitlines()[0]}")
            raise

    def write_sheet(
        self,
        file_path: str,
        data: Union[List[List], pd.DataFrame],
        sheet_name: str = "Sheet1",
        headers: Optional[List[str]] = None,
        start_row: int = 1,
        start_col: int = 1,
    ) -> bool:
        """
        Write data to a sheet.

        Args:
            file_path: Path to the Excel file
            data: Data to write (list of lists or DataFrame)
            sheet_name: Sheet name
            headers: Optional column headers
            start_row: Starting row (1-indexed)
            start_col: Starting column (1-indexed)

        Returns:
            True if successful
        """
        try:
            # Create or load workbook
            if os.path.exists(file_path):
                wb = load_workbook(file_path)
                if sheet_name in wb.sheetnames:
                    sheet = wb[sheet_name]
                else:
                    sheet = wb.create_sheet(title=sheet_name)
            else:
                wb = Workbook()
                if "Sheet" in wb.sheetnames:
                    wb.remove(wb["Sheet"])
                sheet = wb.create_sheet(title=sheet_name)

            # Handle DataFrame
            if isinstance(data, pd.DataFrame):
                headers = headers or list(data.columns)
                data = data.values.tolist()

            # Write headers
            if headers:
                for col_idx, header in enumerate(headers, start=start_col):
                    sheet.cell(row=start_row, column=col_idx, value=header)
                start_row += 1

            # Write data
            for row_idx, row_data in enumerate(data, start=start_row):
                for col_idx, value in enumerate(row_data, start=start_col):
                    sheet.cell(row=row_idx, column=col_idx, value=value)

            # Create directories if needed
            os.makedirs(
                os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True
            )

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Wrote {len(data)} rows to sheet: {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing sheet: {str(e).splitlines()[0]}")
            raise

    def read_cell(self, file_path: str, sheet_name: str, cell: str) -> Any:
        """
        Read a specific cell value.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            cell: Cell reference (e.g., 'A1')

        Returns:
            Cell value
        """
        try:
            wb = load_workbook(file_path, data_only=True)
            sheet = wb[sheet_name]
            value = sheet[cell].value
            wb.close()
            self.logger.info(f"Read cell {cell} from {sheet_name}: {value}")
            return value
        except Exception as e:
            self.logger.error(f"Error reading cell: {str(e).splitlines()[0]}")
            raise

    def write_cell(self, file_path: str, sheet_name: str, cell: str, value: Any) -> bool:
        """
        Write a value to a specific cell.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            cell: Cell reference (e.g., 'A1')
            value: Value to write

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet[cell] = value
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Wrote value to cell {cell} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing cell: {str(e).splitlines()[0]}")
            raise

    def read_range(
        self, file_path: str, sheet_name: str, start_cell: str, end_cell: str
    ) -> List[List]:
        """
        Read a range of cells.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            start_cell: Starting cell (e.g., 'A1')
            end_cell: Ending cell (e.g., 'C10')

        Returns:
            List of rows in the range
        """
        try:
            wb = load_workbook(file_path, data_only=True)
            sheet = wb[sheet_name]
            cell_range = sheet[f"{start_cell}:{end_cell}"]

            data = []
            for row in cell_range:
                data.append([cell.value for cell in row])

            wb.close()
            self.logger.info(f"Read range {start_cell}:{end_cell} from {sheet_name}")
            return data
        except Exception as e:
            self.logger.error(f"Error reading range: {str(e).splitlines()[0]}")
            raise

    def append_row(self, file_path: str, sheet_name: str, row_data: List[Any]) -> bool:
        """
        Append a row to the end of a sheet.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            row_data: List of values to append

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.append(row_data)
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Appended row to {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error appending row: {str(e).splitlines()[0]}")
            raise

    def insert_row(
        self, file_path: str, sheet_name: str, row_index: int, row_data: Optional[List[Any]] = None
    ) -> bool:
        """
        Insert a row at a specific position.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            row_index: Row index to insert at (1-indexed)
            row_data: Optional data for the new row

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.insert_rows(row_index)

            if row_data:
                for col_idx, value in enumerate(row_data, start=1):
                    sheet.cell(row=row_index, column=col_idx, value=value)

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Inserted row at index {row_index} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error inserting row: {str(e).splitlines()[0]}")
            raise

    def delete_row(self, file_path: str, sheet_name: str, row_index: int) -> bool:
        """
        Delete a row.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            row_index: Row index to delete (1-indexed)

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.delete_rows(row_index)
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Deleted row {row_index} from {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting row: {str(e).splitlines()[0]}")
            raise

    def insert_column(
        self, file_path: str, sheet_name: str, col_index: int, col_data: Optional[List[Any]] = None
    ) -> bool:
        """
        Insert a column at a specific position.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            col_index: Column index to insert at (1-indexed)
            col_data: Optional data for the new column

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.insert_cols(col_index)

            if col_data:
                for row_idx, value in enumerate(col_data, start=1):
                    sheet.cell(row=row_idx, column=col_index, value=value)

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Inserted column at index {col_index} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error inserting column: {str(e).splitlines()[0]}")
            raise

    def delete_column(self, file_path: str, sheet_name: str, col_index: int) -> bool:
        """
        Delete a column.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            col_index: Column index to delete (1-indexed)

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.delete_cols(col_index)
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Deleted column {col_index} from {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting column: {str(e).splitlines()[0]}")
            raise

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get all sheet names in a workbook.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of sheet names
        """
        try:
            wb = load_workbook(file_path)
            sheet_names = wb.sheetnames
            wb.close()
            self.logger.info(f"Found {len(sheet_names)} sheets")
            return sheet_names
        except Exception as e:
            self.logger.error(f"Error getting sheet names: {str(e).splitlines()[0]}")
            raise

    def create_sheet(self, file_path: str, sheet_name: str, index: Optional[int] = None) -> bool:
        """
        Create a new sheet in an existing workbook.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name for the new sheet
            index: Optional position for the new sheet

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            wb.create_sheet(title=sheet_name, index=index)
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Created sheet: {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating sheet: {str(e).splitlines()[0]}")
            raise

    def delete_sheet(self, file_path: str, sheet_name: str) -> bool:
        """
        Delete a sheet from a workbook.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to delete

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            if sheet_name in wb.sheetnames:
                wb.remove(wb[sheet_name])
                wb.save(file_path)
                wb.close()
                self.logger.info(f"Deleted sheet: {sheet_name}")
                return True
            else:
                self.logger.warning(f"Sheet not found: {sheet_name}")
                wb.close()
                return False
        except Exception as e:
            self.logger.error(f"Error deleting sheet: {str(e).splitlines()[0]}")
            raise

    def rename_sheet(self, file_path: str, old_name: str, new_name: str) -> bool:
        """
        Rename a sheet.

        Args:
            file_path: Path to the Excel file
            old_name: Current sheet name
            new_name: New sheet name

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            if old_name in wb.sheetnames:
                sheet = wb[old_name]
                sheet.title = new_name
                wb.save(file_path)
                wb.close()
                self.logger.info(f"Renamed sheet from {old_name} to {new_name}")
                return True
            else:
                self.logger.warning(f"Sheet not found: {old_name}")
                wb.close()
                return False
        except Exception as e:
            self.logger.error(f"Error renaming sheet: {str(e).splitlines()[0]}")
            raise

    def copy_sheet(self, file_path: str, source_sheet: str, target_sheet: str) -> bool:
        """
        Copy a sheet within a workbook.

        Args:
            file_path: Path to the Excel file
            source_sheet: Name of the sheet to copy
            target_sheet: Name for the new sheet

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            source = wb[source_sheet]
            target = wb.copy_worksheet(source)
            target.title = target_sheet
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Copied sheet {source_sheet} to {target_sheet}")
            return True
        except Exception as e:
            self.logger.error(f"Error copying sheet: {str(e).splitlines()[0]}")
            raise

    def format_cell(
        self,
        file_path: str,
        sheet_name: str,
        cell: str,
        font_name: Optional[str] = None,
        font_size: Optional[int] = None,
        bold: bool = False,
        italic: bool = False,
        font_color: Optional[str] = None,
        bg_color: Optional[str] = None,
        alignment: Optional[str] = None,
    ) -> bool:
        """
        Format a cell with various styling options.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            cell: Cell reference (e.g., 'A1')
            font_name: Font name
            font_size: Font size
            bold: Bold text
            italic: Italic text
            font_color: Font color (hex code without #, e.g., 'FF0000' for red)
            bg_color: Background color (hex code without #)
            alignment: Text alignment ('left', 'center', 'right')

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            target_cell = sheet[cell]

            # Font styling
            if any([font_name, font_size, bold, italic, font_color]):
                target_cell.font = Font(
                    name=font_name or target_cell.font.name,
                    size=font_size or target_cell.font.size,
                    bold=bold,
                    italic=italic,
                    color=font_color,
                )

            # Background color
            if bg_color:
                target_cell.fill = PatternFill(
                    start_color=bg_color, end_color=bg_color, fill_type="solid"
                )

            # Alignment
            if alignment:
                align_map = {"left": "left", "center": "center", "right": "right"}
                target_cell.alignment = Alignment(horizontal=align_map.get(alignment, "left"))

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Formatted cell {cell} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error formatting cell: {str(e).splitlines()[0]}")
            raise

    def format_range(
        self, file_path: str, sheet_name: str, start_cell: str, end_cell: str, **format_options
    ) -> bool:
        """
        Format a range of cells.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            start_cell: Starting cell (e.g., 'A1')
            end_cell: Ending cell (e.g., 'C10')
            **format_options: Formatting options (same as format_cell)

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            cell_range = sheet[f"{start_cell}:{end_cell}"]

            # Create font if needed
            font = None
            if any(
                k in format_options
                for k in ["font_name", "font_size", "bold", "italic", "font_color"]
            ):
                font = Font(
                    name=format_options.get("font_name"),
                    size=format_options.get("font_size"),
                    bold=format_options.get("bold", False),
                    italic=format_options.get("italic", False),
                    color=format_options.get("font_color"),
                )

            # Create fill if needed
            fill = None
            if "bg_color" in format_options:
                fill = PatternFill(
                    start_color=format_options["bg_color"],
                    end_color=format_options["bg_color"],
                    fill_type="solid",
                )

            # Create alignment if needed
            alignment = None
            if "alignment" in format_options:
                align_map = {"left": "left", "center": "center", "right": "right"}
                alignment = Alignment(horizontal=align_map.get(format_options["alignment"], "left"))

            # Apply formatting
            for row in cell_range:
                for cell in row:
                    if font:
                        cell.font = font
                    if fill:
                        cell.fill = fill
                    if alignment:
                        cell.alignment = alignment

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Formatted range {start_cell}:{end_cell} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error formatting range: {str(e).splitlines()[0]}")
            raise

    def merge_cells(self, file_path: str, sheet_name: str, start_cell: str, end_cell: str) -> bool:
        """
        Merge a range of cells.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            start_cell: Starting cell (e.g., 'A1')
            end_cell: Ending cell (e.g., 'C1')

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.merge_cells(f"{start_cell}:{end_cell}")
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Merged cells {start_cell}:{end_cell} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging cells: {str(e).splitlines()[0]}")
            raise

    def unmerge_cells(
        self, file_path: str, sheet_name: str, start_cell: str, end_cell: str
    ) -> bool:
        """
        Unmerge a range of cells.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            start_cell: Starting cell (e.g., 'A1')
            end_cell: Ending cell (e.g., 'C1')

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.unmerge_cells(f"{start_cell}:{end_cell}")
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Unmerged cells {start_cell}:{end_cell} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error unmerging cells: {str(e).splitlines()[0]}")
            raise

    def set_column_width(
        self, file_path: str, sheet_name: str, column: Union[str, int], width: float
    ) -> bool:
        """
        Set column width.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            column: Column letter or index
            width: Column width

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]

            if isinstance(column, int):
                column = get_column_letter(column)

            sheet.column_dimensions[column].width = width
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Set column {column} width to {width} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting column width: {str(e).splitlines()[0]}")
            raise

    def set_row_height(self, file_path: str, sheet_name: str, row: int, height: float) -> bool:
        """
        Set row height.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            row: Row number
            height: Row height

        Returns:
            True if successful
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            sheet.row_dimensions[row].height = height
            wb.save(file_path)
            wb.close()
            self.logger.info(f"Set row {row} height to {height} in {sheet_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting row height: {str(e).splitlines()[0]}")
            raise

    def find_value(self, file_path: str, sheet_name: str, search_value: Any) -> List[str]:
        """
        Find all cells containing a specific value.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            search_value: Value to search for

        Returns:
            List of cell references
        """
        try:
            wb = load_workbook(file_path, data_only=True)
            sheet = wb[sheet_name]

            matches = []
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value == search_value:
                        matches.append(cell.coordinate)

            wb.close()
            self.logger.info(f"Found {len(matches)} cells with value: {search_value}")
            return matches
        except Exception as e:
            self.logger.error(f"Error finding value: {str(e).splitlines()[0]}")
            raise

    def replace_value(self, file_path: str, sheet_name: str, old_value: Any, new_value: Any) -> int:
        """
        Replace all occurrences of a value.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            old_value: Value to replace
            new_value: New value

        Returns:
            Number of replacements made
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]

            count = 0
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value == old_value:
                        cell.value = new_value
                        count += 1

            wb.save(file_path)
            wb.close()
            self.logger.info(f"Replaced {count} occurrences in {sheet_name}")
            return count
        except Exception as e:
            self.logger.error(f"Error replacing value: {str(e).splitlines()[0]}")
            raise

    def get_row_count(self, file_path: str, sheet_name: str) -> int:
        """
        Get the number of rows with data.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name

        Returns:
            Number of rows
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            row_count = sheet.max_row
            wb.close()
            self.logger.info(f"Sheet {sheet_name} has {row_count} rows")
            return row_count
        except Exception as e:
            self.logger.error(f"Error getting row count: {str(e).splitlines()[0]}")
            raise

    def get_column_count(self, file_path: str, sheet_name: str) -> int:
        """
        Get the number of columns with data.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name

        Returns:
            Number of columns
        """
        try:
            wb = load_workbook(file_path)
            sheet = wb[sheet_name]
            col_count = sheet.max_column
            wb.close()
            self.logger.info(f"Sheet {sheet_name} has {col_count} columns")
            return col_count
        except Exception as e:
            self.logger.error(f"Error getting column count: {str(e).splitlines()[0]}")
            raise

    def filter_data(
        self,
        file_path: str,
        sheet_name: str,
        column: str,
        condition,
        output_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Filter data based on a condition.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            column: Column name to filter on
            condition: Function that returns True for rows to keep
            output_path: Optional output file path

        Returns:
            Filtered DataFrame
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            filtered_df = df[df[column].apply(condition)]

            if output_path:
                filtered_df.to_excel(output_path, sheet_name=sheet_name, index=False)
                self.logger.info(f"Filtered data saved to: {output_path}")

            self.logger.info(f"Filtered {len(df)} rows to {len(filtered_df)} rows")
            return filtered_df
        except Exception as e:
            self.logger.error(f"Error filtering data: {str(e).splitlines()[0]}")
            raise

    def sort_data(
        self,
        file_path: str,
        sheet_name: str,
        column: str,
        ascending: bool = True,
        output_path: Optional[str] = None,
    ) -> bool:
        """
        Sort data by a column.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name
            column: Column name to sort by
            ascending: Sort order
            output_path: Optional output file path

        Returns:
            True if successful
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sorted_df = df.sort_values(by=column, ascending=ascending)

            save_path = output_path or file_path
            sorted_df.to_excel(save_path, sheet_name=sheet_name, index=False)
            self.logger.info(f"Sorted data by {column} ({'asc' if ascending else 'desc'})")
            return True
        except Exception as e:
            self.logger.error(f"Error sorting data: {str(e).splitlines()[0]}")
            raise

    def backup_file(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """
        Create a backup of an Excel file.

        Args:
            file_path: Path to the Excel file
            backup_suffix: Suffix for backup file

        Returns:
            Path to backup file
        """
        try:
            path_obj = Path(file_path)
            backup_path = str(path_obj.with_suffix(f"{path_obj.suffix}{backup_suffix}"))

            wb = load_workbook(file_path)
            wb.save(backup_path)
            wb.close()

            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e).splitlines()[0]}")
            raise

    def load_test_data_from_example(
        self, test_data_manager, pytest_bdd_example: dict, sheet_file_path: Optional[str] = None
    ) -> dict:
        """
        Load test data from Excel based on pytest-bdd example parameters.

        Args:
            test_data_manager: TestDataManager fixture for loading Excel data
            pytest_bdd_example: pytest-bdd example dict with SheetName and RowNumber
            sheet_file_path: Optional path to Excel file (if not using test_data_manager's default)

        Returns:
            Loaded test data dictionary

        Raises:
            ValueError: If SheetName or RowNumber not provided
        """
        sheet_name = pytest_bdd_example.get("SheetName", "")
        row_number = int(pytest_bdd_example.get("RowNumber", 0))

        if not sheet_name or row_number <= 0:
            raise ValueError(
                "SheetName/RowNumber not provided in Examples table for this scenario."
            )

        # Load test data using TestDataManager
        selected_row = test_data_manager.get_row_by_number(sheet_name, row_number)
        self.logger.info(f"Loaded test data from {sheet_name} sheet, row {row_number}")

        return selected_row

    # --- Test Execution Report Methods ---

    def clear_test_results(self) -> None:
        self.test_results.clear()
        self.session_start_time = datetime.now()

    def collect_result_from_item(self, item, report) -> None:
        """Extract per-test data from a pytest item/report and store it."""
        ctx = item.funcargs.get("test_context", {})
        td = ctx.get("test_data", {})

        # Always fetch Test Case Id directly from Excel using BDD example params
        test_case_id = "NA"
        try:
            example = item.funcargs.get("_pytest_bdd_example", {})
            sheet = example.get("SheetName", "")
            row_num = int(example.get("RowNumber", 0))
            if sheet and row_num > 0:
                from config.settings import settings
                from openpyxl import load_workbook as _lwb
                wb = _lwb(str(settings.test_data_excel), read_only=True, data_only=True)
                ws = wb[sheet]
                rows = list(ws.iter_rows(values_only=True))
                headers = [str(h).strip() for h in rows[0]]
                row_data = dict(zip(headers, rows[row_num - 1]))
                wb.close()
                test_case_id = str(row_data.get("Test Case Id", "NA") or "NA").strip()
        except Exception:
            pass

        def _v(src, key):
            return str(src.get(key, "NA") or "NA").strip()

        name = item.nodeid.rsplit("::", 1)[-1].split("[")[0]
        if name.startswith("test_"):
            name = name[5:]
        title = "_".join(p.capitalize() if p.islower() else p for p in name.split("_"))

        try:
            feature = (item.funcargs.get("_pytest_bdd_example", {}).get("SheetName", "") or "").strip() or "NA"
        except Exception:
            feature = "NA"

        cause = "NA"
        if report.failed and report.longrepr:
            cause = str(report.longrepr).strip()

        start_time = getattr(item, "start_time", None)
        end_time = datetime.now()
        if start_time:
            duration = end_time - start_time
            total_secs = int(duration.total_seconds())
            total_time = f"{total_secs // 60}m {total_secs % 60}s"
        else:
            total_time = "NA"

        # Fetch hrc_number from class variable (always set during view documents step)
        hrc_val = _v(ctx, "hrc_number")
        if hrc_val == "NA":
            try:
                from tests.steps.naw.view_documents_step import ViewDocumentsStep
                hrc_val = (ViewDocumentsStep.hrc_number or "NA").strip() or "NA"
                # Reset class variable so the next test doesn't inherit a stale value
                ViewDocumentsStep.hrc_number = ""
            except Exception:
                pass

        # Fetch nNumber from DocuSignPage class variable
        n_val = "NA"
        try:
            from applicationqe.pages.ewm.docusign_page import DocuSignPage
            n_val = (DocuSignPage.nNumber or "NA").strip() or "NA"
            # Reset class variable so the next test doesn't inherit a stale value
            DocuSignPage.nNumber = ""
        except Exception:
            pass

        self.test_results.append({
            "Test Case Id": test_case_id, "Title": title,
            "Last Run": datetime.now().strftime("%m/%d/%Y"),
            "Run By": os.getenv("USERNAME", os.getenv("USER", platform.node())),
            "B#": _v(ctx, "b_number"), "hrcNumber": hrc_val,
            "nNumber": n_val,
            "parentBNumber": _v(ctx, "parent_b_number"),
            "activationNumber": _v(ctx, "activation_number"),
            "Status": "Passed" if report.passed else "Failed",
            "Feature": feature,
            "Environment": os.getenv("TEST_ENV", "NA"),
            "Start Time": start_time.strftime("%I:%M:%S %p") if start_time else "NA",
            "End Time": end_time.strftime("%I:%M:%S %p"),
            "Total Time": total_time,
            "Cause Of Failure": cause,
        })

    def generate_excel_report(self, output_dir: Union[str, Path, None] = None) -> Optional[Path]:
        """Generate Excel report from collected test results."""
        if not self.test_results:
            return None

        out = Path(output_dir or Path("reports") / "ExcelReport")
        out.mkdir(parents=True, exist_ok=True)
        filepath = out / f"ExcelReport_{datetime.now().strftime('%d-%b-%y %H-%M-%S.%f')}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = f"ExcelReport_{datetime.now().strftime('%d-%b-%y %H-%M-%S')}"

        for ci, col in enumerate(self._REPORT_COLUMNS, 1):
            c = ws.cell(row=1, column=ci, value=col)
            c.font, c.fill, c.alignment, c.border = (
                self._HDR_STYLE["font"], self._HDR_STYLE["fill"], self._HDR_STYLE["alignment"], self._BORDER
            )

        for ri, row in enumerate(self.test_results, 2):
            for ci, col in enumerate(self._REPORT_COLUMNS, 1):
                val = row.get(col, "NA")
                c = ws.cell(row=ri, column=ci, value=val)
                c.alignment = Alignment(vertical="top", wrap_text=True)
                c.border = self._BORDER
                if col == "Status":
                    style = self._PASS_STYLE if val == "Passed" else self._FAIL_STYLE if val == "Failed" else {}
                    for k, v in style.items():
                        setattr(c, k, v)

        for col_cells in ws.columns:
            letter = col_cells[0].column_letter
            header_len = len(str(col_cells[0].value or ""))
            data_len = max((max(len(l) for l in str(c.value or "").split("\n")) for c in col_cells), default=8)
            width = max(header_len + 4, data_len + 4, 15)
            ws.column_dimensions[letter].width = min(width, 60)

        # Overall Execution Time summary row (under End Time / Total Time columns)
        summary_row = len(self.test_results) + 3
        session_start = getattr(self, "session_start_time", None)
        if session_start:
            overall = datetime.now() - session_start
            total_secs = int(overall.total_seconds())
            hrs, rem = divmod(total_secs, 3600)
            mins, secs = divmod(rem, 60)
            overall_text = f"{hrs}h {mins}m {secs}s" if hrs else f"{mins}m {secs}s"
        else:
            overall_text = "NA"
        end_time_col = self._REPORT_COLUMNS.index("End Time") + 1
        total_time_col = self._REPORT_COLUMNS.index("Total Time") + 1
        label_cell = ws.cell(row=summary_row, column=end_time_col, value="Overall Execution Time")
        label_cell.font = Font(bold=True, size=11)
        label_cell.border = self._BORDER
        value_cell = ws.cell(row=summary_row, column=total_time_col, value=overall_text)
        value_cell.font = Font(bold=True, size=11)
        value_cell.border = self._BORDER

        ws.freeze_panes = "A2"
        wb.save(filepath)
        self.logger.info(f"Excel Report: {filepath.absolute()}")
        return filepath


# Convenience functions
def read_excel(
    file_path: str, sheet_name: Optional[str] = None, **kwargs
) -> Union[List[List], pd.DataFrame]:
    """Read data from an Excel sheet."""
    return ExcelUtils().read_sheet(file_path, sheet_name, **kwargs)


def write_excel(
    file_path: str, data: Union[List[List], pd.DataFrame], sheet_name: str = "Sheet1", **kwargs
) -> bool:
    """Write data to an Excel sheet."""
    return ExcelUtils().write_sheet(file_path, data, sheet_name, **kwargs)


def get_cell_value(file_path: str, sheet_name: str, cell: str) -> Any:
    """Get value from a specific cell."""
    return ExcelUtils().read_cell(file_path, sheet_name, cell)


def set_cell_value(file_path: str, sheet_name: str, cell: str, value: Any) -> bool:
    """Set value to a specific cell."""
    return ExcelUtils().write_cell(file_path, sheet_name, cell, value)


# Shared instance for test execution report (used by conftest.py)
excel_report = ExcelUtils()
