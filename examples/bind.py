from logs import get_logger
from logs.bind import bind


def main():
    logger = get_logger(__name__)

    logger.info("{extra}")  # prints "{}"
    with bind(key="value"):
        logger.info("{extra}")  # prints "{"key": "value"}"


    logger2 = get_logger("other")
    with bind(logger2, key="value"):
        logger.info("{extra}")  # prints "{}"


if __name__ == "__main__":
    main()
