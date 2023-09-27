from typing import Dict, Callable, Any, Tuple, Type
from functools import wraps
from enum import Enum
import json
import copy

Config = Dict[str, Any]

_dependencies_per_function = {}
_functions_dependant_of = {}
_config_value_or_default: Dict[str, Tuple[bool, Type, Any]] = {}


def config_dependencies(*deps: Tuple[str, Type]):
    def sub(f: Callable[[...], Any]):
        key = f"{f.__module__}.{f.__name__}"
        assert key not in _dependencies_per_function, f"Config dependencies for {key} already registered"
        _dependencies_per_function[key] = deps

        for attributes_string, _ in deps:
            _functions_dependant_of.setdefault(attributes_string, set()).add(key)

        @wraps(f)
        def f_with_deps_resolved(*args, **argv):
            context = current_ctxt()
            config = context.setdefault('config', {})
            unknown_configs = []
            default_to_fixed = []
            has_been_deep_copied = False

            for attributes_string, expected_type_from_dep in deps:
                if attributes_string in _config_value_or_default:
                    is_default_value, expected_type, value = _config_value_or_default[attributes_string]
                    assert expected_type == expected_type_from_dep, \
                        f"Expecting type {expected_type_from_dep} from dependency, found {expected_type}"
                    # the other case is when the config already contains the right value, so do nothing
                    if is_default_value:
                        # check if the config contains the desired value, in this case not a default value anymore
                        success, value_from_context = check_dict_against_attributes_string(config, attributes_string)
                        if success:
                            _config_value_or_default[attributes_string] = (False, expected_type, value_from_context)
                            default_to_fixed.append(attributes_string)
                        else:
                            if not has_been_deep_copied:
                                config = copy.deepcopy(config)  # this is in order not to pollute the context
                                # with a default value
                            set_dict_against_attributes_string(config, attributes_string, value)
                else:
                    unknown_configs.append(attributes_string)

            if unknown_configs:
                from core.core11_config.policy.missing_config import missing_config_policy
                filled_values = missing_config_policy(unknown_configs, key)

                for attributes_string, value in filled_values.items():
                    _config_value_or_default[attributes_string] = \
                        (False, _config_value_or_default[attributes_string][1], value)
                    set_dict_against_attributes_string(config, attributes_string, value)
                    if has_been_deep_copied:  # in this case the changes should be reported within the context
                        set_dict_against_attributes_string(context['config'], attributes_string, value)
                    default_to_fixed.append(attributes_string)

            if default_to_fixed:
                update_fixed(*default_to_fixed)

            return f(config, *args, **argv)

        return f_with_deps_resolved

    return sub


def register_config_default(attribute_string, default_value_type, default_value):
    if attribute_string in _config_value_or_default:  # should not happen, but tolerate the case where not a default val
        assert _config_value_or_default[attribute_string][0] is False, \
            f"Not allowing to register twice for the same default value location {attribute_string}"
    _config_value_or_default[attribute_string] = (True, default_value_type, default_value)


# some tweaks there to convert from string to any correct type
def right_type_for(value, str_or_default_type):
    if str_or_default_type == bool:
        return False if isinstance(value, str) and (value.lower() == 'false' or value == '0')\
                        or isinstance(value, int) and value == 0 else True
    if str_or_default_type == list or str_or_default_type == dict:
        return json.loads(value)
    return str_or_default_type(value)


def inverse_type_to_string(value):
    match value:
        case bool():
            return
        case int():
            return str(value)
        case str():
            return value
        case Enum():
            return value.name
        case dict() | list() | set():
            return json.dumps(value)
        case _:
            raise NotImplementedError


def enrich_config(config_to_merge: Dict[str, Any]):
    rightly_typed = {
        k: right_type_for(v, _config_value_or_default.get(k, (str, str))[1]) for k, v in config_to_merge.items()
    }
    context = current_ctxt()
    context.setdefault('config', {})
    for key in rightly_typed:
        set_dict_against_attributes_string(context['config'], key, rightly_typed[key])


def config_to_string(with_default: bool = False):
    output = {}
    for key in _config_value_or_default:
        # only writing it if a specific value has been set or if explicitly asked to dump default
        if with_default or not _config_value_or_default[key][0]:
            set_dict_against_attributes_string(output, key,
                                               inverse_type_to_string(_config_value_or_default[key][2],
                                                                      _config_value_or_default[key][1]))
    return output


def update_fixed(*attributes_strings: str):
    functions_to_update = set()
    for attributes_string in attributes_strings:
        functions_to_update = functions_to_update.union(
            _functions_dependant_of.get(attributes_string, set())
        )
    for function in functions_to_update:
        # in this case it is known that the function as no argument in order to be called during dependency resolve
        func = is_context_producer(function)
        if func:
            func()


from ..core99_misc.fakejq.utils import check_dict_against_attributes_string, set_dict_against_attributes_string
from ..core31_policy.misc.dict_operations import update_dict_check_already_there
from ..core30_context.context_dependency_graph import is_context_producer
from ..core30_context.context import current_ctxt
