import logging.config
import logging.handlers
from typing import Union


class NonErrorFilter(logging.Filter):
    """Filter out messages higher than a specific level, e.g. warning and errors.

    Intended so you can have a buffered handler that logs to stdout and a non-buffered handler that logs to stderr, without duplicates.

    Ref: https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/135_modern_logging/mylogger.py
    """

    def __init__(self, maxlevel: int = None) -> None:
        super().__init__()
        levelno = getattr(logging, maxlevel or "WARNING")
        self.maxlevel = levelno

    def filter(self, record: logging.LogRecord) -> Union[bool, logging.LogRecord]:
        """Filter out non-error messages."""
        return record.levelno <= self.maxlevel
