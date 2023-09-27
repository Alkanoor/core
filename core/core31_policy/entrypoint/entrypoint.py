from ..misc.dict_operations import update_dict_check_already_there
from ...core10_parsing.parsing.string_transform import cli_string_transforms
from ...core11_config.config import update_fixed
from ...core11_config.policy.default_env import default_config_env
from ...core11_config.policy.read_config import try_open_and_parse_config
from ...core11_config.policy.write_config import write_config
from ...core30_context.context_dependency_graph import context_dynamic_producer
from ...core10_parsing.cli.registry import command_registry
from ...core10_parsing.cli.simple_parse import simple_parse
from ...core30_context.context import Context, current_ctxt

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


def check_log_level_in_dict(config_dict, current_log_level):
    if '.log_level' in config_dict:
        if current_log_level != -1 and current_log_level != config_dict['.log_level']:
            update_fixed('.log.log_level')
        return config_dict['.log_level']
    return -1


@context_dynamic_producer(('.interactor.local', bool), ('.interactor.type', str))
def cli_entrypoint(ctxt: Context):
    ctxt.setdefault('interactor', {}).update({
        'local': True,
        'type': 'cli'
    })

    # this is going to determine the final log level (as it can change depending on each parsing step
    # and on dict merge policy)
    log_value = -1
    config_dict = {}

    # parse CLI args
    parsed_cli_dict = simple_parse(sys.argv[1:])
    if 'mgr' in parsed_cli_dict:  # global configuration in this case,
        config_dict.update(command_registry['mgr']['callback'](parsed_cli_dict['mgr']))

    log_value = check_log_level_in_dict(config_dict, log_value)


    # parse main environment arguments (only config and database, next C2 but if no database is provided atm it's over)
    key_envkeys, env_associations = default_config_env()
    parsed_env_main = {
        env_associations[k]: cli_string_transforms.get(env_associations[k], lambda x: x)(os.environ[k])
        for k in key_envkeys if k in os.environ
    }
    parsed_env_main.update({
        env_associations[k]: cli_string_transforms.get(env_associations[k], lambda x: x)(os.environ[k.upper()])
        for k in key_envkeys if k.upper() in os.environ
    })
    print(parsed_env_main)

    common_keys = update_dict_check_already_there(config_dict, parsed_env_main)
    print(config_dict)
    print(common_keys)
    log_value = check_log_level_in_dict(config_dict, log_value)

    parsed_config_file = try_open_and_parse_config(config_dict)
    print(parsed_config_file)
    print("parsed")

    current_ctxt().setdefault('config', {}).update(parsed_config_file)

    write_config(parsed_config_file, 'C:\\Users\\Alka\\AppData\\Roaming\\mgr\\config.ini')

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
