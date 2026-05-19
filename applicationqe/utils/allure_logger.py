"""Lightweight compatibility logger used by BDD steps and page objects."""

import json
import logging
from typing import Any


class AllureLogger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def info(self, message: str, attach_to_allure: bool = False) -> None:
        self._logger.info(message)
        if attach_to_allure:
            self._attach_text(message, "info")

    def warning(self, message: str, attach_to_allure: bool = False) -> None:
        self._logger.warning(message)
        if attach_to_allure:
            self._attach_text(message, "warning")

    def error(self, message: str, attach_to_allure: bool = False) -> None:
        self._logger.error(message)
        if attach_to_allure:
            self._attach_text(message, "error")

    def attach_json(self, payload: Any, name: str = "payload") -> None:
        self._attach_text(json.dumps(payload, indent=2, default=str), name)

    def _attach_text(self, body: str, name: str) -> None:
        try:
            import allure

            allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)
        except Exception:
            # Allure is optional in local runs; do not break test execution.
            pass


def get_allure_logger(name: str) -> AllureLogger:
    return AllureLogger(name)
