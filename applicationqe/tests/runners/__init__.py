"""
BDD Test Runners Package

This package contains pytest test files that execute BDD scenarios.
Each test file uses pytest-bdd's scenarios() function to load and run
feature files with their corresponding step definitions.

Subpackages:
- oam/ - OAM (Online Account Management) test runner

Usage:
    pytest tests/runners/oam/test_OAM.py
"""

__all__: list[str] = []
