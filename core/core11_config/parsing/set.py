from argparse import Namespace
from typing import List


def check_and_parse_set_options(values: List[str]):
    return list(map(check_and_parse_set_option, values))


def check_and_parse_set_option(value: str):
    if '=' not in value:
        raise Exception(f"Expecting = to get key, value for config option, but found {value}")
    s = value.split('=')
    return s[0], '='.join(s[1:])


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


def config_set(parsed: Namespace):
    pass

#write_current_config('C:\\Users\\Alka\\AppData\\Roaming\\mgr\\config.ini')
#write_current_config('C:\\Users\\Alka\\AppData\\Roaming\\mgr\\config3.yaml')