from core.core10_parsing.cli.registry import command_registry
from core.core30_context.context_dependency_graph import context_producer, context_dependencies
from core.core10_parsing.cli.simple_parse import simple_parse
from core.core30_context.context import Context

from typing import Callable
import shlex
import cmd

from core.core31_policy.exception.strictness import raise_exception


class BasicArgparseREPL(cmd.Cmd):
    prompt = '/> '

    def onecmd(self, command: str):
        print(command)
        import os
        print(os.environ['log_level'])
        print(shlex.split(command))
        try:
            ns_per_command = simple_parse(shlex.split(command))
            for key in ns_per_command:
                command_registry[key]['callback'](ns_per_command[key])
        except Exception as e:
            raise_exception(e)


def cli_repl_loop():
    try:
        BasicArgparseREPL().cmdloop()
    except KeyboardInterrupt:
        exit(0)


@context_producer(('.interactor.parsing_no_action', Callable[[], None]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))  # dynamically generated
def no_action_parsed(ctxt: Context):
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor']['parsing_no_action'] = cli_repl_loop
        return cli_repl_loop
    else:
        raise NotImplementedError
