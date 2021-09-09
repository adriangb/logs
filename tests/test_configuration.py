import sys
from tempfile import TemporaryFile

import pytest

from logs import StreamHandler, get_logger
from tests.utils import redirect_stream


@pytest.mark.usefixtures("reset_logging")
def test_default_logging_config():
    # should have a root logger emitting to stderr
    logger = get_logger("test")
    root_logger = get_logger("")
    with TemporaryFile(mode="w+") as output:
        with redirect_stream(sys.stderr, output):
            logger.info("test")
            handler = root_logger.handlers[0]
            assert isinstance(
                handler, StreamHandler
            ), "The root logger should be configured with a StreamHandler by default"
            handler.stream.flush()
        output.seek(0)
        assert output.read() == "test\n"
