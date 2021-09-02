from datetime import datetime
from logs import LogRecord
from logs.levels import LogLevel


def test_message_formatting():
    record = LogRecord(
        "{data[test]}",
        name="test",
        level=LogLevel.INFO,
        data={"test": 1},
        created_at=datetime.now(),
        process=0,
        thread=0
    )
    assert record.message == "1"
