from ..cli.registry import register_simple_parsing

from argparse import Namespace
from typing import Dict, Any


arguments = [
    (['--config', '-c'],
     # the following statement must be backed by the right policy in case no config option is provided
     {'help': 'Yaml configuration file for global options, default to one of ~/.mgr/config.yml, '
              '/etc/mgr/config.yml, or %%APPDATA%%/mgr/config.yml (depending on OS and privs)'}),
     # 'default': default_config_path(ctxt)}),
    (['--subconfig', '-sc'], {'help': 'Sub-configuration block to use from config file (default to default)',
                              'default': 'default'}),
    (['--loglevel', '-l'], {'help': 'Global logger value (default to info)',
                            'choices': ['error', 'warning', 'info', 'debug'],
                            'default': 'info'}),
    (['--database', '-d'], {'help': 'Specify the database holding all the application state (including contexts)'}),
    (['--envregex', '-e'], {'help': 'Specify the environment regex to get environment variables into config (default is'
                                    ' \\.?config\\.*)',
                            'default': '\\.?config\\.*'}),
    (['--set'], {'help': 'Additional configuration options',
                 'metavar': 'KEY=VALUE',
                 'action': 'append'}),
]

def deal_with_parsed_data_and_continue_parsing(ctxt: Dict[str, Any], parsed_data: Namespace):
    print(ctxt)
    print(parsed_data)

# initial CLI entrypoint allowing to switch config
# (initial because if not starting with mgr, the default config is used)
register_simple_parsing('mgr', arguments=arguments, callback_after_parsing=deal_with_parsed_data_and_continue_parsing)
