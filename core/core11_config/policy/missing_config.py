from ...core31_policy.exception.strictness import raise_exception_from_string
from ...core30_context.context_dependency_graph import context_dependencies
from ..config import Config, register_config_default, config_dependencies
from ...core30_context.context import Context

from typing import List, Callable
from enum import Enum


class MissingConfigPolicy(Enum):
    RAISE = 1
    ASK = 2
    ASK_GROUP = 3

register_config_default('.config.missing_config', MissingConfigPolicy, MissingConfigPolicy.ASK)


#@register_policy('.config.missing_config')
@config_dependencies(('.config.missing_config', MissingConfigPolicy))
@context_dependencies(('.interactor.ask', Callable[[...], str]))
def missing_config_policy(ctxt: Context, config: Config, missing_configs: List[str], func_name: str):
    if config['config']['missing_config'] == MissingConfigPolicy.RAISE:
        raise Exception(f"Missing configuration for function {func_name}: {', '.join(missing_configs)}")
    elif config['config']['missing_config'] == MissingConfigPolicy.ASK:
        filled = {}
        for missing_config in missing_configs:
            filled[missing_config] = \
                ctxt['interactor']['ask'](f"Configuration for item at {missing_config}? (for {func_name})", str)
        return filled
    elif config['config']['missing_config'] == MissingConfigPolicy.ASK_GROUP:
        filled = ctxt['interactor']['ask'](f"Configuration for missing items at {func_name}?", dict, missing_configs)
        return filled
    else:
        raise_exception_from_string(f"Non allowed value {config['config']['missing_config']} provided for {MissingConfigPolicy}")
        return {}
