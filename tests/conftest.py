import pytest

import logs


@pytest.fixture(autouse=True)
def reset_logging() -> None:
    logs.reset()
