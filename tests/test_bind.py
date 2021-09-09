import asyncio
from threading import Event, Thread

import pytest

from logs import Logger, get_logger
from logs.bind import bind
from logs.testing import capture_logs


@pytest.fixture
def logger() -> Logger:
    return get_logger("test")


def test_bind_context_management(logger: Logger):
    with capture_logs() as logs:
        logger.info("TEST")
        with bind(logger, key="value"):
            logger.info("TEST")
            with bind(logger, secondkey="value2"):
                logger.info("TEST")
        logger.info("TEST")

    assert "key" not in logs.records[0].extra
    assert logs.records[1].extra["key"] == "value"
    assert logs.records[2].extra["key"] == "value"
    assert logs.records[2].extra["secondkey"] == "value2"
    assert "key" not in logs.records[3].extra


def test_thread_safety(logger: Logger):
    """If a different thread is using the same logger, it should not be affected by the bind"""

    log = Event()
    logged = Event()

    def log_in_thread():
        while True:
            if log.is_set():
                # log once
                logger.info("TEST")
                with bind(logger, other=123):
                    logger.info("TEST")
                log.clear()
                logged.set()
                return

    with capture_logs() as logs:
        t = Thread(target=log_in_thread)
        t.start()
        with bind(logger, key="value"):
            log.set()
            assert logged.wait(1)
        t.join()

    assert "key" not in logs.records[0].extra
    assert logs.records[1].extra["other"] == 123


def test_coroutine_in_bind(logger: Logger):
    """Coroutines launched from within a bind should use it"""

    async def log_in_coro():
        logger.info("from thread")
        with bind(logger, other=123):
            logger.info("TEST")

    with capture_logs() as logs:
        with bind(logger, key="value"):
            asyncio.run(log_in_coro())

    assert logs.records[0].extra["key"] == "value"
    assert logs.records[1].extra["key"] == "value"
    assert logs.records[1].extra["other"] == 123


def test_coroutine_concurrent_with_bind(logger: Logger):
    """Coroutines launched concurrently but outside of a bind should NOT use it"""
    bound = False

    async def enter_bind():
        nonlocal bound
        with bind(logger, key="value"):
            bound = True
            await asyncio.sleep(float("inf"))

    async def log():
        while not bound:
            asyncio.sleep(0.1)
        logger.info("TEST")

    async def run():
        binder_task = asyncio.Task(enter_bind())
        logger_task = asyncio.Task(log())
        await asyncio.wait((binder_task, logger_task), return_when=asyncio.FIRST_COMPLETED)
        binder_task.cancel()

    with capture_logs() as logs:
        asyncio.run(run())

    assert "key" not in logs.records[0].extra


def test_exception_handling(logger: Logger):
    with capture_logs() as logs:
        try:
            with bind(logger, key="value"):
                logger.info("TEST")
                raise ValueError
        except ValueError:
            pass
        logger.info("TEST")
    assert logs.records[0].extra["key"] == "value"
    assert "key" not in logs.records[1].extra
