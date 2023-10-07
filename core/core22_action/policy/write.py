from ...core11_config.config import register_config_default, config_dependencies, Config
from ...core30_context.context_dependency_graph import context_producer, context_dependencies
from ...core30_context.context import Context
from .send import default_send_cli

from typing import Callable, Any
from logging import Logger
from enum import Enum, auto
import os.path
import json
import yaml


class WriteOnExistingFile(Enum):
    RAISE = auto()
    WARNING_DONT_DO = auto()
    WARNING_DO = auto()
    APPEND = auto()
    SILENT_DONT_DO = auto()
    SILENT_DO = auto()

class EnforceFormatFromExt(Enum):
    EXT_TO_FORMAT = auto()
    DONT_CARE = auto()

class OutputFormat(Enum):
    TEXT = auto()
    JSON = auto()
    YAML = auto()
    INI = auto()


register_config_default('.interactor.output.file.rewrite_behavior', WriteOnExistingFile,
                        WriteOnExistingFile.WARNING_DONT_DO)
register_config_default('.interactor.output.file.rewrite_behavior_if_forced', WriteOnExistingFile,
                        WriteOnExistingFile.WARNING_DO)
register_config_default('.interactor.output.ext_behavior', EnforceFormatFromExt, EnforceFormatFromExt.EXT_TO_FORMAT)
register_config_default('.interactor.output.format', OutputFormat, OutputFormat.TEXT)


@config_dependencies(('.interactor.output.ext_behavior', EnforceFormatFromExt),
                     ('.interactor.output.format', OutputFormat))
@context_dependencies(('.log.debug_logger', Logger | None))
def format_data(ctxt: Context, config: Config, data: Any, output_format: OutputFormat, destination: Any):
    if not destination:  # this case is the default with the interactor write to, so get the config option
        fmt = config['interactor']['output']['format']
    elif isinstance(destination, str):  # this case we should have an output file (in the future it may change)
        if config['interactor']['output']['ext_behavior'] == EnforceFormatFromExt.DONT_CARE:
            fmt = config['interactor']['output']['format']
        else:
            lower_dst = destination[-5:].lower()
            if lower_dst== '.json':
                fmt = OutputFormat.JSON
            elif lower_dst == '.yaml' or lower_dst[-4:] == '.yml':
                fmt = OutputFormat.YAML
            else:
                fmt = OutputFormat.TEXT
            if output_format and fmt != output_format:
                ctxt['log']['debug_logger'].debug(f"Specified output format {output_format}"
                                                  f" not considered regarding extension {fmt}")
    else:
        raise NotImplementedError

    if fmt == OutputFormat.TEXT:
        return f"{data}"
    elif fmt == OutputFormat.JSON:
        return json.dumps(data)
    elif fmt == OutputFormat.YAML:
        return yaml.dump(data)
    else:
        raise NotImplementedError


@config_dependencies(('.interactor.output.file.rewrite_behavior', WriteOnExistingFile),
                     ('.interactor.output.file.rewrite_behavior_if_forced', WriteOnExistingFile))
@context_dependencies(('.interactor.output.write_to', Callable[[str], None]), ('.log.main_logger', Logger),
                      ('.interactor.local', bool, False), ('.interactor.cli', bool, False))
def write_data(ctxt: Context, config: Config, input_data: Any, output_format: OutputFormat,
               destination: Any | None = None, **additional_arguments):
    formatted_data = format_data(input_data, output_format, destination)
    if not destination:
        return ctxt['interactor']['output']['write_to'](formatted_data)
    elif isinstance(destination, str):  # this case we should have an output file (in the future it may change)
        already_existing = os.path.isfile(destination)
        mode = 'w'
        do_ok = True
        if already_existing:
            if 'force' in additional_arguments and additional_arguments['force']:
                policy = config['interactor']['output']['file']['rewrite_behavior_if_forced']
            else:
                policy = config['interactor']['output']['file']['rewrite_behavior']
            if policy == WriteOnExistingFile.RAISE:
                raise Exception(f"Forbidden attempt to rewrite file {destination}")
            elif policy == WriteOnExistingFile.WARNING_DO:
                ctxt['log']['main_logger'].warning(f"File {destination} will be rewritten with new data "
                                                   f"due to current policy")
            elif policy == WriteOnExistingFile.WARNING_DONT_DO:
                ctxt['log']['main_logger'].warning(f"File {destination} won't be rewritten with new data "
                                                   f"due to current policy")
                do_ok = False
            elif policy == WriteOnExistingFile.APPEND:
                mode = 'a'
            elif policy == WriteOnExistingFile.SILENT_DONT_DO:
                do_ok = False

        if do_ok:
            with open(destination, mode) as f:
                f.write(formatted_data)
    else:
        raise NotImplementedError  # future cases: network send, database send, C2 send, etc ...


@context_producer(('.interactor.output.write_to', Callable[[str], None]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))  # dynamically generated
def output_write_to(ctxt: Context):
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor'].setdefault('output', {})['write_to'] = default_send_cli
    else:
        raise NotImplementedError
