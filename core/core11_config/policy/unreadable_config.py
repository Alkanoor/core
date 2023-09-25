from core.core11_config.config import Config, register_config_default, config_dependencies
from core.core30_context.context_dependency_graph import context_dependencies
from core.core31_policy.exception.strictness import raise_exception
from core.core30_context.context import Context

from typing import List, Callable
from enum import Enum


class UnreadableConfigPolicy(Enum):
    GO_NEXT_RAISE_AT_END = 1
    VERBOSE_GO_NEXT_RAISE_AT_END = 2
    VERBOSE_GO_NEXT_ASK_AT_END = 3
    STOP_FIRST_FAILURE = 4  # this is just exception raising
    ASK = 5


register_config_default('.config.missing_config', UnreadableConfigPolicy,
                        UnreadableConfigPolicy.VERBOSE_GO_NEXT_ASK_AT_END)


def exit_or_specify_conf(ctxt: Context):
    exit_or_ask = ctxt['interactor']['ask_boolean']('No possible configuration file remains, '
                                                    'exit (y) or provide other one (n)?')
    if exit_or_ask:
        exit(0)
    return ctxt['interactor']['ask']('Please specify a valid location for an existing config file')


# @register_policy('.config.unreadable_config')
@config_dependencies(('.config.unreadable_config', UnreadableConfigPolicy))
@context_dependencies(('.interactor.ask_boolean', Callable[[...], bool]), ('.interactor.ask', Callable[[...], str]))
def unreadable_config_policy(ctxt: Context, config: Config, remaining_files_to_test: bool, raised_exception: Exception):
    if config['unreadable_config'] == UnreadableConfigPolicy.STOP_FIRST_FAILURE:
        raise Exception(raised_exception)
    elif config['unreadable_config'] == UnreadableConfigPolicy.GO_NEXT_RAISE_AT_END or \
            config['unreadable_config'] == UnreadableConfigPolicy.VERBOSE_GO_NEXT_RAISE_AT_END or \
            config['unreadable_config'] == UnreadableConfigPolicy.VERBOSE_GO_NEXT_ASK_AT_END:
        if not remaining_files_to_test:
            if config['unreadable_config'] == UnreadableConfigPolicy.VERBOSE_GO_NEXT_ASK_AT_END:
                return exit_or_specify_conf(ctxt)
            else:
                raise Exception(raised_exception)
    elif config['unreadable_config'] == UnreadableConfigPolicy.ASK:
        if remaining_files_to_test:
            exit_or_ask = ctxt['interactor']['ask_boolean']('Check next configuration? Continue (y) Exit (n)')
            if not exit_or_ask:
                exit(0)
        else:
            return exit_or_specify_conf(ctxt)
    else:
        raise NotImplementedError
