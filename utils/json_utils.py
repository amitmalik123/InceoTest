"""
JSON utility module for comprehensive JSON file operations.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

from utils.logger import setup_logger


class JSONUtils:
    """Comprehensive utility class for JSON file operations."""

    def __init__(self):
        self.logger = setup_logger(__name__)

    def read_json(
        self, file_path: str, encoding: str = "utf-8"
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Read and parse a JSON file.

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)

        Returns:
            Parsed JSON data (dict or list)

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        try:
            with open(file_path, "r", encoding=encoding) as file:
                data = json.load(file)
                self.logger.info(f"Successfully read JSON from: {file_path}")
                return data
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            raise

    def write_json(
        self,
        file_path: str,
        data: Union[Dict[str, Any], List[Any]],
        indent: int = 4,
        ensure_ascii: bool = False,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> bool:
        """
        Write data to a JSON file.

        Args:
            file_path: Path to the JSON file
            data: Data to write (dict or list)
            indent: Number of spaces for indentation
            ensure_ascii: Escape non-ASCII characters
            encoding: File encoding (default: utf-8)
            create_dirs: Create parent directories if they don't exist

        Returns:
            True if successful
        """
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding=encoding) as file:
                json.dump(data, file, indent=indent, ensure_ascii=ensure_ascii)
                self.logger.info(f"Successfully wrote JSON to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing JSON file {file_path}: {str(e)}")
            raise

    def append_to_json_array(
        self, file_path: str, new_data: Union[Dict[str, Any], List[Any]], encoding: str = "utf-8"
    ) -> bool:
        """
        Append data to a JSON array file.

        Args:
            file_path: Path to the JSON file (must contain an array)
            new_data: Data to append (can be single item or list)
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            # Read existing data
            if os.path.exists(file_path):
                data = self.read_json(file_path, encoding)
                if not isinstance(data, list):
                    raise ValueError("File must contain a JSON array")
            else:
                data = []

            # Append new data
            if isinstance(new_data, list):
                data.extend(new_data)
            else:
                data.append(new_data)

            # Write back
            self.write_json(file_path, data, encoding=encoding)
            self.logger.info(f"Successfully appended data to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error appending to JSON file {file_path}: {str(e)}")
            raise

    def update_json(
        self,
        file_path: str,
        updates: Dict[str, Any],
        encoding: str = "utf-8",
        merge_deep: bool = False,
    ) -> bool:
        """
        Update existing JSON file with new values.

        Args:
            file_path: Path to the JSON file
            updates: Dictionary with updates
            encoding: File encoding (default: utf-8)
            merge_deep: Deep merge nested dictionaries

        Returns:
            True if successful
        """
        try:
            # Read existing data
            data: Any = self.read_json(file_path, encoding)

            if not isinstance(data, dict):
                raise ValueError("File must contain a JSON object")

            # Update data
            if merge_deep:
                data = self._deep_merge(data, updates)
            else:
                data.update(updates)

            # Write back
            self.write_json(file_path, data, encoding=encoding)
            self.logger.info(f"Successfully updated JSON file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating JSON file {file_path}: {str(e)}")
            raise

    def get_value(
        self, file_path: str, key_path: str, default: Any = None, encoding: str = "utf-8"
    ) -> Any:
        """
        Get a value from JSON file using dot notation path.

        Args:
            file_path: Path to the JSON file
            key_path: Dot-separated path to the value (e.g., 'user.address.city')
            default: Default value if key not found
            encoding: File encoding (default: utf-8)

        Returns:
            Value at the specified path or default
        """
        try:
            data: Any = self.read_json(file_path, encoding)
            keys = key_path.split(".")
            for key in keys:
                if isinstance(data, dict):
                    data = data.get(key)
                elif isinstance(data, list) and key.isdigit():
                    data = data[int(key)]
                else:
                    return default

                if data is None:
                    return default

            self.logger.info(f"Retrieved value for '{key_path}' from {file_path}")
            return data
        except Exception as e:
            self.logger.error(f"Error getting value from {file_path}: {str(e)}")
            return default

    def set_value(self, file_path: str, key_path: str, value: Any, encoding: str = "utf-8") -> bool:
        """
        Set a value in JSON file using dot notation path.

        Args:
            file_path: Path to the JSON file
            key_path: Dot-separated path to set (e.g., 'user.address.city')
            value: Value to set
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            data = self.read_json(file_path, encoding)
            keys = key_path.split(".")

            # Ensure top-level object is a dict
            if not isinstance(data, dict):
                raise ValueError("File must contain a JSON object")

            # Navigate to parent
            current: Dict[str, Any] = data
            for key in keys[:-1]:
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]

            # Set value
            current[keys[-1]] = value

            # Write back
            self.write_json(file_path, data, encoding=encoding)
            self.logger.info(f"Set value for '{key_path}' in {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting value in {file_path}: {str(e)}")
            raise

    def delete_key(self, file_path: str, key_path: str, encoding: str = "utf-8") -> bool:
        """
        Delete a key from JSON file using dot notation path.

        Args:
            file_path: Path to the JSON file
            key_path: Dot-separated path to delete (e.g., 'user.address.city')
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:

            data = self.read_json(file_path, encoding)
            keys = key_path.split(".")

            if not isinstance(data, dict):
                self.logger.warning(f"Key path '{key_path}' not found (not a JSON object)")
                return False

            # Navigate to parent
            current: Dict[str, Any] = data
            for key in keys[:-1]:
                if key not in current or not isinstance(current[key], dict):
                    self.logger.warning(f"Key path '{key_path}' not found")
                    return False
                current = current[key]

            # Delete key
            if keys[-1] in current:
                del current[keys[-1]]
                self.write_json(file_path, data, encoding=encoding)
                self.logger.info(f"Deleted key '{key_path}' from {file_path}")
                return True
            else:
                self.logger.warning(f"Key '{keys[-1]}' not found")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting key from {file_path}: {str(e)}")
            raise

    def validate_json(self, file_path: str, encoding: str = "utf-8") -> bool:
        """
        Validate if a file contains valid JSON.

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)

        Returns:
            True if valid JSON, False otherwise
        """
        try:
            self.read_json(file_path, encoding)
            self.logger.info(f"File {file_path} contains valid JSON")
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            self.logger.warning(f"File {file_path} contains invalid JSON or doesn't exist")
            return False

    def merge_json_files(
        self, file_paths: List[str], output_path: str, encoding: str = "utf-8"
    ) -> bool:
        """
        Merge multiple JSON files into one.

        Args:
            file_paths: List of JSON file paths to merge
            output_path: Output file path
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            merged_data: Dict[str, Any] = {}

            for file_path in file_paths:
                data = self.read_json(file_path, encoding)
                if isinstance(data, dict):
                    merged_data = self._deep_merge(merged_data, data)
                else:
                    self.logger.warning(f"Skipping {file_path}: not a JSON object")

            self.write_json(output_path, merged_data, encoding=encoding)
            self.logger.info(f"Successfully merged {len(file_paths)} files to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error merging JSON files: {str(e)}")
            raise

    def pretty_print_json(self, file_path: str, indent: int = 4, encoding: str = "utf-8") -> str:
        """
        Pretty print JSON file content.

        Args:
            file_path: Path to the JSON file
            indent: Number of spaces for indentation
            encoding: File encoding (default: utf-8)

        Returns:
            Pretty-printed JSON string
        """
        try:
            data = self.read_json(file_path, encoding)
            pretty_json = json.dumps(data, indent=indent, ensure_ascii=False)
            return pretty_json
        except Exception as e:
            self.logger.error(f"Error pretty printing JSON: {str(e)}")
            raise

    def minify_json(self, file_path: str, encoding: str = "utf-8") -> bool:
        """
        Minify JSON file (remove whitespace).

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)

        Returns:
            True if successful
        """
        try:
            data = self.read_json(file_path, encoding)

            with open(file_path, "w", encoding=encoding) as file:
                json.dump(data, file, separators=(",", ":"), ensure_ascii=False)

            self.logger.info(f"Successfully minified JSON file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error minifying JSON file: {str(e)}")
            raise

    def search_json(self, file_path: str, search_key: str, encoding: str = "utf-8") -> List[Any]:
        """
        Search for all occurrences of a key in JSON file.

        Args:
            file_path: Path to the JSON file
            search_key: Key to search for
            encoding: File encoding (default: utf-8)

        Returns:
            List of values found for the key
        """
        try:
            data = self.read_json(file_path, encoding)
            results = self._search_recursive(data, search_key)
            self.logger.info(f"Found {len(results)} occurrences of '{search_key}'")
            return results
        except Exception as e:
            self.logger.error(f"Error searching JSON file: {str(e)}")
            raise

    def filter_json_array(
        self,
        file_path: str,
        filter_func,
        output_path: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> List:
        """
        Filter JSON array using a custom function.

        Args:
            file_path: Path to the JSON file (must contain an array)
            filter_func: Function that returns True for items to keep
            output_path: Optional output file path
            encoding: File encoding (default: utf-8)

        Returns:
            Filtered list
        """
        try:
            data = self.read_json(file_path, encoding)

            if not isinstance(data, list):
                raise ValueError("File must contain a JSON array")

            filtered_data = [item for item in data if filter_func(item)]

            if output_path:
                self.write_json(output_path, filtered_data, encoding=encoding)
                self.logger.info(f"Filtered data written to: {output_path}")

            self.logger.info(f"Filtered {len(data)} items to {len(filtered_data)} items")
            return filtered_data
        except Exception as e:
            self.logger.error(f"Error filtering JSON array: {str(e)}")
            raise

    def convert_to_json_string(self, data: Union[Dict, List], indent: Optional[int] = None) -> str:
        """
        Convert Python object to JSON string.

        Args:
            data: Data to convert
            indent: Optional indentation for pretty formatting

        Returns:
            JSON string
        """
        try:
            json_str = json.dumps(data, indent=indent, ensure_ascii=False)
            return json_str
        except Exception as e:
            self.logger.error(f"Error converting to JSON string: {str(e)}")
            raise

    def parse_json_string(self, json_str: str) -> Union[Dict, List]:
        """
        Parse JSON string to Python object.

        Args:
            json_str: JSON string to parse

        Returns:
            Parsed data (dict or list)
        """
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON string: {str(e)}")
            raise

    def compare_json_files(
        self, file_path1: str, file_path2: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Compare two JSON files.

        Args:
            file_path1: First JSON file path
            file_path2: Second JSON file path
            encoding: File encoding (default: utf-8)

        Returns:
            Dictionary with comparison results
        """
        try:
            data1 = self.read_json(file_path1, encoding)
            data2 = self.read_json(file_path2, encoding)

            result = {"are_equal": data1 == data2, "file1": file_path1, "file2": file_path2}

            if not result["are_equal"]:
                result["differences"] = self._find_differences(data1, data2)

            self.logger.info(f"Compared {file_path1} and {file_path2}")
            return result
        except Exception as e:
            self.logger.error(f"Error comparing JSON files: {str(e)}")
            raise

    def backup_json(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """
        Create a backup of a JSON file.

        Args:
            file_path: Path to the JSON file
            backup_suffix: Suffix for backup file

        Returns:
            Path to backup file
        """
        try:
            backup_path = f"{file_path}{backup_suffix}"
            data = self.read_json(file_path)
            self.write_json(backup_path, data)
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            raise

    # Helper methods
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result: Dict[str, Any] = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _search_recursive(
        self, data: Any, search_key: str, results: Optional[List[Any]] = None
    ) -> List[Any]:
        """Recursively search for a key in nested structures."""
        if results is None:
            results = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == search_key:
                    results.append(value)
                self._search_recursive(value, search_key, results)
        elif isinstance(data, list):
            for item in data:
                self._search_recursive(item, search_key, results)

        return results

    def _find_differences(self, data1: Any, data2: Any, path: str = "") -> List[Dict[str, Any]]:
        """Find differences between two data structures."""
        differences: List[Dict[str, Any]] = []

        if type(data1) is not type(data2):
            differences.append(
                {
                    "path": path,
                    "type": "type_mismatch",
                    "value1": str(type(data1)),
                    "value2": str(type(data2)),
                }
            )
            return differences

        if isinstance(data1, dict):
            all_keys = set(data1.keys()) | set(data2.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key

                if key not in data1:
                    differences.append(
                        {"path": new_path, "type": "missing_in_first", "value": data2[key]}
                    )
                elif key not in data2:
                    differences.append(
                        {"path": new_path, "type": "missing_in_second", "value": data1[key]}
                    )
                else:
                    differences.extend(self._find_differences(data1[key], data2[key], new_path))

        elif isinstance(data1, list):
            if len(data1) != len(data2):
                differences.append(
                    {
                        "path": path,
                        "type": "length_mismatch",
                        "length1": len(data1),
                        "length2": len(data2),
                    }
                )

        elif data1 != data2:
            differences.append(
                {"path": path, "type": "value_mismatch", "value1": data1, "value2": data2}
            )

        return differences


# Convenience functions
def read_json(file_path: str, **kwargs) -> Union[Dict, List]:
    """Read JSON file."""
    return JSONUtils().read_json(file_path, **kwargs)


def write_json(file_path: str, data: Union[Dict, List], **kwargs) -> bool:
    """Write data to JSON file."""
    return JSONUtils().write_json(file_path, data, **kwargs)


def get_json_value(file_path: str, key_path: str, **kwargs) -> Any:
    """Get value from JSON file using dot notation."""
    return JSONUtils().get_value(file_path, key_path, **kwargs)


def update_json_file(file_path: str, updates: Dict, **kwargs) -> bool:
    """Update JSON file with new values."""
    return JSONUtils().update_json(file_path, updates, **kwargs)
