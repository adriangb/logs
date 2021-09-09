# Python Standard Library Logging Wishlist

Part wishlist, part afternoon project: what I **think** I would want Python's `logging` standard library to look like if _I_ wrote it from scratch today.

This package is probably:

- Buggy: especially around concurrency stuff, I didn't test that part at all
- Opinionated: just because it's what I want or came up with today doesn't meant it's a good idea
- Slow: I didn't benchmark anything
- Undocumented: I'm don't plan on rewriting the stdlib docs, the differences are documented below

So needless to say, this is not meant to be used by _anyone_.

## Changes

So what are the changes?

- Don't unpack `extra` into `LogRecord.__dict__`.
- Only one way to format strings: the `string.format()` format.
- By default, the root logger is configured to log to `sys.stderr`.
- Filters don't modify LogRecord in place (which propagates to other handlers/loggers). Instead, they either return a LogRecord (the same one or a different modified one) or None (which breaks the filter chain).
- Filters are (and can only be) a callable (including a class w/ `__call__`)
- Testing tools, primarily to capture logs. Similar to `unittest.assertLogs` and Pytest's `caplog` fixture
- Utilities to bind values to loggers
- No backwards compatibility stuff
- Type hints

## Example

You can run the following example by cloning the repo or pip installing from git.
I do not plan to publish this on PyPi.

```python
from logs import get_logger, LogRecord

logger = get_logger(__name__)


# Prints "Use string formatting: See!" to stderr
logger.info("Use string formatting: {data[thing][nested]}", data=dict(thing=dict(nested="See!")))

# create a filter that only allows records that have data w/ a key "thing"
def only_allow_with_thing(record: LogRecord) -> LogRecord | None:
    if "thing" in record.data:
        return record

logger.add_filter(only_allow_with_thing)
# prints "1234"
logger.info("{data[thing]}", data=dict(thing="1234"))
# does not print anything
logger.info("{data[thing]}", data=dict(otherthing="1234"))
logger.remove_filter(only_allow_with_thing)

# or a filter that completely replaces the record
def replace(record: LogRecord) -> LogRecord | None:
    new_record = record.copy()  # LogRecord implements .copy()
    new_record.template = "Not today junior!"
    return new_record

logger.add_filter(replace)
# prints "Not today junior!"
logger.info("{data[thing]}", data=dict(thing="1234"))
logger.remove_filter(replace)
```
