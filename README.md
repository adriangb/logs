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

- Renamed the `extra` keyword to `data` and made it a first class citizen of `LogRecord`, which makes it much easier to use than trying figure out key collisions with the existing `LogRecord` attributes.
- Only one way to format strings: the `string.format()` format.
- By default, the root logger is configured to log to `sys.stderr`.
- Filters don't modify LogRecord in place (which propagates to other handlers/loggers). Instead, they either return a LogRecord (the same one or a different modified one) or None (which breaks the filter chain).
- Filters are (and can only be) a callable (including a class w/ `__call__`)
- Testing tools, primarily to capture logs. Similar to `unittest.assertLogs` and Pytest's `caplog` fixture.
- No backwards compatibility stuff
- Type hints, no `*args, **kwargs` anywhere.

## Example

```python
from logs import get_logger

logger = get_logger(__name__)

class Something:
    prop: str = "See!"

# Prints "Use string formatting: See!" to stderr
logger.info("Use string formatting: {data[thing].prop}", data=dict(thing=Something()))
```
