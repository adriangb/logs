import pytest

from logs import Filter, LogRecord, Logger, get_logger, register_logger, testing
from logs.levels import FiltererLevel


def test_root_logger_level():
    assert get_logger("").level == FiltererLevel.INFO


def test_level_notset():
    logger = get_logger("test")
    assert logger.level == FiltererLevel.NOTSET
    with testing.capture_logs("test") as captured_logs:
        logger.debug("debug")
        logger.info("info")
        logger.error("error")
        logger.critical("critical")
    assert captured_logs.output == ["debug", "info", "error", "critical"]


@pytest.mark.parametrize(
    "logger_level, expected_output", (
        (FiltererLevel.DEBUG, ["debug", "info", "error", "critical"]),
        (FiltererLevel.INFO, ["info", "error", "critical"]),
        (FiltererLevel.ERROR, ["error", "critical"]),
        (FiltererLevel.CRITICAL, ["critical"]),
    )
)
def test_levels(logger_level: FiltererLevel, expected_output: list[str]):
    logger = get_logger("test")
    logger.level = logger_level
    with testing.capture_logs("test") as captured_logs:
        logger.debug("debug")
        logger.info("info")
        logger.error("error")
        logger.critical("critical")
    assert captured_logs.output == expected_output


def not_a_filter(record: LogRecord) -> LogRecord | None:
    if "a" == record.template:
        return None
    return record


def not_b_filter(record: LogRecord) -> LogRecord | None:
    if "b" == record.template:
        return None
    return record


@pytest.mark.parametrize(
    "filters, expected_output", (
        ([], ["a", "b", "c"]),
        ([not_a_filter], ["b", "c"]),
        ([not_b_filter], ["a", "c"]),
        ([not_a_filter, not_b_filter], ["c"]),
        ([not_b_filter, not_a_filter], ["c"]),
    )
)
def test_filters(filters: list[Filter], expected_output: list[str]):
    logger = get_logger("test")
    for filter in filters:
        logger.add_filter(filter)
    with testing.capture_logs("test") as captured_logs:
        logger.info("a")
        logger.info("b")
        logger.info("c")
    assert captured_logs.output == expected_output


@pytest.mark.parametrize(
    "captured_logger,emitting_logger,expected_output", (
        (Logger("grandparent"), Logger("grandparent.parent"), ["test"]),
        (Logger("grandparent"), Logger("grandparent.parent.child"), ["test"]),
        (Logger("grandparent"), Logger("grandparent.parent", propagate=False), []),
        (Logger("grandparent"), Logger("grandparent.parent.child", propagate=False), []),
    )
)
def test_propagation(captured_logger: Logger, emitting_logger: Logger, expected_output: list[str]):
    register_logger(captured_logger)
    register_logger(emitting_logger)
    with testing.capture_logs(captured_logger) as captured_logs:
        emitting_logger.info("test")
    assert captured_logs.output == expected_output


def test_propagation_middle_is_disabled():
    grandparent = get_logger("grandparent")
    parent = get_logger("grandparent.parent")
    child = get_logger("grandparent.parent.child")
    parent.propagate = False
    with testing.capture_logs(grandparent) as captured_logs:
        child.info("test")
    assert captured_logs.output == []
