from ...core10_parsing.cli.registry import register_simple_parsing, help_back_to_user
from .help import config_help

from argparse import Namespace


arguments_show = [
    (['--subconfig', '-sc'], {'help': 'Sub-configuration block to show (default to None = all configs displayed)',
                              'default': 'default'}),
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
    (['--modules', '-ms'], {'help': 'List all available modules in which some config options can be set',
                            'action': 'store_true'}),
    (['--module', '-m'], {'help': 'Set the module to perform list operations on'}),
    (['--subtrees', '-sts'], {'help': 'List all available subtrees for module in which some config options can be set',
                             'action': 'store_true'}),
    (['--prefix', '-p'], {'help': 'Set the subtree to perform list operations on (this requires a module provided)'}),
    (['--out', '-o'], {'help': 'Output the configuration options within the given file'}),
    (['--outformat', '-of'], {'help': 'Set the (optional) output format in case an output file is given',
                              'choices': ['text', 'json', 'yaml', 'ini', 'html']}),
]

arguments_use = [
    (['subconfig'], {'help': 'Sub-configuration block to use (set as default)'}),
]

arguments_save_db = [
    (['--name', '-n'], {'help': 'Configuration name to save config as in database'}),
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
    'savedb': {
        'description': 'Save the current configuration to provided database',
        'arguments': arguments_save_db,
    }
    # TODO: implement encrypted config, with encryption/decryption functions, policies to decrypt
}


def deal_with_parsed_data(parsed_data: Namespace):
    print(parsed_data)
    help_back = False
    if parsed_data.command == 'set':
        print("SET")
    elif parsed_data.command == 'use':
        print("USE")
    elif parsed_data.command == 'help':
        if not parsed_data.modules and not parsed_data.subtrees and not parsed_data.prefix:
            help_back = True
        else:
            config_help(parsed_data)
    if help_back:
        help_back_to_user('config', parsed_data.command)


register_simple_parsing('config', subparsers=subparsers, callback_after_parsing=deal_with_parsed_data)
