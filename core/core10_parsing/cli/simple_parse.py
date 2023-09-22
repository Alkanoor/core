from typing import List
import argparse


def parse_string():
    pass

# rule of thumb here is there is no positional argument parsing unless it is the next step to parse
def default_recursive_parse(arguments_list: List[str]):
    argparse.ArgumentParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', action='append')
    parser.add_argument('bar')
    parser.add_argument('--badger', action='append')
    print(parser.parse_known_args(['--foo', 'oo','--badger', 'BAR', 'spam', '--foo', 'x']))

