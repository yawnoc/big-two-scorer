#!/usr/bin/env python3

"""
# big2.py

A Python scorer for Big Two (鋤大弟).

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import os
import re
import sys

__version__ = '0.0.0'


def get_duplicates(iterable):
    seen_items = set()
    duplicate_items = []
    for item in iterable:
        if item in seen_items:
            duplicate_items.append(item)
        else:
            seen_items.add(item)

    return duplicate_items


class ScoreMaster:
    def __init__(self, scores_text):
        self.players, self.games = ScoreMaster.parse(scores_text)

    LINE_EXPLAINER = (
        'A line must have one of the following forms:\n'
        '    <yyyy>-<mm>-<dd>     # a date\n'
        '    <P1> <P2> <P3> <P4>  # a list of player names (no hashes or leading digits)\n'
        '    <L1> <L2> <L3> <L4>  # a list of losses (number of cards with optional\n'
        '                         # suffix `t` for a player taking on all losses)\n'
        '    # <comment>          # a comment\n'
        'All other lines are invalid.\n'
    )

    @staticmethod
    def parse(scores_text):
        player_from_name = {}
        players = []
        games = []

        date = None
        names = None

        lines = scores_text.splitlines()
        for line_number, line in enumerate(lines, start=1):

            date_line_match = ScoreMaster.match_date_line(line)
            if date_line_match:
                date = date_line_match.group('date')
                continue

            players_line_match = ScoreMaster.match_players_line(line)
            if players_line_match:
                names = tuple(
                    players_line_match.group(f'name_{n}')
                    for n in (1, 2, 3, 4)
                )

                duplicate_names = get_duplicates(names)
                if duplicate_names:
                    raise ScoreMaster.DuplicateNamesException(
                        line_number,
                        duplicate_names,
                    )

                for name in names:
                    if name not in player_from_name:
                        player_from_name[name] = Player(name)
                continue

            game_line_match = ScoreMaster.match_game_line(line)
            if game_line_match:
                game_losses = tuple(
                    game_line_match.group(f'loss_{n}')
                    for n in (1, 2, 3, 4)
                )
                game_is_takes = tuple(
                    game_line_match.group(f'loss_{n}') != ''
                    for n in (1, 2, 3, 4)
                )

                if game_is_takes.count(True) > 1:
                    raise ScoreMaster.MultipleTakesException(line_number)

                game = Game(date, names, game_losses, game_is_takes)
                games.append(game)
                continue

            if ScoreMaster.match_comment_line(line):
                continue

            raise ScoreMaster.InvalidLineException(line_number)

        return players, games

    @staticmethod
    def match_date_line(line):
        return re.fullmatch(
            pattern=r'''
                ^ [\s]*
                (?P<date> [0-9]{4} - [0-9]{2} - [0-9]{2} )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_players_line(line):
        player_name_regex = r'[^\s#0-9][^\s#]*'
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?P<name_1> {player_name_regex} )
                    [\s]+
                (?P<name_2> {player_name_regex} )
                    [\s]+
                (?P<name_3> {player_name_regex} )
                    [\s]+
                (?P<name_4> {player_name_regex} )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_game_line(line):
        loss_regex = r'[0-9]+'
        take_regex = f'[t]?'
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?P<loss_1> {loss_regex} ) (?P<take_1> {take_regex} )
                    [\s]+
                (?P<loss_2> {loss_regex} ) (?P<take_2> {take_regex} )
                    [\s]+
                (?P<loss_3> {loss_regex} ) (?P<take_3> {take_regex} )
                    [\s]+
                (?P<loss_4> {loss_regex} ) (?P<take_4> {take_regex} )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_comment_line(line):
        return re.fullmatch(
            pattern=r'^ [\s]* (?: [#] .* )? $',
            string=line,
            flags=re.VERBOSE,
        )

    class DuplicateNamesException(Exception):
        def __init__(self, line_number, duplicate_names):
            self.line_number = line_number
            self.duplicate_names = duplicate_names

    class InvalidLineException(Exception):
        def __init__(self, line_number):
            self.line_number = line_number

    class MultipleTakesException(Exception):
        def __init__(self, line_number):
            self.line_number = line_number


class Player:
    def __init__(self, name):
        self.name = name


class Game:
    def __init__(self, date, names, losses, is_takes):
        self.date = date
        self.names = names
        self.losses = losses
        self.is_takes = is_takes


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


def read_scores_text(scores_file_name):
    if os.path.isdir(scores_file_name):
        print(
            f'Error: `{scores_file_name}` is a directory, not a file',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(scores_file_name, 'r', encoding='utf-8') as scores_file:
            scores_text = scores_file.read()
    except FileNotFoundError:
        print(
            f'Error: file `{scores_file_name}` not found',
            file=sys.stderr,
        )
        sys.exit(1)

    return scores_text


def main():
    parsed_arguments = parse_command_line_arguments()
    scores_file_name = parsed_arguments.scores_file_name

    scores_text = read_scores_text(scores_file_name)
    try:
        score_master = ScoreMaster(scores_text)
    except ScoreMaster.DuplicateNamesException as exception:
        line_number = exception.line_number
        duplicate_names = exception.duplicate_names
        print(
            f'Error: line {line_number} of `{scores_file_name}` has '
            f'duplicate player names {duplicate_names}'
        )
        sys.exit(1)
    except ScoreMaster.InvalidLineException as exception:
        line_number = exception.line_number
        print(
            f'Error: line {line_number} of `{scores_file_name}` invalid'
            f'\n\n{ScoreMaster.LINE_EXPLAINER}'
        )
        sys.exit(1)
    except ScoreMaster.MultipleTakesException as exception:
        line_number = exception.line_number
        print(
            f'Error: line {line_number} of `{scores_file_name}` has '
            f'multiple players taking on all losses (suffix `t`)'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
