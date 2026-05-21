# Root conftest.py
# Fixtures live outside the tests/ tree (under fixtures/), so pytest cannot
# auto-discover them. Register them here as plugins so they are available
# to every test in this project.
pytest_plugins = [
    "fixtures.salesforce.salesforce_fixtures",
]
