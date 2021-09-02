from datetime import datetime

from logs import Formatter, LogRecord
from logs.levels import LogLevel
from logs.testing import CapturingHandler, CapturedRecord


def test_formatter():
    formatter = Formatter(fmt="{created_at} - {data[test1]}: {message}")
    time = datetime(year=2021, month=9, day=1, hour=0, minute=0, second=0)
    record = LogRecord(
        template="{data[test2]}",
        name="test",
        level=LogLevel.INFO,
        data={"test1": "val1", "test2": "val2"},
        created_at=time,
        process=0,
        thread=0
    )
    recorder = CapturedRecord([], [])
    handler = CapturingHandler(recorder=recorder)
    handler.formatter = formatter
    handler.handle(record)
    assert recorder.output == ["2021-09-01T00:00:00 - val1: val2"]
