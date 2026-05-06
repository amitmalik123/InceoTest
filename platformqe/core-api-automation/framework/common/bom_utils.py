"""
BOM Utility - Remove UTF-8 BOM from JSON files
===============================================

This module provides utilities to detect and remove UTF-8 Byte Order Mark (BOM)
from JSON files that can cause pytest collection and JSON parsing failures.

Functions:
    fix_bom(file_path): Remove BOM from a single JSON file
    fix_bom_recursive(directory, pattern): Fix BOM in all matching files recursively
    check_bom(file_path): Check if a file has BOM without modifying it

Usage:
    # Fix single file
    python -c "from framework.common.bom_utils import fix_bom; fix_bom('testdata/parties/testcases/test.json')"
    
    # Fix all JSON files in a directory
    python -c "from framework.common.bom_utils import fix_bom_recursive; fix_bom_recursive('testdata')"
    
    # Check for BOM
    python -c "from framework.common.bom_utils import check_bom; print(check_bom('test.json'))"
"""

import json
from pathlib import Path
from typing import List, Optional


def check_bom(file_path: str) -> bool:
    """
    Check if a file has UTF-8 BOM without modifying it.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file has BOM, False otherwise
        
    Example:
        >>> check_bom('testdata/parties/testcases/TestCase.json')
        True
    """
    try:
        with open(file_path, 'rb') as f:
            first_bytes = f.read(3)
            return first_bytes == b'\xef\xbb\xbf'
    except Exception:
        return False


def fix_bom(file_path: str, verbose: bool = True) -> str:
    """
    Remove UTF-8 BOM from a JSON file.
    
    Reads the file with utf-8-sig encoding (which automatically strips BOM)
    and writes it back with clean utf-8 encoding.
    
    Args:
        file_path: Path to the JSON file to fix
        verbose: Print success message (default: True)
        
    Returns:
        Success message string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        
    Example:
        >>> fix_bom('testdata/parties/testcases/TestCase_GET.json')
        '✓ Fixed testdata/parties/testcases/TestCase_GET.json'
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read with BOM handling
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Write back without BOM
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    message = f"✓ Fixed {file_path}"
    if verbose:
        print(message)
    
    return message


def fix_bom_recursive(
    directory: str, 
    pattern: str = "*.json",
    verbose: bool = True
) -> List[str]:
    """
    Recursively fix BOM in all files matching the pattern in a directory.
    
    Args:
        directory: Root directory to search
        pattern: File pattern to match (default: "*.json")
        verbose: Print progress messages (default: True)
        
    Returns:
        List of fixed file paths
        
    Example:
        >>> fix_bom_recursive('testdata', pattern='TestCase_*.json')
        ['testdata/parties/testcases/TestCase_GET.json', ...]
    """
    directory = Path(directory)
    fixed_files = []
    failed_files = []
    
    if not directory.exists():
        print(f"⚠ Directory not found: {directory}")
        return []
    
    if verbose:
        print(f"\n🔍 Scanning {directory} for {pattern} files...")
    
    # Find all matching files
    files = list(directory.rglob(pattern))
    
    if not files:
        if verbose:
            print(f"⚠ No files matching '{pattern}' found in {directory}")
        return []
    
    if verbose:
        print(f"📂 Found {len(files)} files to process\n")
    
    # Process each file
    for file_path in files:
        try:
            fix_bom(str(file_path), verbose=False)
            fixed_files.append(str(file_path))
            if verbose:
                print(f"✓ {file_path}")
        except Exception as e:
            failed_files.append(str(file_path))
            if verbose:
                print(f"✗ {file_path}: {e}")
    
    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"✓ Successfully fixed: {len(fixed_files)} files")
        if failed_files:
            print(f"✗ Failed: {len(failed_files)} files")
        print(f"{'='*60}\n")
    
    return fixed_files


def fix_testcase_file(testcase_file: Optional[str]) -> None:
    """
    Fix BOM in a testcase file if it exists.
    
    This is a convenience function used by conftest.py during pytest configuration.
    Silently handles errors to avoid breaking test collection.
    
    Args:
        testcase_file: Path to testcase file (can be None)
        
    Example:
        >>> fix_testcase_file('testdata/parties/testcases/TestCase_GET.json')
    """
    if testcase_file and Path(testcase_file).exists():
        try:
            fix_bom(testcase_file, verbose=False)
        except Exception:
            pass  # Silently continue if auto-fix fails


if __name__ == "__main__":
    """
    Command-line interface for BOM utilities.
    
    Usage:
        python framework/common/bom_utils.py check <file>
        python framework/common/bom_utils.py fix <file>
        python framework/common/bom_utils.py fix-all <directory>
    """
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check" and len(sys.argv) == 3:
        file_path = sys.argv[2]
        has_bom = check_bom(file_path)
        print(f"{'✓ BOM detected' if has_bom else '✗ No BOM'} in {file_path}")
    
    elif command == "fix" and len(sys.argv) == 3:
        file_path = sys.argv[2]
        fix_bom(file_path)
    
    elif command == "fix-all" and len(sys.argv) >= 3:
        directory = sys.argv[2]
        pattern = sys.argv[3] if len(sys.argv) == 4 else "*.json"
        fix_bom_recursive(directory, pattern)
    
    else:
        print("Invalid command. Usage:")
        print("  python framework/common/bom_utils.py check <file>")
        print("  python framework/common/bom_utils.py fix <file>")
        print("  python framework/common/bom_utils.py fix-all <directory> [pattern]")
        sys.exit(1)
