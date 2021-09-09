from logs import get_logger, LogRecord


def main():
    logger = get_logger(__name__)

    # create a filter that only allows records that have data w/ a key "thing"
    def only_allow_with_thing(record: LogRecord) -> LogRecord | None:
        if "thing" in record.extra:
            return record

    logger.add_filter(only_allow_with_thing)
    # prints "1234"
    logger.info("{extra[thing]}", extra=dict(thing="1234"))
    # does not print anything
    logger.info("{extra[thing]}", extra=dict(otherthing="1234"))
    logger.remove_filter(only_allow_with_thing)

    # or a filter that completely replaces the record
    def replace(record: LogRecord) -> LogRecord | None:
        new_record = record.copy()  # LogRecord implements .copy()
        new_record.template = "Not today junior!"
        return new_record

    logger.add_filter(replace)
    # prints "Not today junior!"
    logger.info("{extra[thing]}", extra=dict(thing="1234"))
    logger.remove_filter(replace)


if __name__ == "__main__":
    main()
