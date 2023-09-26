from .unreadable_config import unreadable_config_policy
from .default_path import default_config_paths

import configparser
import yaml


def parse_yaml(location):
    with open(location, 'r') as f:
        config = yaml.safe_load(f)
    if 'subconfig' in config:
        subconfig = config['subconfig']
        if not subconfig in config:
            raise Exception(f"Expecting provided subconfig {config['subconfig']} to be provided as dict")
    else:
        subconfig = 'default'
        if not config.get(subconfig):
            return {'subconfig': subconfig}

    if 'subconfig' in config[subconfig]:
        raise Exception(f"Not expecting subconfig an item of the {subconfig} dict")

    config[subconfig]['subconfig'] = subconfig
    return config[config['subconfig']]


def parse_section_recursive(config, subconfig, default_keys):
    result = {}
    for k, v in config[subconfig].items():
        if k not in default_keys:
            print(k, v)
            if '|' in k:
                name, t = k.split('|')
                if t == 'list':
                    result[name] = v.split(',')
                elif t == 'dict':
                    result[name] = parse_section_recursive(config, v, default_keys)
                elif t == 'list-dict':
                    result[name] = list(map(lambda s: parse_section_recursive(config, s, default_keys), v.split(',')))
                else:
                    raise Exception(f"Unexpected type {t}, expecting list, dict or list-dict")
            else:
                result[k] = v
    return result


def parse_ini(location):
    with open(location, 'r') as f:  # raise exception is not existing, otherwise configparser does not
        pass

    config = configparser.ConfigParser()
    config.read(location)

    if not 'subconfig' in config['DEFAULT']:
        subconfig = 'default'
    else:
        subconfig = config['DEFAULT']['subconfig']

    if subconfig not in config:
        raise Exception(f"Expecting provided subconfig {subconfig} to be provided as section")

    result_config = parse_section_recursive(config, subconfig, config['DEFAULT'].keys())
    result_config.update({'subconfig': subconfig})

    #config['DEFAULT']['subconfig'] = 'default'
    # with open(location, 'w') as configfile:
    #     config.write(configfile)
    return result_config


def parse_config(location):
    if location[-4:] == '.ini':
        loaded_config = parse_ini(location)
    elif location[-5:] == '.yaml' or location[-4:] == '.yml':
        loaded_config = parse_yaml(location)
    else:
        raise Exception(f"Expecting some .ini, .yaml or .yml file as configuration input")
    return loaded_config


def try_open_and_parse_config(config_dict):
    possible_locations = [config_dict['.config']] if '.config' in config_dict else []
    possible_locations.extend(default_config_paths())

    last_location = None
    while possible_locations:
        location = possible_locations.pop(0)
        try:
            loaded_config = parse_config(location)
        except Exception as e:
            last_location = unreadable_config_policy(location, len(possible_locations) > 0, e)
    if last_location:  # gives it a last try
        loaded_config = parse_config(last_location)
    print(loaded_config)
