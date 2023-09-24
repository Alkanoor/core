from ..core99_misc.fakejq.utils import check_dict_against_attributes_string, set_dict_against_attributes_string
from ..core31_policy.misc.dict_operations import update_dict_check_already_there
from ..core31_policy.config.missing_config import missing_config_policy
from ..core30_context.context import current_ctxt

from typing import Dict, List, Callable, Any, Tuple, Type
from functools import wraps
import copy


Config = Dict[str, Any]


_dependencies_per_function = {}
_config_value_or_default: Dict[str, Tuple[bool, Type, Any]] = {}

def config_dependencies(*deps: List[Tuple[str, Type]]):
    def sub(f: Callable[[...], Any]):
        key = f"{f.__module__}.{f.__name__}"
        assert key not in _dependencies_per_function[key], f"Config dependencies for {key} already registered"
        _dependencies_per_function[key] = deps

        @wraps(f)
        def f_with_deps_resolved(*args, **argv):
            context = current_ctxt()
            config = context['config']
            unknown_configs = []
            has_been_deep_copied = False

            for attributes_string, expected_type_from_dep in deps:
                if attributes_string in _config_value_or_default:
                    is_default_value, expected_type, value = _config_value_or_default[attributes_string]
                    assert expected_type == expected_type_from_dep,\
                        f"Expecting type {expected_type_from_dep} from dependency, found {expected_type}"
                    # the other case is when the config already contains the right value, so do nothing
                    if is_default_value:
                        # check if the config contains the desired value, in this case not a default value anymore
                        success, value_from_context = check_dict_against_attributes_string(config, attributes_string)
                        if success:
                            set_dict_against_attributes_string(_config_value_or_default, attributes_string,
                                                               (False, value_from_context))
                        else:
                            if not has_been_deep_copied:
                                config = copy.deepcopy(config)  # this is in order not to pollute the context
                                                                # with a default value
                            set_dict_against_attributes_string(config, attributes_string, value)
                else:
                    unknown_configs.append(attributes_string)

            filled_values = missing_config_policy(unknown_configs, key)
            for attributes_string, value in filled_values.items():
                set_dict_against_attributes_string(_config_value_or_default, attributes_string, (False, value))
                set_dict_against_attributes_string(config, attributes_string, value)
                if has_been_deep_copied:  # in this case the changes should be reported within the context
                    set_dict_against_attributes_string(context['config'], attributes_string, value)

            return f(config, *args, **argv)

        return f_with_deps_resolved

    return sub


def register_config_default(attribute_string, default_value_type, default_value):
    if attribute_string in _config_value_or_default:  # should not happen, but tolerate the case where not a default val
        assert _config_value_or_default[attribute_string][0] == False, \
            f"Not allowing to register twice for the same default value location {attribute_string}"
    _config_value_or_default[attribute_string] = (True, default_value_type, default_value)


# some tweaks there to convert from string to any correct type
def right_type_for(value, type):
    return type(value)

def enrich_config(config_to_merge: Dict[str, Any]):
    context = current_ctxt()
    rightly_typed = {
        k: right_type_for(v, _config_value_or_default.get(k, (str, str))[1]) for k, v in config_to_merge
    }
    update_dict_check_already_there(context['config'], rightly_typed)
