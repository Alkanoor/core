from core.core30_context.context_dependency_graph import context_producer, context_dependencies
from core.core30_context.context import Context

from typing import Callable


def default_ask_cli(*args, **argv):
    print(args, argv)
    print("aaaaa")

@context_producer(('.interactor.ask', Callable[[...], str]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))  # dynamically generated
def ask_to_interactor(ctxt: Context):
    print(ctxt)
    print(ctxt['interactor']['local'])
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor']['ask'] = default_ask_cli
    else:
        raise NotImplementedError
