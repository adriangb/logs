# All credit to https://stackoverflow.com/a/22434262/6582418
import os
from contextlib import contextmanager
from typing import Generator, TextIO


@contextmanager
def redirect_stream(source: TextIO, target: TextIO) -> Generator[None, None, None]:
    source_fd = source.fileno()
    # copy source_fd before it is overwritten
    with os.fdopen(os.dup(source_fd), 'w') as copied: 
        source.flush()  # flush library buffers that dup2 knows nothing about
        os.dup2(target.fileno(), source.fileno())
        try:
            yield
        finally:
            # restore source to its previous value
            #NOTE: dup2 makes source_fd inheritable unconditionally
            target.flush()
            os.dup2(copied.fileno(), source_fd)
