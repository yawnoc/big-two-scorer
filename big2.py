#!/usr/bin/env python3

"""
# big2.py

A Python scorer for Big Two (鋤大弟).

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse


__version__ = '0.0.0'


DESCRIPTION = 'Score some games of Big Two (鋤大弟).'


def parse_command_line_arguments():
    argument_parser = argparse.ArgumentParser(description=DESCRIPTION)
    argument_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{argument_parser.prog} version {__version__}',
    )
    argument_parser.add_argument(
        'scores_file_name',
        help='name of scores file',
        metavar='scores.txt',
    )

    return argument_parser.parse_args()


def main():
    parsed_arguments = parse_command_line_arguments()


if __name__ == '__main__':
    main()
