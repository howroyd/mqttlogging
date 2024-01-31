import concurrent.futures as cf
import functools
import logging.config
import logging.handlers
import multiprocessing as mp
from typing import Union

import tomlkit


def deep_merge(dest: dict, src: dict, path=[]):
    for key in src:
        if key in dest:
            if isinstance(dest[key], dict) and isinstance(src[key], dict):
                deep_merge(dest[key], src[key], path + [str(key)])
            elif dest[key] != src[key]:
                raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
        else:
            dest[key] = src[key]
    return dest


def to_dict(tomldoc: Union[tomlkit.TOMLDocument, tomlkit.items.Table]) -> dict:
    """Convert a TOML document to a dict."""
    for key, value in tomldoc.items():
        if isinstance(value, tomlkit.items.Table):
            tomldoc[key] = to_dict(value)
    return dict(tomldoc)


def setup_logging(config_filename: str, secrets: str = None) -> logging.Logger:
    """Setup logging."""
    config = None
    with open(config_filename, 'r') as f:
        config = to_dict(tomlkit.load(f))
    assert config is not None

    if secrets:
        with open(secrets, 'r') as f:
            secrets = to_dict(tomlkit.load(f))
        if secrets:
            functools.reduce(deep_merge, [config, secrets])

    logging.config.dictConfig(config)

    return logging.getLogger()


def do_something(n: int, level: str = None) -> None:
    logger = logging.getLogger()
    logging.basicConfig(level=level or "INFO")
    logger.debug(f"{n} debug message", extra={"x": "hello"})
    logger.info(f"{n} info message")
    logger.info(
        f"{n} warning message (basicConfig level is {level}) {mp.current_process()}")
    logger.error(f"{n} error message")
    logger.critical(f"{n} critical message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception(f"{n} exception message")


def main():
    logger = setup_logging("example_config.toml", secrets="secrets.toml")

    logger.critical("Starting main")

    workers = [
        functools.partial(do_something, level="DEBUG"),
        functools.partial(do_something, level="INFO"),
        functools.partial(do_something, level="WARNING"),
        functools.partial(do_something, level="ERROR"),
        functools.partial(do_something, level="CRITICAL"),
    ]

    # processes = [mp.Process(target=fn, args=(i,))
    #              for i, fn in enumerate(workers)]
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join()

    with cf.ProcessPoolExecutor() as executor:
        #  NOTE: On Python 3.8 this will throw at exit https://github.com/python/cpython/issues/83285
        for i, fn in enumerate(workers):
            executor.submit(functools.partial(fn, i))

    logger.critical("Ending main\n\n")


if __name__ == "__main__":
    mp.freeze_support()
    main()
