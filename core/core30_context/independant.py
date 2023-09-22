from .log.logger import get_logger

import os


@enrich_context('executor', [])  # no dependancy for first executor information retrieval
def init_executor_context():
    return {'os': os.uname(),
            # 'arch': os...
            }

@enrich_context('log', [])  # default log context when no config has yet be parsed
def init_log_context():
    default_logger = get_logger('context.log.default')
    return {'initial_logger': default_logger}
