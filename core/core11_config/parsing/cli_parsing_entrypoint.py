from ...core10_parsing.cli.registry import register_simple_parsing

from argparse import Namespace
from typing import Dict, Any


arguments_show = [
    (['--subconfig', '-sc'], {'help': 'Sub-configuration block to show (default to None = all configs displayed)'}),
]

arguments_set = [
    (['--subconfig', '-sc'], {'help': 'Sub-configuration block to set (default to default)'}),
    (['--loglevel', '-l'], {'help': 'Global logger value',
                            'choices': ['error', 'warning', 'info', 'debug']}),
    (['--database', '-d'], {'help': 'Global database holding all the application state (including further contexts)'}),
    (['--set'], {'help': 'Additional configuration options',
                 'action': 'append'}),
    (['--out', '-o'], {'help': 'Output the configuration options within the given file (instead of current one)'}),
    (['--outformat', '-of'], {'help': 'Set the (optional) output format in case an output file is given',
                              'choices': ['yaml', 'ini']}),
]

# this one holds some mutually exclusive argument groups but this is not handled yet
arguments_help = [
    (['--modules', '-ms'], {'help': 'List all available modules in which some config options can be set'}),
    (['--module', '-m'], {'help': 'Set the module to perform list operations on'}),
    (['--subtrees', '-ss'], {'help': 'List all available subtrees for module in which some config options can be set'}),
    (['--subtree', '-s'], {'help': 'Set the subtree to perform list operations on (this requires a module provided)'}),
    (['--out', '-o'], {'help': 'Output the configuration options within the given file'}),
    (['--outformat', '-of'], {'help': 'Set the (optional) output format in case an output file is given',
                              'choices': ['text', 'json', 'yaml', 'ini', 'html']}),
]

arguments_use = [
    (['subconfig'], {'help': 'Sub-configuration block to use (set as default)'}),
]

subparsers = {
    'show': {
        'description': 'Show the target configuration (or all if none is provided)',
        'arguments': arguments_show,
    },
    'set': {
        'description': 'Set the target configuration',
        'arguments': arguments_set,
    },
    'help': {
        'description': 'Show the desired available options',
        'arguments': arguments_help,
    },
    'use': {
        'description': 'Use the target configuration as default',
        'arguments': arguments_use,
    },
    # TODO: implement encrypted config, with encryption/decryption functions, policies to decrypt
}

def deal_with_parsed_data_and_continue_parsing(ctxt: Dict[str, Any], parsed_data: Namespace):
    print(ctxt)
    print(parsed_data)


register_simple_parsing('config', subparsers=subparsers, callback_after_parsing=deal_with_parsed_data_and_continue_parsing)
