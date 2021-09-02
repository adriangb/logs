import pytest

import logs


@pytest.fixture(autouse=True)
def reset_logs() -> None:
    logs.reset()
