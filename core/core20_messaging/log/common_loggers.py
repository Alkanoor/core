from core.core30_context.context_dependency_graph import context_producer
from core.core11_config.config import config_dependencies, Config
from core.core20_messaging.log.logger import get_logger
from core.core30_context.context import Context

from logging import Logger, DEBUG


@context_producer(('.log.debug_logger', Logger | None))
@config_dependencies(('.log.log_level', int))
def debug_logger(config: Config, ctxt: Context):
    if config['log']['log_level'] == DEBUG:
        ctxt.setdefault('log', {})['debug_logger'] = get_logger('context.log.debug_logger')
        ctxt['log']['debug_logger'].setLevel(DEBUG)
    else:
        ctxt.setdefault('log', {})['debug_logger'] = None


@context_producer(('.log.main_logger', Logger))
def main_logger(ctxt: Context):
    ctxt.setdefault('log', {})['main_logger'] = get_logger('context.log.main_logger')
