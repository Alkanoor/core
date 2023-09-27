import yaml

from ..config import config_dependencies, Config

from typing import Dict
import configparser


def compute_string_dict_hash(string_dict: Dict[str, str]):
    return hash(frozenset(sorted(string_dict.items())))

def compute_hashes_for_sections(config_parser: configparser.ConfigParser):
    return {
        compute_string_dict_hash(config_parser[section]): section for section in config_parser.sections()
    }


def recursive_config_iterator(config: Config, config_parser: configparser.ConfigParser,
                              hashes_for_sections: Dict[str, str]):
    config_parser_dict = {}
    for section_or_attribute, value in config.items():
        if isinstance(value, str):
            config_parser_dict[section_or_attribute] = value
        elif isinstance(value, dict):
            subconfig = recursive_config_iterator(config[section_or_attribute], config_parser, hashes_for_sections)
            config_parser_dict[f"{section_or_attribute}|dict"] = subconfig
        elif isinstance(value, list) or isinstance(value, set):
            if all([isinstance(v, str) for v in value]):
                config_parser_dict[f"{section_or_attribute}|list"] = ','.join(value)
            elif all([isinstance(v, dict) for v in value]):
                raise NotImplementedError
            else:
                raise Exception(f"Mixing types not supported (expecting all strings or all dicts)")

    result_hash = compute_string_dict_hash(config_parser_dict)
    if result_hash not in hashes_for_sections:
        i = 0
        while f"{section_or_attribute}-{i}" in config_parser.sections():
            i += 1
        hashes_for_sections[result_hash] = f"{section_or_attribute}-{i}"
        config_parser[f"{section_or_attribute}-{i}"] = config_parser_dict
    return hashes_for_sections[result_hash]


def write_config_ini(string_config: Dict[str, str | Dict], location: str):
    config_parser = configparser.ConfigParser()

    config = configparser.ConfigParser()
    config.read(location)  # read it so that it can be compared to current state

    subconfig = string_config.get('subconfig', 'default')
    config_parser['DEFAULT']['subconfig'] = subconfig
    config_parser[subconfig] = {}

    hashes_for_sections = compute_hashes_for_sections(config)
    recursive_config_iterator(string_config, config_parser, hashes_for_sections)

    with open(location, 'w') as configfile:
        config_parser.write(configfile)


def write_config_yaml(config: Config, location: str):
    subconfig = config.get('subconfig', 'default')

    try:
        with open(location, 'r') as previous_conf:
            to_write = yaml.safe_load(previous_conf)
    except:
        to_write = {}

    print("la")
    print(config)
    to_write.update({'DEFAULT': subconfig})
    to_write.update({subconfig: config})

    with open(location, 'w') as configfile:
        yaml.dump(to_write, configfile)


def write_config(config: Config, location: str):
    if location[-4:] == '.ini':
        write_config_ini(config, location)
    elif location[-5:] == '.yaml' or location[-4:] == '.yml':
        write_config_yaml(config, location)
    else:
        raise Exception(f"Expecting some .ini, .yaml or .yml file as configuration input")


@config_dependencies(('.subconfig', str))
def write_current_config(config: Config, location: str):
    write_config(config, location)
