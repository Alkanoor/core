from ...core11_config.config import config_dependencies, Config

import logging


@config_dependencies(('.log.log_level', int))
def get_logger(config: Config, name: str):
    logger = logging.getLogger(name)

    handler = logging.StreamHandler()
    handler.setLevel(config['log']['log_level'])
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    handler.setFormatter(formatter)

    for hdlr in logger.handlers[:]:
        logger.removeHandler(hdlr)
        logger.handlers.clear()
        logger.propagate = False

    logger.addHandler(handler)

    return logger
