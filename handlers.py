import atexit
import logging.config
import logging.handlers
import multiprocessing as mp
import queue
from typing import Dict, List, Union
import pathlib


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extension = pathlib.Path(kwargs["filename"]).suffix
        self.namer = lambda name: name.replace(extension, "") + extension


def _resolve_handlers(handlers: Union[str, logging.config.ConvertingList]) -> List[Dict]:
    """Resolve handlers from a logging configuration.

    Ref: https://rob-blackbourn.medium.com/how-to-use-python-logging-queuehandler-with-dictconfig-1e8b1284e27a"""
    if not isinstance(handlers, logging.config.ConvertingList):
        return handlers

    # Indexing the list performs the evaluation.
    return [handlers[i] for i in range(len(handlers))]


class QueueListenerHandler(logging.handlers.QueueHandler):
    def __init__(self, handlers, respect_handler_level: bool = True, auto_run: bool = True, handler_queue: queue.Queue = None):
        super().__init__(handler_queue or mp.Queue())
        handlers = _resolve_handlers(handlers)
        self._listener = logging.handlers.QueueListener(
            self.queue, *handlers, respect_handler_level=respect_handler_level)
        if auto_run:
            self.start()
            atexit.register(self.stop)

    def start(self) -> None:
        """Start the listener."""
        print("Starting listener")
        self._listener.start()

    def stop(self) -> None:
        """Stop the listener."""
        print("Stopping listener")
        self._listener.stop()

    def emit(self, record):
        """Emit a record."""
        return super().emit(record)


def getHandlerByName(name: str) -> logging.Handler:
    """Get a handler by name.

    Exists natively in Python 3.12 in the logging module."""
    logger = logging.getLogger()
    for handler in logger.handlers:
        if handler.name == name:
            return handler
    raise KeyError(name)
