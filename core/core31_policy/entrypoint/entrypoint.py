from ...core30_context.context_dependency_graph import context_dynamic_producer
from ...core10_parsing.cli.registry import command_registry
from ...core10_parsing.cli.simple_parse import simple_parse
from ...core30_context.context import current_ctxt, Context

import regex
import sys
import os


def parse_environment(env_regex):
    result = {}
    for name, value in os.environ.items():
        if regex.match(env_regex, name):
            result[name] = value
    return result


@context_dynamic_producer(('.interactor.local', bool), ('.interactor.type', str))
def entrypoint(ctxt: Context):
    ctxt.setdefault('interactor', {}).update({
        'local': True,
        'type': 'cli'
    })

    # parse args until first positional argument
    parsed_dict = simple_parse(sys.argv[1:])
    print(parsed_dict)

    if 'mgr' in parsed_dict:  # global configuration in this case, the
        command_registry['mgr']['callback'](parsed_dict['mgr'])

    print(current_ctxt())

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

