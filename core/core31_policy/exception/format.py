from ..entrypoint.initialization import init_policy
from traceback import FrameSummary, StackSummary
from typing import List, Dict, Any
from functools import partial
from enum import Enum


class ExceptionFormat(Enum):
    DEFAULT = 1
    MINIMAL = 2
    ONE_LINE = 3
    KEEP_ARRAY = 4

@init_policy
def init(ctxt: Dict[str, Any]):
    return register_config(ctxt, 'exeception_format', ExceptionFormat, ExceptionFormat.DEFAULT)


def default_trace_line_formatting(trace_line: FrameSummary):
    return f"\tFile \"{trace_line.filename}\", line {trace_line.lineno}, in {trace_line.name}\n\t\t{trace_line.line}"

# this is like StackSummary.format (but we do not have a StackSummary available so we fake it)
def default_trace_formatting(trace_lines: StackSummary, message: str):
    return 'Traceback:\n' + '\n'.join(map(default_trace_line_formatting, trace_lines)) + f"\n\tException: {message}"


#@config_dependancies('.exeception.format')
def format_exception(ctxt: Dict[str, Any], trace_lines: StackSummary, message: str):
    if ctxt['config']['exception']['format'].lower() == ExceptionFormat.DEFAULT.name.lower():
        return default_trace_formatting(trace_lines, message)
    else:
        raise NotImplemented

@init_policy
def init(ctxt: Dict[str, Any]):
    return register_policy(ctxt, 'exception.format_exception', partial(format_exception, ctxt=ctxt))
