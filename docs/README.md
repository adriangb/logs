## Purpose

This library is a personal experiment, created to share thoughts, and is not intended for use by others (aside from experimenting with it).

## Goals

Make something largely API compatible to the standard library's logging module, while fixing some of the more annoying bits and providing added batteries.

## Non-goals

This is not an attempt to re-imagine logging (see [Loguru] for a great production ready example of that).

## Changes vs. the standard library

- Don't unpack `extra` into `LogRecord.__dict__`
- Only one way to format strings: the `string.format()` format
- By default, the root logger is configured to log to `sys.stderr`
- Filters don't modify LogRecord in place (which propagates to other handlers/loggers). Instead, they either return a LogRecord (the same one or a different modified one) or None (which breaks the filter chain)
- Filters are (and can only be) a callable (including a class w/ `__call__`)
- No backwards compatibility stuff
- Type hints

### Formatting

[formatting.py](examples/formatting.py ':include :type=code python')

### Filters

[filters.py](examples/filters.py ':include :type=code python')

## Additional batteries

### Testing

An API-compatible improvement over `unittest.assertLogs` that not only captures logs but also:

- Captures raw records
- Allows you to apply filters & formatters (so you can assert formatted output)
- Is fully typed

Example usage:

[testing.py](examples/testing.py ':include :type=code python')

This tool can be ported to the standard library just by changing the imports.

### Binding of `extra` parameters

A context manager to bind values to `extra`.
It optionally accepts a `Logger` instance as a parameter (to bind to a specific logger), or defaults to the root logger.

This context manager is coroutine and thread safe: only logs emitted from within the context manager (including from a thread, coroutine, background task, etc.) will have the bound values.

Example usage:

[bind.py](examples/bind.py ':include :type=code python')

This tool can be ported to the standard library just by changing the imports.

[Loguru]: https://github.com/Delgan/loguru
