import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s", style="%")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
