import logging


def get_logger(name):
    logger = logging.getLogger(name)

    handler = logging.StreamHandler()
    handler.setLevel(logger.level)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    handler.setFormatter(formatter)

    for hdlr in logger.handlers[:]:
        logger.removeHandler(hdlr)
        logger.handlers.clear()
        logger.propagate = False
    logger.addHandler(handler)

    return logger
