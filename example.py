import concurrent.futures as cf
import functools
import logging.config
import logging.handlers
import multiprocessing as mp

import tomlkit


def setup_logging(config_filename: str) -> logging.Logger:
    """Setup logging."""
    config = None
    with open(config_filename, 'r') as f:
        config = tomlkit.load(f)
    assert config is not None

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
    logger = setup_logging("example_config.toml")
    logger.critical("Starting main")

    workers = [
        functools.partial(do_something, level="DEBUG"),
        functools.partial(do_something, level="INFO"),
        functools.partial(do_something, level="WARNING"),
        functools.partial(do_something, level="ERROR"),
        functools.partial(do_something, level="CRITICAL"),
    ]

    processes = [mp.Process(target=fn, args=(i,))
                 for i, fn in enumerate(workers)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    with cf.ProcessPoolExecutor() as executor:
        #  NOTE: On Python 3.8 this will throw at exit https://github.com/python/cpython/issues/83285
        for i, fn in enumerate(workers):
            executor.submit(functools.partial(fn, i))

    logger.critical("Ending main\n\n")


if __name__ == "__main__":
    mp.freeze_support()
    main()
