import os


class Branch:
    """Branch test names exposed from environment variables."""

    test_branch_name_1: str = os.getenv("TEST_BRANCH_NAME_1", "")
    test_branch_name_2: str = os.getenv("TEST_BRANCH_NAME_2", "")


__all__ = ["Branch"]
