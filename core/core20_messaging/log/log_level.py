from ...core11_config.config import register_config_default

import logging


register_config_default('.log.log_level', int, logging.INFO)
