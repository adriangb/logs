from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator, Optional

from logs import Logger, LogRecord, get_logger


_ctx_var: ContextVar[dict] = ContextVar("_ctx_var")


def _get_ctx() -> dict | None:
    try:
        return _ctx_var.get()
    except LookupError:
        return None


@contextmanager
def bind(logger: Optional[Logger] = None, **kwargs) -> Generator[None, None, None]:
    """Temporarily bind **kwargs into the logger's context.

    Every log record emitted will have **kwargs injected into it,
    just like if you have logged with `logger.info(..., extra=kwargs)`.

    Parameters
    ----------
    logger : Logger
        Logger to bind to.
    **kwargs : Dict[str, Any]
        Attributes to bind to all emitted log records.
    """

    logger = logger or get_logger("")

    ctx = _get_ctx()
    if ctx is None:
        ctx = kwargs
    else:
        ctx = ctx.copy()
        ctx.update(kwargs)
    token = _ctx_var.set(ctx)

    def filter(record: LogRecord) -> LogRecord:
        cur_ctx = _get_ctx()
        if cur_ctx:
            record = record.copy()
            record.extra.update(**cur_ctx)
        return record

    logger.add_filter(filter)

    try:
        yield
    finally:
        _ctx_var.reset(token)
        logger.remove_filter(filter)
