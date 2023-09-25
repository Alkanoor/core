from core.core30_context.context_dependency_graph import context_dependencies
from core.core30_context.context import Context

from os import path


# @register_policy('.config.default_config_paths')
@context_dependencies(('.executor.os', str), ('.executor.uid', int), ('.executor.gid', int))
def default_config_paths(ctxt: Context):
    if 'win' in ctxt['executor']['os']:
        return [path.expandvars('%APPDATA%\\mgr\\config.yml')]
    else:
        if ctxt['executor']['uid'] == 0 or ctxt['executor']['gid'] == 0:  # quick & dirty way to know we are root
            return ['/etc/mgr/config.yml', path.expanduser('~/.mgr/config.yml')]
        else:  # if not root check if a config is available in current user home
            return [path.expanduser('~/.mgr/config.yml'), '/etc/mgr/config.yml']


# @register_policy('.config.default_database_paths')
@context_dependencies(('.executor.os', str), ('.executor.uid', int), ('.executor.gid', int))
def default_database_paths(ctxt: Context):
    if 'win' in ctxt['executor']['os']:
        return [path.expandvars('%APPDATA%\\mgr\\state.db')]
    else:
        if ctxt['executor']['uid'] == 0 or ctxt['executor']['gid'] == 0:
            return ['/var/mgr/state.db', path.expanduser('~/.mgr/state.db')]
        else:
            return [path.expanduser('~/.mgr/state.db')]
