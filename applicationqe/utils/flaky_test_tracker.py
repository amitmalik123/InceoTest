"""
Flaky Test Tracker - Detects and reports flaky tests

Tracks:
- Tests that pass after retries (flaky)
- Tests with inconsistent failures
- Retry counts and patterns
- Flaky test history
"""

import os
from datetime import datetime
from typing import Dict, Optional


class FlakyTestTracker:
    """Track and report flaky tests"""

    def __init__(self):
        from config.settings import get_settings

        self.environment = os.getenv("ENVIRONMENT", get_settings().env)
        self.build_id = os.getenv("BUILD_ID", "local")

        # Track flaky tests during session
        self.flaky_tests: Dict[str, Dict] = {}

    def record_flaky_test(
        self,
        test_name: str,
        test_id: str,
        total_attempts: int,
        failed_attempts: int,
        final_status: str,
        duration_ms: int,
        error_message: Optional[str] = None,
    ):
        """Record a flaky test occurrence"""
        self.flaky_tests[test_id] = {
            "test_name": test_name,
            "test_id": test_id,
            "total_attempts": total_attempts,
            "failed_attempts": failed_attempts,
            "final_status": final_status,
            "duration_ms": duration_ms,
            "error_message": error_message or "",
            "timestamp": datetime.now(),
            "environment": self.environment,
            "build_id": self.build_id,
        }

        print("\n⚠️  FLAKY TEST DETECTED:")
        print(f"   Test: {test_name}")
        print(f"   Attempts: {total_attempts} (failed: {failed_attempts})")
        print(f"   Final Status: {final_status}")
        print(f"   Duration: {duration_ms}ms")
        if error_message:
            print(f"   Error: {error_message[:100]}...")

    def get_flaky_summary(self) -> Dict:
        """Get summary of flaky tests in current session"""
        return {
            "total_flaky_tests": len(self.flaky_tests),
            "flaky_tests": [
                {
                    "name": data["test_name"],
                    "attempts": data["total_attempts"],
                    "failed": data["failed_attempts"],
                    "status": data["final_status"],
                }
                for data in self.flaky_tests.values()
            ],
        }


# Global tracker instance
_tracker = None


def get_tracker() -> FlakyTestTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = FlakyTestTracker()
    return _tracker
