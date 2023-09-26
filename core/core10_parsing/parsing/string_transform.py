from ...core11_config.parsing.set import check_and_parse_set_options
import logging


cli_string_transforms = {
    '.log_level': lambda v: getattr(logging, v.upper()),
    '.additional_options': lambda v: check_and_parse_set_options(v),
}
