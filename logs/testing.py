import typing as t
from contextlib import contextmanager

from logs import Filter, Formatter, Handler, Logger, LogRecord, get_logger
from logs.levels import FiltererLevel


class CapturedRecord(t.NamedTuple):
    records: t.List[LogRecord]
    output: t.List[str]


class CapturingHandler(Handler):
    def __init__(
        self,
        level: t.Union[str, int] = FiltererLevel.NOTSET,
        *,
        recorder: CapturedRecord,
    ) -> None:
        super().__init__(level=level)
        self.recorder = recorder

    def handle(self, record: LogRecord) -> None:
        msg = self.formatter.format(record)
        self.recorder.records.append(record)
        self.recorder.output.append(msg)


@contextmanager
def capture_logs(
    logger: Logger | str | None = None,
    level: int | str | None = None,
    *,
    formatter: Formatter | None = None,
    filters: t.Sequence[Filter] | None = None,
) -> t.Generator[CapturedRecord, None, None]:
    filters = filters or []
    filters = list(filters)

    logger = logger or ""
    if not isinstance(logger, Logger):
        logger = get_logger(logger)

    level = level if level is not None else logger.level
    original_level = logger.level
    logger.level = level

    recorder = CapturedRecord([], [])
    handler = CapturingHandler(level=level, recorder=recorder)
    if formatter is not None:
        handler.formatter = formatter
    for filter in filters or []:
        handler.add_filter(filter)

    logger.add_handler(handler)

    try:
        yield recorder
    finally:
        logger.level = original_level
        logger.handlers.pop()  # remove handler we just added
