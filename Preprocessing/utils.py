import logging


def setup_logger(class_name: str, level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=level,
    )
    return logging.getLogger(class_name)
