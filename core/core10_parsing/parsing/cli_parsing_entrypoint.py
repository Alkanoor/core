from ..cli.registry import register_simple_parsing
from ...core11_config.config import enrich_config

from argparse import Namespace


arguments = [
    (['--config', '-c'],
     # the following statement must be backed by the right policy in case no config option is provided
            {'help': 'Yaml configuration file for global options, default to one of ~/.mgr/config.yml, '
             '/etc/mgr/config.yml, or %%APPDATA%%/mgr/config.yml (depending on OS and privileges)'}),
     # 'default': default_config_path(ctxt)}),
    (['--subconfig', '-sc'], {'help': 'Sub-configuration block to use from config file (default to default)',
                              'default': 'default'}),
    (['--loglevel', '-l'], {'help': 'Global logger value (default to info)',
                            'choices': ['error', 'warning', 'info', 'debug']}),
    (['--database', '-d'], {'help': 'Specify the database holding all the application state (including contexts)'}),
    (['--envregex', '-e'], {'help': 'Specify the environment regex to get environment variables into config (default is'
                                    ' ^\\.?config(\\..*)$ )',
                            'default': '^\\.?config(\\..*)$'}),
    (['--set'], {'help': 'Additional configuration options',
                 'metavar': 'KEY=VALUE',
                 'action': 'append'}),
]

different_matching = {
    'subconfig': 'sub_config',
    'loglevel': 'log_level',
    'envregex': 'env_regex',
    'set': 'additional_options'
}

# @config_producer('.config_file',
#                  '.sub_config',
#                  '.log_level',
#                  '.database',
#                  '.env_regex',
#                  '.additional_options')
def deal_with_parsed_data(parsed_data: Namespace):
    enrich_config({
        f".{k}": different_matching.get(k, v) for k, v in parsed_data.__dict__.items()
    })

# initial CLI entrypoint allowing to switch config
# (initial because if not starting with mgr, the default config is used)
register_simple_parsing('mgr', arguments=arguments, callback_after_parsing=deal_with_parsed_data)
