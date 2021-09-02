# Python Standard Library Logging Wishlist

Part wishlist, part afternoon project: what I **think** I would want Python's `logging` standard library to look like if _I_ wrote it from scratch today.

This package is probably:

- Buggy: especially around concurrency stuff, I didn't test that part at all
- Opinionated: just because it's what I want or came up with today doesn't meant it's a good idea
- Slow: I didn't benchmark anything

So needless to say, this is not meant to be used by _anyone_.

## Changes

So what are the changes? Well, off of the top of my head:

- No backwards compatibility stuff
- Renamed the `extra` keyword to `data` and made it a first class citizen of `LogRecord`, which makes it much easier to use than trying figure out key collisions with the existing `LogRecord` attributes.
- Only one way to format strings: the `string.format()` format.
- By default, the root logger is configured to log to `sys.stderr`.
- Type hints, no `*args, **kwargs` anywhere.
