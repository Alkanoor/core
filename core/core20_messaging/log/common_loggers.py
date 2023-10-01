from core.core30_context.context_dependency_graph import context_producer
from core.core11_config.config import config_dependencies, Config
from core.core20_messaging.log.log_level import LogLevel
from core.core20_messaging.log.logger import get_logger
from core.core30_context.context import Context

from logging import Logger, DEBUG, INFO


@context_producer(('.log.debug_logger', Logger | None))
@config_dependencies(('.log.log_level', LogLevel))
def debug_logger(config: Config, ctxt: Context):
    if config['log']['log_level'] == LogLevel.DEBUG:
        ctxt.setdefault('log', {})['debug_logger'] = get_logger('context.log.debug_logger')
        ctxt['log']['debug_logger'].setLevel(DEBUG)
    else:
        ctxt.setdefault('log', {})['debug_logger'] = None


@context_producer(('.log.main_logger', Logger))
@config_dependencies(('.log.log_level', LogLevel))
def main_logger(config: Config, ctxt: Context):
    ctxt.setdefault('log', {})['main_logger'] = get_logger('context.log.main_logger')
    ctxt['log']['main_logger'].setLevel(config['log']['log_level'].value)


@context_producer(('.log.cli_interactor_logger', Logger))
def cli_interactor_logger(ctxt: Context):
    ctxt.setdefault('log', {})['cli_interactor_logger'] = get_logger('context.log.cli_interactor_logger')
    ctxt['log']['cli_interactor_logger'].setLevel(INFO)
