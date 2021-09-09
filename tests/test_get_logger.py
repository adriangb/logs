import pytest

from logs import get_logger


def test_get_root_logger():
    logger = get_logger("")
    assert logger.name == ""


@pytest.mark.parametrize("name", ("", "one", "one.two"))
def test_get_existing_logger(name: str):
    logger = get_logger(name)
    assert get_logger(name) is logger


def test_get_logger_parents():
    logger = get_logger("one.two.three")
    assert logger.name == "one.two.three", logger.name
    assert logger.parent.name == "one.two", logger.parent.name
    assert logger.parent.parent.name == "one", logger.parent.parent.name
    assert logger.parent.parent.parent is get_logger("")


def test_get_logger_children():
    child_one = get_logger("parent.child_one")
    child_two = get_logger("parent.child_two")
    assert child_one.parent == child_two.parent
