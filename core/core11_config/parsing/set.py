from typing import List


def check_and_parse_set_options(values: List[str]):
    return list(map(check_and_parse_set_option, values))


def check_and_parse_set_option(value: str):
    if '=' not in value:
        raise Exception(f"Expecting = to get key, value for config option, but found {value}")
    s = value.split('=')
    return s[0], '='.join(s[1:])
