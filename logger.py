
import logging

__logger_table = {}


def get_logger(name):
    if name in __logger_table:
        return __logger_table[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    __logger_table[name] = logger
    return logger
