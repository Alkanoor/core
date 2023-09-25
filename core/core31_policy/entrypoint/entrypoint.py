from ..misc.dict_operations import update_dict_check_already_there
from ...core11_config.policy.default_env import default_config_env
from ...core30_context.context_dependency_graph import context_dynamic_producer
from ...core11_config.policy.default_path import default_config_paths
from ...core10_parsing.cli.registry import command_registry
from ...core10_parsing.cli.simple_parse import simple_parse
from ...core30_context.context import current_ctxt, Context

import regex
import yaml
import sys
import os


def parse_environment(env_regex):
    result = {}
    for name, value in os.environ.items():
        if regex.match(env_regex, name):
            result[name] = value
    return result


@context_dynamic_producer(('.interactor.local', bool), ('.interactor.type', str))
def cli_entrypoint(ctxt: Context):
    ctxt.setdefault('interactor', {}).update({
        'local': True,
        'type': 'cli'
    })

    # parse CLI args
    parsed_cli_dict = simple_parse(sys.argv[1:])

    # parse main environment arguments (only config and database, next C2 but if no database is provided atm it's over)
    key_envkeys, env_associations = default_config_env()
    parsed_env_main = {
        env_associations[k]: k for k in key_envkeys if k in os.environ or k.upper() in os.environ
    }
    print(parsed_env_main)

    base_options = {}
    if 'mgr' in parsed_cli_dict:  # global configuration in this case,
        base_options.update(command_registry['mgr']['callback'](parsed_cli_dict['mgr']))

    update_dict_check_already_there(base_options, parsed_env_main)
    print(base_options)

    if '.config' in base_options:
        with open(base_options['.config'], 'r') as f:
            loaded_config = yaml.safe_load(f)
        print(loaded_config)
    else:
        possible_locations = default_config_paths()
        print(possible_locations)

    print(base_options)

    # parse config
    if base_options.config:
        config_file = base_options.config
    else:
        config_file = default_config_file
    # parse env
    from_environment = parse_environment(env_regex)
    # parse BDD
    from_bdd = parse_bdd_config()
    # parse C2, ...
    from_c2 = parse_c2_config()
    if config.save:
        save_config()

    # now all is parsed, current_context['config'] is ready, give it to following layers

