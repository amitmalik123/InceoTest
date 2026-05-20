"""
Tests Package

This package contains all test modules organized by type:

BDD Tests (using pytest-bdd):
- features/ - Gherkin feature files (.feature)
- steps/ - Step definitions implementing feature steps
- runners/ - Pytest test files that execute scenarios
- bdd/conftest.py - BDD-specific fixtures and configuration

Other test types:
- api/ - API integration tests
- fixtures/ - Test fixtures and utilities (shared by all tests)

All test fixtures are automatically discovered from conftest.py files.
"""

__all__: list[str] = []
