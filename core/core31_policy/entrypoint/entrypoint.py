

def entrypoint():
    # parse args until first positional argument
    base_options = parse_begin()
    # parse config
    if base_options.config:
        config_file = base_options.config
    else:
        config_file =
    # parse env
    # parse BDD
    # parse C2, ...