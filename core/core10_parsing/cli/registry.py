from typing import Callable, Dict, Any, List, Tuple
import argparse


command_registry = {}

def register_simple_parsing(command: str,
                            callback_after_parsing: Callable[[Dict[str, Any], argparse.Namespace, ...], Any],
                            arguments: List[Tuple[List[str], Dict[str, str]]]=None,
                            subparsers: Dict[str, str|List[Tuple[List[str], Dict[str, str]]]]=None,
                            description: str=None):
    assert command not in command_registry, f"Command {command} already in registry, please register another name"
    arg_parser = argparse.ArgumentParser(prog=command, description=description)

    if arguments:
        for positional, optional in arguments:
            arg_parser.add_argument(*positional, **optional)

    if subparsers:
        subparsers_for_parser = arg_parser.add_subparsers()
        for subparser_name in subparsers:
            subparser = subparsers_for_parser.add_parser(subparser_name, description=subparsers[subparser_name]['description'])
            for positional, optional in subparsers[subparser_name]['arguments']:
                subparser.add_argument(*positional, **optional)

    command_registry[command] = {
        'parser': arg_parser,
        'built_from': {'arguments': arguments, 'subparsers': subparsers, 'description': description},
        'callback': callback_after_parsing,
    }


# @init_policy
# @context_dependancies('.persistent.valid_sqlalchemy_session')
# def save_parsing_registry_in_database(ctxt: Dict[str, Any]):
#     session = ctxt_get_or_create(ctxt, '.persistent.valid_sqlalchemy_session')
#     for command_name in command_registry:
#         built_from = command_registry[command_name]
        #PARSING_ARGUMENTS.GET_CREATE(...)
        #PARSING_subparsers.GET_CREATE(...)
    #...