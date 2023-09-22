from ..entrypoint.initialization import init_policy

from typing import Dict, Any
from enum import Enum
import traceback


class ExceptionLevel(Enum):
    IGNORE = 1  # don't produce anything else than a debug message
    LAX = 2     # at least produce some warning but keep going
    STRICT = 3  # raise the exception no matter what

@init_policy
def init(ctxt: Dict[str, Any]):
    return register_config(ctxt, '.exeception.level', ExceptionLevel)


#@config_dependancies('.exeception.level')
#@context_dependancies('.log.logger', '.log.debug_logger', '.exception.format')
def raise_exception(ctxt: Dict[str, Any], msg: str):
    if ctxt['config']['exception']['level'].lower() == ExceptionLevel.STRICT.name.lower():
        raise Exception(msg)
    else:
        ctxt['policy']['log']['logger'].warning(msg)
        ctxt['policy']['log']['debug_logger'].debug(
            ctxt['policy']['exception']['format'](traceback.extract_stack(), msg)
        )
