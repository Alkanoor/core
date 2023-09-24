from .context_dependency_graph import context_producer
from core.core20_messaging.log.logger import get_logger
from .context import Context

from logging import Logger
import platform
import os


@context_producer(('.executor.os', str), ('.executor.arch', str), ('.executor.platform', str), ('.executor.uid', int), ('.executor.gid', int))
def init_executor_context(ctxt: Context):
    uid, gid = -1, -1
    if 'win' not in platform.system().lower():
        uid, gid = os.getuid(), os.getgid()
    ctxt.setdefault('executor', {}) \
         .update({'os': platform.system(),
                  'arch': platform.machine(),
                  'platform': platform.platform(),
                  'uid': uid,
                  'gid': gid
            })


@context_producer(('.log.initial_logger', Logger))  # default log context when no config has yet be parsed
def init_log_context(ctxt: Context):
    default_logger = get_logger('context.log.initial_logger')
    ctxt.setdefault('log', {}).update({'initial_logger': default_logger})
