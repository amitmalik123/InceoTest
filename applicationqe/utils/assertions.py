"""Minimal assertion helpers for step definitions."""


class Assertions:
    @staticmethod
    def assert_true(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(message)
