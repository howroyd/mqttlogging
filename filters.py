import logging.config
import logging.handlers
from typing import Union


class NonErrorFilter(logging.Filter):
    def __init__(self, maxlevel: int = None) -> None:
        super().__init__()
        levelno = getattr(logging, maxlevel or "WARNING")
        self.maxlevel = levelno

    def filter(self, record: logging.LogRecord) -> Union[bool, logging.LogRecord]:
        """Filter out non-error messages."""
        return record.levelno <= self.maxlevel
