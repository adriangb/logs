import re

from examples.bind import main as bind_main
from examples.filters import main as filters_main
from examples.formatting import main as formatting_main
from examples.testing import main as testing_main
from logs.testing import capture_logs


def test_bind_example():
    with capture_logs() as logs:
        bind_main()

    assert logs.output == ["{}", "{'key': 'value'}", "{}"], logs.output


def test_filters_example():
    with capture_logs() as logs:
        filters_main()

    expected = ["1234", "Not today junior!"]

    assert logs.output == expected, logs.output


def test_formatting_example():
    with capture_logs() as logs:
        formatting_main()

    assert re.match(r"Formatting example INFO - [\d-]+ [\d:.]+ - 123", logs.output[0]) is not None


def test_testing_example():
    testing_main()
