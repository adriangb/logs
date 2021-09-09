from logs import get_logger


def main():
    logger = get_logger(__name__)

    logger.info("Formatting example {level} - {created_at} - {extra[key]}", extra=dict(key=123))


if __name__ == "__main__":
    main()
