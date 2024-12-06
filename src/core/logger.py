import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s", style="%")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
