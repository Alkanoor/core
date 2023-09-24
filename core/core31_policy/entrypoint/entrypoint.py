from .initialization import init_policy

import regex
import os


def parse_environment(env_regex):
    result = {}
    for name, value in os.environ.items():
        if regex.match(env_regex, name):
            result[name] = value
    return result


@init_policy
def entrypoint():
    # parse args until first positional argument
    base_options = parse_args()
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

