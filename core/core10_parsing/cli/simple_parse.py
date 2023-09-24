from ...core30_context.context_dependency_graph import context_producer
from ...core30_context.context import Context
from .registry import command_registry

from typing import List, Dict, Any
from argparse import Namespace


# at the moment we only do linear parsing not stopping at positional arguments
# so there must be no duplicate optional arguments
# TODO: more elaborate parsing based on grammar, allowing complex interactions
def default_recursive_parse(arguments_list: List[str], accumulated: Dict[str, Any]):
    command = arguments_list[0]
    parser = command_registry[command]['parser']
    parsed, remaining = parser.parse_known_args(arguments_list)
    if command in accumulated:
        raise Exception(f"Unauthorized double command with the same name in current simple parsing")
    accumulated[command] = parsed
    if remaining:
        return default_recursive_parse(remaining, accumulated)
    return accumulated


@context_producer(('.cli.parsed', Dict[str, Namespace]))
def simple_parse(ctxt: Context, arguments_list: List[str]):
    after_parsing = default_recursive_parse(arguments_list, {})
    ctxt.setdefault('cli', {}).update({'parsed': after_parsing})
    return after_parsing
