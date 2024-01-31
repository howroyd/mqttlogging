import atexit
import logging.config
import logging.handlers
import multiprocessing as mp
import pathlib
import queue
from typing import Any, Dict, List, Union

import paho.mqtt.client as mqttc


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

    def emit(self, record: logging.LogRecord):
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


class MqttHandler(logging.Handler):
    def __init__(self, *args, mqtt_config: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)

        self._topic = mqtt_config['topic']
        self._qos = mqtt_config.get('qos', 0)
        self._retain = mqtt_config.get('retain', False)
        self._started = False
        self._host = mqtt_config['host']
        self._port = mqtt_config.get('port', 1883)
        self._keepalive = mqtt_config.get('keepalive', 60)
        self._bind_address = mqtt_config.get('bind_address', '')

        self._client = mqttc.Client()
        username = mqtt_config.get('username', None)
        password = mqtt_config.get('password', None)
        if username is not None and password is not None:
            self._client.username_pw_set(username, password)
        print(f"Connecting MQTT logging to {self._host}:{self._port}")
        self._client.connect_async(self._host, self._port, self._keepalive, self._bind_address)
        self.loop_start()

    def emit(self, record: logging.LogRecord):
        """Emit a record."""
        if not self._started:
            self.loop_start()

        try:
            msg = self.format(record)
            self._client.publish(
                topic=self._topic + "/" + record.levelname.lower(),
                payload=msg,
                qos=self._qos,
                retain=self._retain)
            self.flush()
        except Exception:
            self.handleError(record)

    def __del__(self):
        self.loop_stop()

    def loop_start(self):
        if not self._started:
            self._client.loop_start()
            self._started = True

    def loop_stop(self):
        self._client.loop_stop()
        self._started = False
