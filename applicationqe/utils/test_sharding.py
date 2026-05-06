"""
Test sharding configuration for distributed test execution.

This module provides utilities for sharding tests across multiple machines
or CI/CD pipeline jobs for faster test execution.
"""

import hashlib
import os
from typing import List, Optional


class TestShard:
    """Configuration for test sharding."""

    def __init__(self, shard_index: int, total_shards: int):
        """
        Initialize test shard configuration.

        Args:
            shard_index: Current shard index (0-based)
            total_shards: Total number of shards
        """
        if shard_index >= total_shards:
            raise ValueError(f"shard_index ({shard_index}) must be < total_shards ({total_shards})")
        if shard_index < 0:
            raise ValueError(f"shard_index must be >= 0, got {shard_index}")
        if total_shards < 1:
            raise ValueError(f"total_shards must be >= 1, got {total_shards}")

        self.shard_index = shard_index
        self.total_shards = total_shards

    def should_run_test(self, test_id: str) -> bool:
        """
        Determine if a test should run in this shard.

        Args:
            test_id: Unique test identifier

        Returns:
            bool: True if test should run in this shard
        """
        # Use hash-based distribution for even test distribution
        test_hash = int(hashlib.md5(test_id.encode()).hexdigest(), 16)
        return test_hash % self.total_shards == self.shard_index

    @classmethod
    def from_environment(cls) -> Optional["TestShard"]:
        """
        Create TestShard from environment variables.

        Environment variables:
            TEST_SHARD_INDEX: Current shard index (0-based)
            TEST_SHARD_TOTAL: Total number of shards

        Returns:
            TestShard or None if environment variables not set
        """
        shard_index = os.environ.get("TEST_SHARD_INDEX")
        total_shards = os.environ.get("TEST_SHARD_TOTAL")

        if shard_index is None or total_shards is None:
            return None

        return cls(int(shard_index), int(total_shards))

    def __repr__(self) -> str:
        return f"TestShard({self.shard_index + 1}/{self.total_shards})"


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to filter tests based on sharding configuration.

    This hook is called by pytest after test collection.
    """
    shard = TestShard.from_environment()

    if shard is None:
        # No sharding configured
        return

    print(f"\nRunning test shard: {shard}")

    # Filter tests based on shard configuration
    selected_items = []
    deselected_items = []

    for item in items:
        if shard.should_run_test(item.nodeid):
            selected_items.append(item)
        else:
            deselected_items.append(item)

    # Update items list (in-place modification required by pytest)
    items[:] = selected_items

    # Log sharding statistics
    print(f"Selected {len(selected_items)} tests for this shard")
    print(f"Deselected {len(deselected_items)} tests (running in other shards)")

    config.hook.pytest_deselected(items=deselected_items)


def calculate_optimal_shards(total_tests: int, max_tests_per_shard: int = 50) -> int:
    """
    Calculate optimal number of shards based on total test count.

    Args:
        total_tests: Total number of tests
        max_tests_per_shard: Maximum tests per shard (default: 50)

    Returns:
        int: Recommended number of shards
    """
    if total_tests <= max_tests_per_shard:
        return 1

    shards = (total_tests + max_tests_per_shard - 1) // max_tests_per_shard
    return shards


def get_shard_info() -> dict:
    """
    Get current shard configuration information.

    Returns:
        dict: Shard configuration details
    """
    shard = TestShard.from_environment()

    if shard is None:
        return {
            "enabled": False,
            "shard_index": None,
            "total_shards": None,
        }

    return {
        "enabled": True,
        "shard_index": shard.shard_index,
        "total_shards": shard.total_shards,
        "description": str(shard),
    }


# CLI helper for sharding
def print_shard_distribution(test_ids: List[str], total_shards: int):
    """
    Print test distribution across shards for analysis.

    Args:
        test_ids: List of test IDs
        total_shards: Number of shards to distribute across
    """
    print(f"\nTest Distribution Across {total_shards} Shards:")
    print("=" * 60)

    for shard_index in range(total_shards):
        shard = TestShard(shard_index, total_shards)
        shard_tests = [tid for tid in test_ids if shard.should_run_test(tid)]
        print(f"Shard {shard_index + 1}/{total_shards}: {len(shard_tests)} tests")

    print("=" * 60)


if __name__ == "__main__":
    # Example usage for testing distribution
    test_ids = [f"test_{i}" for i in range(100)]
    print_shard_distribution(test_ids, 4)
