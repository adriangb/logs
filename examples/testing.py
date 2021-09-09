from logs import Formatter, LogRecord, get_logger
from logs.testing import capture_logs


def main():
    logger = get_logger(__name__)

    class CustomFormatter(Formatter):
        def format_time(self, record: LogRecord) -> str:
            return "2021"

    with capture_logs(formatter=CustomFormatter(fmt="{message} - {created_at}")) as logs:
        logger.info("Test", extra=dict(key="value"))

    assert logs.records[0].extra == dict(key="value"), logs.records[0].extra
    assert logs.output[0] == "Test - 2021", logs.output[0]


if __name__ == "__main__":
    main()
