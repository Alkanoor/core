

#@register_policy('.config.default_config_env')
def default_config_env():
    return {
        'mgr.config',
        'mgr_config',
        'mgrconfig',
        '.config',
        '.config.config_file',
        'mgr.database',
        'mgr_database',
        'mgr.config.database',
        'config.database',
        '.config.database'
    }, {
        'mgr.config': '.config',
        'mgr_config': '.config',
        'mgrconfig': '.config',
        '.config': '.config',
        '.config.config_file': '.config',
        'mgr.database': '.database',
        'mgr_database': '.database',
        'mgr.config.database': '.database',
        'config.database': '.database',
        '.config.database': '.database',
    }
