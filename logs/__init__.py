import itertools
import functools
import typing as t
import os
import threading
import sys
from dataclasses import dataclass, replace
from datetime import datetime

from logs.levels import LogLevel, FiltererLevel


@dataclass
class LogRecord:
    template: str
    name: str
    level: LogLevel
    extra: t.MutableMapping[str, t.Any]
    created_at: datetime
    process: int
    thread: int

    @functools.cached_property
    def message(self):
        return self.template.format(**vars(self))
    
    def copy(self):
        return replace(self)


class Formatter:

    def __init__(self, fmt: str = "{message}") -> None:
        self.fmt = fmt

    def format_message(self, record: LogRecord) -> str:
        return record.message

    def format_time(self, record: LogRecord) -> str:
        return record.created_at.isoformat()

    def format(self, record: LogRecord) -> str:
        return self.fmt.format(
            **{
                **vars(record),
                "message": self.format_message(record),
                "created_at": self.format_time(record)
            }
        )


class Filter(t.Protocol):
    def __call__(self, record: LogRecord) -> LogRecord | None:
        ...


class Filterer:

    filters: list[Filter]
    level: FiltererLevel

    def __init__(
        self,
        level: FiltererLevel = FiltererLevel.NOTSET,
    ) -> None:
        self._lock = threading.RLock()
        self.filters = []
        self.level = level
    
    def at_level(self, level: FiltererLevel) -> bool:
        if level.value < self.level.value:
            return False
        return True

    def filter(self, record: LogRecord) -> LogRecord | None:
        if not self.at_level(record.level):
            return None
        for filter in self.filters:
            record = filter(record)
            if not record:
                break
        return record

    def add_filter(self, filter: Filter) -> None:
        with self._lock:
            self.filters.append(filter)

    def remove_filter(self, filter: Filter) -> None:
        with self._lock:
            for other_idx, other in enumerate(self.filters):
                if filter is other:
                    self.filters.pop(other_idx)
                    return
        raise ValueError(f"Filter {filter} not found amongst the current filters")


class Handler(Filterer):

    formatter: Formatter

    def __init__(
        self,
        level: FiltererLevel = FiltererLevel.NOTSET,
    ) -> None:
        super().__init__(level=level)
        self.formatter = Formatter()

    def handle(self, record: LogRecord) -> None:
        ...


class StreamHandler(Handler):

    def __init__(
        self,
        level: FiltererLevel = FiltererLevel.NOTSET,
        stream: t.TextIO = sys.stderr
    ) -> None:
        super().__init__(level=level)
        self.stream = stream
        self._stream_lock = threading.RLock()

    def handle(self, record: LogRecord) -> None:
        record = self.filter(record)
        if record is None:
            return
        with self._stream_lock:
            self.stream.write(self.formatter.format(record))
            self.stream.write("\n")


class Logger(Filterer):
    handlers: list[Handler]
    parent: "Logger"

    def __init__(
        self,
        name: str,
        level: FiltererLevel = FiltererLevel.NOTSET,
        propagate: bool = True,
    ) -> None:
        super().__init__(level=level)
        self.name = name
        self.propagate = propagate
        self.parent = None
        self.handlers = []

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __repr__(self) -> str:
        return f"Logger(\"{self.name}\")"

    def add_handler(self, handler: Handler) -> None:
        with self._lock:
            self.handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        with self._lock:
            for other_idx, other in enumerate(self.handlers):
                if handler is other:
                    self.handlers.pop(other_idx)
                    return
        raise ValueError(f"Handler {handler} not found amongst the current handlers")

    def log(self, record: LogRecord) -> None:
        record = self.filter(record)
        if record is None:
            return
        for handler in self.handlers:
            handler.handle(record)
        if self.propagate and self.parent:
            self.parent.log(record)

    def _create_record(
        self,
        template: str,
        level: LogLevel,
        extra: dict[str, t.Any] | None
    ):
        return LogRecord(
            template=template,
            level=level,
            name=self.name,
            extra=extra if extra is not None else {},
            created_at=datetime.now(),
            process=os.getpid(),
            thread=threading.get_ident()
        )

    def debug(self, template: str, extra: dict[str, t.Any] | None = None) -> None:
        if self.at_level(LogLevel.DEBUG):
            self.log(
                self._create_record(
                    template=template,
                    level=LogLevel.DEBUG,
                    extra=extra
                )
            )

    def info(self, template: str, extra: dict[str, t.Any] | None = None) -> None:
        if self.at_level(LogLevel.INFO):
            self.log(
                self._create_record(
                    template=template,
                    level=LogLevel.INFO,
                    extra=extra
                )
            )

    def warning(self, template: str, extra: dict[str, t.Any] | None = None) -> None:
        if self.at_level(LogLevel.WARNING):
            self.log(
                self._create_record(
                    template=template,
                    level=LogLevel.WARNING,
                    extra=extra
                )
            )

    def error(self, template: str, extra: dict[str, t.Any] | None = None) -> None:
        if self.at_level(LogLevel.ERROR):
            self.log(
                self._create_record(
                    template=template,
                    level=LogLevel.ERROR,
                    extra=extra
                )
            )

    def critical(self, template: str, extra: dict[str, t.Any] | None = None) -> None:
        if self.at_level(LogLevel.CRITICAL):
            self.log(
                self._create_record(
                    template=template,
                    level=LogLevel.CRITICAL,
                    extra=extra
                )
            )


class _LoggerManager:

    _loggers: dict[str, Logger]
    _children: dict[Logger, t.Set[Logger]]

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.initialize()

    def register_logger(self, logger: Logger) -> None:
        path = logger.name.split(".")
        parent = self._root
        with self._lock:
            if current := self._loggers.pop(logger.name, None):
                # we already have a logger under this name
                # se we can replace it and copy over it's children w/o
                # traversing the log heirachy
                logger.parent = current.parent
                for child in self._children.pop(current):
                    child.parent = logger
            else:
                # make sure there are loggers from the root logger to this logger
                for subpath in itertools.accumulate(path[:-1], lambda path, leaf: f"{path}.{leaf}"):
                    if subpath not in self._loggers:
                        self._loggers[subpath] = Logger(subpath)
                        self._loggers[subpath].parent = parent
                        self._children[self._loggers[subpath]] = set()
                    parent = self._loggers[subpath]
                # set the last logger we saw in the heirachy as this logger's parent
                logger.parent = parent
                # initialize this loggers children to an empty set
                self._children[logger] = set()
                # register the logger
                self._loggers[logger.name] = logger
    
    def remove_logger(self, name: str) -> None:
        if name == "":
            self.initialize()
            return
        with self._lock:
            to_remove: list[str] = [name]
            while to_remove:
                current = self._loggers.pop(to_remove.pop())
                children = self._children.pop(current)
                for child in children:
                    to_remove.append(child.name)

    def initialize(self) -> None:
        with self._lock:
            self._root = Logger(name="", level=FiltererLevel.INFO)
            self._root.add_handler(StreamHandler())
            self._loggers = {"": self._root}
            self._children = {self._root: set()}

    def get_logger(self, name: str) -> Logger:
        with self._lock:
            if current := self._loggers.get(name, None):
                return current
        logger = Logger(name)
        self.register_logger(logger)
        return logger


_log_manager = _LoggerManager()


def reset() -> None:
    _log_manager.initialize()


def get_logger(name: str) -> Logger:
    return _log_manager.get_logger(name)


def register_logger(logger: Logger) -> None:
    return _log_manager.register_logger(logger)


def remove_logger(name: str) -> None:
    return _log_manager.remove_logger(name)
