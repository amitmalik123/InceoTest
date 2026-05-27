from contextlib import contextmanager
import logging


class _WrapperModelLogger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def debug(self, msg: str, attach_to_allure: bool = True) -> None:
        self._logger.debug(msg)

    def info(self, msg: str, attach_to_allure: bool = True) -> None:
        self._logger.info(msg)

    def warning(self, msg: str, attach_to_allure: bool = True) -> None:
        self._logger.warning(msg)

    def error(self, msg: str, attach_to_allure: bool = True) -> None:
        self._logger.error(msg)

    @contextmanager
    def step(self, title: str):
        self._logger.info(title)
        yield

    def attach_text(self, text: str, name: str = "Text") -> None:
        self._logger.info("%s: %s", name, text)

    def attach_screenshot(self, page, name: str = "Screenshot") -> None:
        self._logger.info(name)


def get_allure_logger(name: str) -> _WrapperModelLogger:
    return _WrapperModelLogger(name)
