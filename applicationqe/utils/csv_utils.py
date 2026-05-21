"""
CSV utility module for comprehensive CSV file operations.
"""

import csv
import os
from typing import Any, Callable, Dict, List, Optional

from utils.logger import setup_logger


class CSVUtils:
    """Comprehensive utility class for CSV file operations."""

    def __init__(self):
        self.logger = setup_logger(__name__)

    def read_csv(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
        skip_rows: int = 0,
    ) -> List[List[str]]:
        """
        Read a CSV file and return all rows.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            has_header: Whether file has a header row
            skip_rows: Number of rows to skip from the beginning

        Returns:
            List of rows (each row is a list of values)
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)

                # Skip rows
                for _ in range(skip_rows):
                    next(reader, None)

                data = list(reader)
                self.logger.info(f"Read {len(data)} rows from: {file_path}")
                return data
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {str(e)}")
            raise

    def read_csv_as_dict(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        fieldnames: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """
        Read a CSV file and return rows as dictionaries.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            fieldnames: Optional custom field names (uses first row if not provided)

        Returns:
            List of dictionaries (each dict is a row)
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                if fieldnames:
                    reader = csv.DictReader(file, fieldnames=fieldnames, delimiter=delimiter)
                else:
                    reader = csv.DictReader(file, delimiter=delimiter)

                data = list(reader)
                self.logger.info(f"Read {len(data)} rows as dictionaries from: {file_path}")
                return data
        except Exception as e:
            self.logger.error(f"Error reading CSV as dict: {str(e)}")
            raise

    def write_csv(
        self,
        file_path: str,
        data: List[List[Any]],
        delimiter: str = ",",
        encoding: str = "utf-8",
        headers: Optional[List[str]] = None,
        mode: str = "w",
        create_dirs: bool = True,
    ) -> bool:
        """
        Write data to a CSV file.

        Args:
            file_path: Path to the CSV file
            data: Data to write (list of rows)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            headers: Optional column headers
            mode: Write mode ('w' for write, 'a' for append)
            create_dirs: Create parent directories if needed

        Returns:
            True if successful
        """
        try:
            if create_dirs:
                os.makedirs(
                    os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True
                )

            with open(file_path, mode, encoding=encoding, newline="") as file:
                writer = csv.writer(file, delimiter=delimiter)

                if headers and mode == "w":
                    writer.writerow(headers)

                writer.writerows(data)

            self.logger.info(f"Wrote {len(data)} rows to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing CSV file: {str(e)}")
            raise

    def write_csv_from_dict(
        self,
        file_path: str,
        data: List[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        mode: str = "w",
        create_dirs: bool = True,
    ) -> bool:
        """
        Write dictionary data to a CSV file.

        Args:
            file_path: Path to the CSV file
            data: List of dictionaries to write
            fieldnames: Column names (uses keys from first dict if not provided)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            mode: Write mode ('w' for write, 'a' for append)
            create_dirs: Create parent directories if needed

        Returns:
            True if successful
        """
        try:
            if not data:
                raise ValueError("Data list is empty")

            if create_dirs:
                os.makedirs(
                    os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True
                )

            if not fieldnames:
                fieldnames = list(data[0].keys())

            with open(file_path, mode, encoding=encoding, newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=delimiter)

                if mode == "w":
                    writer.writeheader()

                writer.writerows(data)

            self.logger.info(f"Wrote {len(data)} rows from dictionaries to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing CSV from dict: {str(e)}")
            raise

    def append_row(
        self, file_path: str, row_data: List[Any], delimiter: str = ",", encoding: str = "utf-8"
    ) -> bool:
        """
        Append a single row to a CSV file.

        Args:
            file_path: Path to the CSV file
            row_data: Row data to append
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            with open(file_path, "a", encoding=encoding, newline="") as file:
                writer = csv.writer(file, delimiter=delimiter)
                writer.writerow(row_data)

            self.logger.info(f"Appended row to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error appending row: {str(e)}")
            raise

    def append_rows(
        self,
        file_path: str,
        rows_data: List[List[Any]],
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Append multiple rows to a CSV file.

        Args:
            file_path: Path to the CSV file
            rows_data: List of rows to append
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            with open(file_path, "a", encoding=encoding, newline="") as file:
                writer = csv.writer(file, delimiter=delimiter)
                writer.writerows(rows_data)

            self.logger.info(f"Appended {len(rows_data)} rows to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error appending rows: {str(e)}")
            raise

    def read_column(
        self,
        file_path: str,
        column_index: int,
        delimiter: str = ",",
        encoding: str = "utf-8",
        skip_header: bool = True,
    ) -> List[str]:
        """
        Read a specific column from a CSV file.

        Args:
            file_path: Path to the CSV file
            column_index: Column index (0-based)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            skip_header: Skip the first row

        Returns:
            List of column values
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)

                if skip_header:
                    next(reader, None)

                column_data = [row[column_index] for row in reader if len(row) > column_index]

            self.logger.info(f"Read column {column_index} ({len(column_data)} values)")
            return column_data
        except Exception as e:
            self.logger.error(f"Error reading column: {str(e)}")
            raise

    def read_column_by_name(
        self, file_path: str, column_name: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> List[str]:
        """
        Read a specific column by name from a CSV file.

        Args:
            file_path: Path to the CSV file
            column_name: Name of the column
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            List of column values
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                column_data = [row[column_name] for row in reader]

            self.logger.info(f"Read column '{column_name}' ({len(column_data)} values)")
            return column_data
        except Exception as e:
            self.logger.error(f"Error reading column by name: {str(e)}")
            raise

    def update_row(
        self,
        file_path: str,
        row_index: int,
        new_data: List[Any],
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Update a specific row in a CSV file.

        Args:
            file_path: Path to the CSV file
            row_index: Row index to update (0-based)
            new_data: New data for the row
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read all data
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if row_index < 0 or row_index >= len(data):
                raise ValueError(f"Row index {row_index} out of range")

            # Update row
            data[row_index] = new_data

            # Write back
            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Updated row {row_index} in: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating row: {str(e)}")
            raise

    def update_cell(
        self,
        file_path: str,
        row_index: int,
        column_index: int,
        new_value: Any,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Update a specific cell in a CSV file.

        Args:
            file_path: Path to the CSV file
            row_index: Row index (0-based)
            column_index: Column index (0-based)
            new_value: New value for the cell
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read all data
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if row_index < 0 or row_index >= len(data):
                raise ValueError(f"Row index {row_index} out of range")

            if column_index < 0 or column_index >= len(data[row_index]):
                raise ValueError(f"Column index {column_index} out of range")

            # Update cell
            data[row_index][column_index] = str(new_value)

            # Write back
            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Updated cell [{row_index}, {column_index}] in: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating cell: {str(e)}")
            raise

    def delete_row(
        self, file_path: str, row_index: int, delimiter: str = ",", encoding: str = "utf-8"
    ) -> bool:
        """
        Delete a specific row from a CSV file.

        Args:
            file_path: Path to the CSV file
            row_index: Row index to delete (0-based)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read all data
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if row_index < 0 or row_index >= len(data):
                raise ValueError(f"Row index {row_index} out of range")

            # Delete row
            del data[row_index]

            # Write back
            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Deleted row {row_index} from: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting row: {str(e)}")
            raise

    def delete_column(
        self, file_path: str, column_index: int, delimiter: str = ",", encoding: str = "utf-8"
    ) -> bool:
        """
        Delete a specific column from a CSV file.

        Args:
            file_path: Path to the CSV file
            column_index: Column index to delete (0-based)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read all data
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            # Delete column from each row
            new_data = []
            for row in data:
                if column_index < len(row):
                    new_row = row[:column_index] + row[column_index + 1 :]
                    new_data.append(new_row)
                else:
                    new_data.append(row)

            # Write back
            self.write_csv(file_path, new_data, delimiter, encoding, mode="w")
            self.logger.info(f"Deleted column {column_index} from: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting column: {str(e)}")
            raise

    def insert_row(
        self,
        file_path: str,
        row_index: int,
        row_data: List[Any],
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Insert a row at a specific position.

        Args:
            file_path: Path to the CSV file
            row_index: Position to insert at (0-based)
            row_data: Data for the new row
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read all data
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            # Insert row
            data.insert(row_index, row_data)

            # Write back
            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Inserted row at index {row_index} in: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error inserting row: {str(e)}")
            raise

    def find_rows(
        self,
        file_path: str,
        search_value: Any,
        column_index: Optional[int] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> List[Tuple[int, List[str]]]:
        """
        Find rows containing a specific value.

        Args:
            file_path: Path to the CSV file
            search_value: Value to search for
            column_index: Optional specific column to search in
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            List of tuples (row_index, row_data)
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)
            matches = []

            for idx, row in enumerate(data):
                if column_index is not None:
                    if column_index < len(row) and row[column_index] == str(search_value):
                        matches.append((idx, row))
                else:
                    if str(search_value) in row:
                        matches.append((idx, row))

            self.logger.info(f"Found {len(matches)} matching rows")
            return matches
        except Exception as e:
            self.logger.error(f"Error finding rows: {str(e)}")
            raise

    def replace_value(
        self,
        file_path: str,
        old_value: Any,
        new_value: Any,
        column_index: Optional[int] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> int:
        """
        Replace all occurrences of a value.

        Args:
            file_path: Path to the CSV file
            old_value: Value to replace
            new_value: New value
            column_index: Optional specific column to search in
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            Number of replacements made
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)
            count = 0

            for row in data:
                if column_index is not None:
                    if column_index < len(row) and row[column_index] == str(old_value):
                        row[column_index] = str(new_value)
                        count += 1
                else:
                    for i in range(len(row)):
                        if row[i] == str(old_value):
                            row[i] = str(new_value)
                            count += 1

            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Replaced {count} occurrences")
            return count
        except Exception as e:
            self.logger.error(f"Error replacing value: {str(e)}")
            raise

    def filter_csv(
        self,
        file_path: str,
        filter_func: Callable,
        output_path: Optional[str] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        keep_header: bool = True,
    ) -> List[List[str]]:
        """
        Filter CSV rows using a custom function.

        Args:
            file_path: Path to the CSV file
            filter_func: Function that returns True for rows to keep
            output_path: Optional output file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            keep_header: Keep the header row in output

        Returns:
            Filtered data
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if keep_header and data:
                header = [data[0]]
                filtered_data = header + [row for row in data[1:] if filter_func(row)]
            else:
                filtered_data = [row for row in data if filter_func(row)]

            if output_path:
                self.write_csv(output_path, filtered_data, delimiter, encoding, mode="w")
                self.logger.info(f"Filtered data saved to: {output_path}")

            self.logger.info(f"Filtered {len(data)} rows to {len(filtered_data)} rows")
            return filtered_data
        except Exception as e:
            self.logger.error(f"Error filtering CSV: {str(e)}")
            raise

    def sort_csv(
        self,
        file_path: str,
        column_index: int,
        reverse: bool = False,
        output_path: Optional[str] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
    ) -> bool:
        """
        Sort CSV file by a specific column.

        Args:
            file_path: Path to the CSV file
            column_index: Column index to sort by (0-based)
            reverse: Sort in descending order
            output_path: Optional output file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            has_header: Whether file has a header row

        Returns:
            True if successful
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if has_header and data:
                header = data[0]
                body = data[1:]
                sorted_body = sorted(
                    body,
                    key=lambda row: row[column_index] if column_index < len(row) else "",
                    reverse=reverse,
                )
                sorted_data = [header] + sorted_body
            else:
                sorted_data = sorted(
                    data,
                    key=lambda row: row[column_index] if column_index < len(row) else "",
                    reverse=reverse,
                )

            save_path = output_path or file_path
            self.write_csv(save_path, sorted_data, delimiter, encoding, mode="w")
            self.logger.info(f"Sorted CSV by column {column_index}")
            return True
        except Exception as e:
            self.logger.error(f"Error sorting CSV: {str(e)}")
            raise

    def merge_csv_files(
        self,
        file_paths: List[str],
        output_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        include_headers: bool = False,
    ) -> bool:
        """
        Merge multiple CSV files into one.

        Args:
            file_paths: List of CSV file paths to merge
            output_path: Output file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            include_headers: Include header from each file

        Returns:
            True if successful
        """
        try:
            all_data = []

            for idx, file_path in enumerate(file_paths):
                data = self.read_csv(file_path, delimiter, encoding, has_header=False)

                if idx == 0 or include_headers:
                    all_data.extend(data)
                else:
                    # Skip header for subsequent files
                    all_data.extend(data[1:] if data else [])

            self.write_csv(output_path, all_data, delimiter, encoding, mode="w")
            self.logger.info(f"Merged {len(file_paths)} files into: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging CSV files: {str(e)}")
            raise

    def get_row_count(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        exclude_header: bool = False,
    ) -> int:
        """
        Get the number of rows in a CSV file.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            exclude_header: Exclude header from count

        Returns:
            Number of rows
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)
                row_count = sum(1 for _ in reader)

                if exclude_header and row_count > 0:
                    row_count -= 1

            self.logger.info(f"File has {row_count} rows")
            return row_count
        except Exception as e:
            self.logger.error(f"Error getting row count: {str(e)}")
            raise

    def get_column_count(
        self, file_path: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> int:
        """
        Get the number of columns in a CSV file.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            Number of columns
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)
                first_row = next(reader, None)
                col_count = len(first_row) if first_row else 0

            self.logger.info(f"File has {col_count} columns")
            return col_count
        except Exception as e:
            self.logger.error(f"Error getting column count: {str(e)}")
            raise

    def get_headers(
        self, file_path: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> List[str]:
        """
        Get the header row from a CSV file.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            List of header values
        """
        try:
            with open(file_path, "r", encoding=encoding, newline="") as file:
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])

            self.logger.info(f"Read headers: {headers}")
            return headers
        except Exception as e:
            self.logger.error(f"Error getting headers: {str(e)}")
            raise

    def add_column(
        self,
        file_path: str,
        column_name: str,
        default_value: Any = "",
        position: Optional[int] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Add a new column to a CSV file.

        Args:
            file_path: Path to the CSV file
            column_name: Name for the new column
            default_value: Default value for existing rows
            position: Optional position to insert column (appends if None)
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if not data:
                raise ValueError("CSV file is empty")

            # Add column header
            if position is None:
                data[0].append(column_name)
            else:
                data[0].insert(position, column_name)

            # Add default values to existing rows
            for i in range(1, len(data)):
                if position is None:
                    data[i].append(str(default_value))
                else:
                    data[i].insert(position, str(default_value))

            self.write_csv(file_path, data, delimiter, encoding, mode="w")
            self.logger.info(f"Added column '{column_name}' to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding column: {str(e)}")
            raise

    def remove_duplicates(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        keep_header: bool = True,
    ) -> int:
        """
        Remove duplicate rows from a CSV file.

        Args:
            file_path: Path to the CSV file
            output_path: Optional output file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)
            keep_header: Keep the header row

        Returns:
            Number of duplicates removed
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)
            original_count = len(data)

            if keep_header and data:
                header = [data[0]]
                body = data[1:]
                unique_body = []
                seen = set()

                for row in body:
                    row_tuple = tuple(row)
                    if row_tuple not in seen:
                        seen.add(row_tuple)
                        unique_body.append(row)

                unique_data = header + unique_body
            else:
                seen = set()
                unique_data = []
                for row in data:
                    row_tuple = tuple(row)
                    if row_tuple not in seen:
                        seen.add(row_tuple)
                        unique_data.append(row)

            save_path = output_path or file_path
            self.write_csv(save_path, unique_data, delimiter, encoding, mode="w")

            duplicates_removed = original_count - len(unique_data)
            self.logger.info(f"Removed {duplicates_removed} duplicate rows")
            return duplicates_removed
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}")
            raise

    def convert_to_json(
        self, file_path: str, json_path: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> bool:
        """
        Convert a CSV file to JSON.

        Args:
            file_path: Path to the CSV file
            json_path: Output JSON file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            import json

            data = self.read_csv_as_dict(file_path, delimiter, encoding)

            with open(json_path, "w", encoding=encoding) as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            self.logger.info(f"Converted CSV to JSON: {json_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error converting to JSON: {str(e)}")
            raise

    def convert_from_json(
        self, json_path: str, csv_path: str, delimiter: str = ",", encoding: str = "utf-8"
    ) -> bool:
        """
        Convert a JSON file to CSV.

        Args:
            json_path: Path to the JSON file
            csv_path: Output CSV file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            import json

            with open(json_path, "r", encoding=encoding) as file:
                data = json.load(file)

            if not isinstance(data, list) or not data:
                raise ValueError("JSON must contain a non-empty array of objects")

            self.write_csv_from_dict(csv_path, data, delimiter=delimiter, encoding=encoding)
            self.logger.info(f"Converted JSON to CSV: {csv_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error converting from JSON: {str(e)}")
            raise

    def transpose_csv(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> bool:
        """
        Transpose rows and columns in a CSV file.

        Args:
            file_path: Path to the CSV file
            output_path: Optional output file path
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if not data:
                raise ValueError("CSV file is empty")

            # Transpose using zip
            transposed = list(map(list, zip(*data)))

            save_path = output_path or file_path
            self.write_csv(save_path, transposed, delimiter, encoding, mode="w")
            self.logger.info(f"Transposed CSV file")
            return True
        except Exception as e:
            self.logger.error(f"Error transposing CSV: {str(e)}")
            raise

    def backup_file(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """
        Create a backup of a CSV file.

        Args:
            file_path: Path to the CSV file
            backup_suffix: Suffix for backup file

        Returns:
            Path to backup file
        """
        try:
            import shutil

            backup_path = f"{file_path}{backup_suffix}"
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            raise

    def validate_csv(
        self,
        file_path: str,
        expected_columns: Optional[int] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """
        Validate a CSV file structure.

        Args:
            file_path: Path to the CSV file
            expected_columns: Expected number of columns
            delimiter: Field delimiter (default: comma)
            encoding: File encoding (default: utf-8)

        Returns:
            Dictionary with validation results
        """
        try:
            issues = []
            data = self.read_csv(file_path, delimiter, encoding, has_header=False)

            if not data:
                issues.append("File is empty")
                return {"valid": False, "issues": issues}

            column_count = len(data[0])

            # Check expected columns
            if expected_columns and column_count != expected_columns:
                issues.append(f"Expected {expected_columns} columns, found {column_count}")

            # Check consistent column count
            for idx, row in enumerate(data):
                if len(row) != column_count:
                    issues.append(f"Row {idx} has {len(row)} columns, expected {column_count}")

            result = {
                "valid": len(issues) == 0,
                "issues": issues,
                "rows": len(data),
                "columns": column_count,
            }

            self.logger.info(f"Validation result: {'Valid' if result['valid'] else 'Invalid'}")
            return result
        except Exception as e:
            self.logger.error(f"Error validating CSV: {str(e)}")
            raise


# Convenience functions
def read_csv(file_path: str, **kwargs) -> List[List[str]]:
    """Read CSV file."""
    return CSVUtils().read_csv(file_path, **kwargs)


def write_csv(file_path: str, data: List[List[Any]], **kwargs) -> bool:
    """Write data to CSV file."""
    return CSVUtils().write_csv(file_path, data, **kwargs)


def read_csv_dict(file_path: str, **kwargs) -> List[Dict[str, str]]:
    """Read CSV file as dictionaries."""
    return CSVUtils().read_csv_as_dict(file_path, **kwargs)


def write_csv_dict(file_path: str, data: List[Dict[str, Any]], **kwargs) -> bool:
    """Write dictionaries to CSV file."""
    return CSVUtils().write_csv_from_dict(file_path, data, **kwargs)
