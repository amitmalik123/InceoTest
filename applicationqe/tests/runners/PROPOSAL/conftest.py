"""
PROPOSAL-specific conftest.

Overrides test_context so PROPOSAL tests always authenticate as Internal Admin,
pulling credentials from config/PROPOSAL/env.{env}.yaml instead of the Excel
file. PROPOSAL steps carry their own workflow data inline — no Excel row needed.
"""

import pytest


@pytest.fixture
def test_context():
    """Always resolve to Internal Admin for PROPOSAL tests."""
    return {"test_data": {"UserRole": "Internal Admin"}}
