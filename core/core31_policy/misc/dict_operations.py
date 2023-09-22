from typing import Dict, Any
from enum import Enum


class UpdateDictConflict(Enum):
    KEEP = 1
    MERGE = 2
    CHOOSE = 3  # this one indicates interaction will be used (more complicated)

@init_policy
def init(ctxt: Context):
    return register_policy(ctxt, 'misc.update_dict_conflict', UpdateDictConflict, config=True)


def already_in_dict(ctxt: Context, initial_dict: Dict[Any, Any], dict_to_merge_into: Dict[Any, Any]):
    common_keys = initial_dict.keys().intersection(dict_to_merge_into.keys())
    optional_debug_logger = ctxt['policy']['log']['debug_logger']
    if optional_debug_logger:
        optional_debug_logger.debug(f"Common keys {common_keys} between the two provided dicts")
    if common_keys:
        if ctxt['config']['exception']['level'].lower() == ExceptionLevel.LAX.name.lower():
            if optional_debug_logger:
                optional_debug_logger.debug('Policy LAX so only warning printed as there are common keys')
            ctxt['policy']['log']['logger'].warning(f"¨Warning common keys {common_keys} between provided dicts")
        elif ctxt['config']['exception_level'] == policy.exeception_level.STRICT:
            if optional_debug_logger:
                optional_debug_logger.debug('Policy STRICT so raising exception as there are common keys between'
                                            ' provided dicts')
            raise Exception(f"Dict to merge into keys are already in source dict: {common_keys}")
        else:
            raise Exception(f"config value for exception_level must be either {policy.exeception_level.LAX} or "
                            f"{policy.exeception_level.STRICT}, not {ctxt['config']['exception_level']}")
    return common_keys


def update_dict_check_already_there(ctxt: Context, initial_dict: Dict[Any, Any], dict_to_merge_into: Dict[Any, Any]):
    common_keys = already_in_dict(ctxt, initial_dict, dict_to_merge_into)

    if common_keys:  # ctxt['config']['policy.exception'] is lax otherwise the already_in_dict function would fail
        ctxt['policy']['log']['logger'].warning(f"¨Warning common keys {common_keys}, dict will be modified or"
                                                f" not according to ctxt['config']['update_dict_conflict']")
        if ctxt['config'].get('update_dict_conflict', UpdateDictConflict.KEEP.name) == UpdateDictConflict.KEEP.name:
            initial_dict.update(**{k: v for k, v in dict_to_merge_into if k not in common_keys})
        elif ctxt['config']['update_dict_conflict'] == UpdateDictConflict.MERGE.name:
            initial_dict.update(dict_to_merge_into)
        elif ctxt['config']['update_dict_conflict'] == UpdateDictConflict.CHOOSE.name:
            initial_dict.update(dict_to_merge_into)
        else:
            raise Exception(f"config value for update_dict_conflict must be either {UpdateDictConflict.KEEP}, "
                            f"{UpdateDictConflict.MERGE} or {UpdateDictConflict.CHOOSE}, not "
                            f"{ctxt['config']['update_dict_conflict']}")
    else:
        initial_dict.update(dict_to_merge_into)

    return common_keys


register_policy('update_dict_check_already_there', [policy.LAX, policy.STRICT])
register_policy('already_in_dict', [policy.LAX, policy.STRICT])
