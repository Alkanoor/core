

#@register_policy('.config.default_config_env')
def default_config_env():
    return {
        'mgr.config',
        'mgr_config',
        'mgrconfig',
        'config',
        '.config.config_file',
        'mgr.database',
        'mgr_database',
        'mgr.config.database',
        'config.database',
        '.config.database',
        'mgr.loglevel',
        'mgr.log_level',
        'mgr_loglevel',
        'loglevel',
        'log_level',
        '.mgr.loglevel',
        '.mgr.log_level',
    }, {
        'mgr.config': '.config',
        'mgr_config': '.config',
        'mgrconfig': '.config',
        'config': '.config',
        '.config.config_file': '.config',
        'mgr.database': '.database',
        'mgr_database': '.database',
        'mgr.config.database': '.database',
        'config.database': '.database',
        '.config.database': '.database',
        'mgr.loglevel': '.log.log_level',
        'mgr.log_level': '.log.log_level',
        'mgr_loglevel': '.log.log_level',
        'loglevel': '.log.log_level',
        'log_level': '.log.log_level',
        '.mgr.loglevel': '.log.log_level',
        '.mgr.log_level': '.log.log_level',
    }
