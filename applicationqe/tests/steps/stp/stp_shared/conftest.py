import pytest


@pytest.fixture
def test_context(test_data):
    """Context to store test data and state across steps"""
    return {"test_data": test_data}


@pytest.fixture(scope="function")
def test_data(all_test_data, request):
    """Load test data from CSV - selects by role if passed in BDD scenario"""
    # Check if role was passed from BDD scenario
    role = getattr(request, "param", None)
    
    if role:
        # Find row matching the role
        for row in all_test_data:
            if row.get("role") == role:
                return row
        # If role not found, raise error
        raise ValueError(f"Role '{role}' not found in test data CSV")
    
    # Default: return first row if no role specified
    return all_test_data[0] if all_test_data else {}
