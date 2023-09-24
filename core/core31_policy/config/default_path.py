from ...core30_context.context_dependency_graph import context_dependencies
from ...core30_context.context import Context

from os import path


@context_dependencies('.executor.os')
def default_config_paths(ctxt: Context):
    if 'win' in ctxt['executor']['os']:
        return [path.expandvars('%APPDATA%\\mgr\\config.yml')]
    else:
        return ['~/.mgr/config.yml', '/etc/mgr/config.yml']
