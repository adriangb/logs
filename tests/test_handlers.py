from io import StringIO
from datetime import datetime

from logs import StreamHandler, LogRecord
from logs.levels import LogLevel


def test_stream_handler():
    time = datetime(year=2021, month=9, day=1, hour=0, minute=0, second=0)
    record = LogRecord(
        template="test",
        name="test",
        level=LogLevel.INFO,
        extra={},
        created_at=time,
        process=0,
        thread=0
    )
    stream = StringIO()
    handler = StreamHandler(stream=stream)
    handler.handle(record)
    assert stream.getvalue() == "test\n"
