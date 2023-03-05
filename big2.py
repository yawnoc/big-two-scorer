#!/usr/bin/env python3

"""
# big2.py

A Python scorer for Big Two (鋤大弟).

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import csv
import os
import re
import sys

__version__ = '0.0.0'
DEFAULT_FRY_THRESHOLD = MIN_FRY_THRESHOLD = 10
TRIPLE_FRY_THRESHOLD = 13


def get_duplicates(iterable):
    seen_items = set()
    duplicate_items = []
    for item in iterable:
        if item in seen_items:
            duplicate_items.append(item)
        else:
            seen_items.add(item)

    return duplicate_items


def robust_divide(dividend, divisor):
    try:
        return dividend / divisor
    except ZeroDivisionError:
        return None


def blunt(number, max_decimal_places=4):
    """
    Round a number to at most certain decimal places, as a string.
    """
    if number is None:
        return None

    if number == 0:
        return '0'

    max_decimal_places_format = f'%.{max_decimal_places}F'
    nice_string = max_decimal_places_format % number
    nice_string = re.sub(r'[.]?0*$', '', nice_string)

    return nice_string


def compute_fry_aware_loss(loss, fry_threshold):
    if loss < fry_threshold:
        return loss

    if loss < TRIPLE_FRY_THRESHOLD:
        return 2 * loss

    return 3 * loss


class ScoreMaster:
    def __init__(self, scores_text):
        self.players, self.games = ScoreMaster.parse(scores_text)

    LINE_EXPLAINER = (
        'A line must have one of the following forms:\n'
        '    <yyyy>-<mm>-<dd>     # a date\n'
       f'    F=<threshold>        # a declaration of fry threshold (default {DEFAULT_FRY_THRESHOLD})\n'
        '    <P1> <P2> <P3> <P4>  # a list of player names (no hashes, asterisks, or\n'
        '                         # leading digits)\n'
        '    <L1> <L2> <L3> <L4>  # a list of losses (number of cards with optional\n'
        '                         # suffix `t` for a player taking on all losses)\n'
        '    # <comment>          # a comment, also allowed at the end of the forms\n'
        '                         # above\n'
        'All other lines are invalid.\n'
    )

    @staticmethod
    def parse(scores_text):
        player_from_name = {}
        games = []

        game_number = 0
        date = None
        fry_threshold = DEFAULT_FRY_THRESHOLD
        names = None

        lines = scores_text.splitlines()
        for line_number, line in enumerate(lines, start=1):

            date_line_match = ScoreMaster.match_date_line(line)
            if date_line_match:
                date = date_line_match.group('date')
                continue

            threshold_line_match = ScoreMaster.match_threshold_line(line)
            if threshold_line_match:
                fry_threshold = int(threshold_line_match.group('fry_threshold'))
                if fry_threshold < MIN_FRY_THRESHOLD:
                    raise ScoreMaster.FryThresholdTooLowException(
                        line_number,
                        f'fry threshold {fry_threshold} is below {MIN_FRY_THRESHOLD}'
                    )
                continue

            players_line_match = ScoreMaster.match_players_line(line)
            if players_line_match:
                names = tuple(
                    players_line_match.group(f'name_{i}')
                    for i in range(0, 4)
                )

                duplicate_names = get_duplicates(names)
                if duplicate_names:
                    raise ScoreMaster.DuplicatePlayerNamesException(
                        line_number,
                        f'duplicate player names {duplicate_names}',
                    )

                for name in names:
                    if name not in player_from_name:
                        player_from_name[name] = Player(name)
                continue

            game_line_match = ScoreMaster.match_game_line(line)
            if game_line_match:
                if names is None:
                    raise ScoreMaster.NoPlayersException(
                        line_number,
                        f'game losses declared without first declaring player names'
                    )

                game_number += 1

                losses = tuple(
                    int(game_line_match.group(f'loss_{i}'))
                    for i in range(0, 4)
                )
                if losses.count(0) != 1:
                    raise ScoreMaster.NonSingleWinnerException(
                        line_number,
                        'game does not have exactly one winner (loss `0`)',
                    )
                winner_index = losses.index(0)

                is_takes = tuple(
                    game_line_match.group(f'take_{i}')
                    for i in range(0, 4)
                )
                if is_takes.count('t') > 1:
                    raise ScoreMaster.MultipleTakesException(
                        line_number,
                        'multiple players taking on all losses (suffix `t`)',
                    )
                try:
                    take_index = is_takes.index('t')
                except ValueError:
                    take_index = None

                game = Game(game_number, date, fry_threshold, names, losses, winner_index, take_index)
                games.append(game)
                continue

            if ScoreMaster.match_comment_line(line):
                continue

            raise ScoreMaster.InvalidLineException(
                line_number,
                f'invalid line\n\n{ScoreMaster.LINE_EXPLAINER}'
            )

        for game in games:
            game.update(player_from_name)

        players = list(player_from_name.values())
        everyone = Player('*')
        everyone.is_regular = True
        everyone.game_count = sum(p.game_count for p in players)
        everyone.win_count = sum(p.win_count for p in players)
        everyone.fry_count = sum(p.fry_count for p in players)
        everyone.real_losses = sum(p.real_losses for p in players)
        everyone.net_score = sum(p.net_score for p in players)

        return players + [everyone], games

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
    def match_threshold_line(line):
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                F=(?P<fry_threshold> [0-9]+ )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_players_line(line):
        player_name_regex = r'[^\s#*0-9][^\s#*]*'
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?P<name_0> {player_name_regex} )
                    [\s]+
                (?P<name_1> {player_name_regex} )
                    [\s]+
                (?P<name_2> {player_name_regex} )
                    [\s]+
                (?P<name_3> {player_name_regex} )
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
                (?P<loss_0> {loss_regex} ) (?P<take_0> {take_regex} )
                    [\s]+
                (?P<loss_1> {loss_regex} ) (?P<take_1> {take_regex} )
                    [\s]+
                (?P<loss_2> {loss_regex} ) (?P<take_2> {take_regex} )
                    [\s]+
                (?P<loss_3> {loss_regex} ) (?P<take_3> {take_regex} )
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

    def write_tsv(self, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator=os.linesep)
            writer.writerow([
                'name',
                'is_regular',
                'game_count',
                'win_count',
                'fry_count',
                'real_losses',
                'net_score',
                'win_fraction',
                'fry_fraction',
                'real_losses_per_game',
                'net_score_per_game',
            ])
            for player in sorted(
                self.players,
                key=lambda p: (p.name == '*', -p.is_regular, p.real_losses_per_game, p.name),
            ):
                player.update_averages()
                writer.writerow([
                    player.name,
                    player.is_regular,
                    player.game_count,
                    player.win_count,
                    player.fry_count,
                    player.real_losses,
                    player.net_score,
                    blunt(player.win_fraction),
                    blunt(player.fry_fraction),
                    blunt(player.real_losses_per_game),
                    blunt(player.net_score_per_game),
                ])

    class BadLineException(Exception):
        def __init__(self, line_number, message):
            self.line_number = line_number
            self.message = message

    class FryThresholdTooLowException(BadLineException):
        pass

    class DuplicatePlayerNamesException(BadLineException):
        pass

    class NoPlayersException(BadLineException):
        pass

    class NonSingleWinnerException(BadLineException):
        pass

    class MultipleTakesException(BadLineException):
        pass

    class InvalidLineException(BadLineException):
        pass


class Player:
    def __init__(self, name):
        self.name = name
        self.is_regular = False

        self.game_count = 0
        self.win_count = 0
        self.fry_count = 0
        self.real_losses = 0
        self.net_score = 0

        self.win_fraction = 0
        self.fry_fraction = 0
        self.real_losses_per_game = 0
        self.net_score_per_game = 0

    def update_averages(self):
        self.win_fraction = robust_divide(self.win_count, self.game_count)
        self.fry_fraction = robust_divide(self.fry_count, self.game_count)
        self.real_losses_per_game = robust_divide(self.real_losses, self.game_count)
        self.net_score_per_game = robust_divide(self.net_score, self.game_count)


class Game:
    def __init__(self, game_number, date, fry_threshold, names, losses, winner_index, take_index):
        self.game_number = game_number
        self.date = date
        self.fry_threshold = fry_threshold
        self.names = names
        self.losses = losses
        self.winner_index = winner_index
        self.take_index = take_index

    def update(self, player_from_name):
        real_losses = Game.compute_real_losses(self.losses, self.fry_threshold, self.take_index)
        net_score = Game.compute_net_scores(real_losses)

        for index, name in enumerate(self.names):
            player = player_from_name[name]
            player.is_regular = player.game_count >= self.game_number / 4

            player.game_count += 1
            player.win_count += 1 if index == self.winner_index else 0
            player.fry_count += 1 if self.losses[index] >= self.fry_threshold else 0
            player.real_losses += real_losses[index]
            player.net_score += net_score[index]

            player.update_averages()

    @staticmethod
    def compute_real_losses(losses, fry_threshold, take_index):
        """
        Compute the tuple of real losses.

        Accounts for the cases of:
        - Frying
        - A player taking on all losses
        """
        fry_aware_losses = tuple(
            compute_fry_aware_loss(loss, fry_threshold)
            for loss in losses
        )

        if take_index is None:
            return fry_aware_losses

        return tuple(
            sum(fry_aware_losses) if i == take_index else 0
            for i in range(0, 4)
        )

    @staticmethod
    def compute_net_scores(real_losses):
        """
        Compute the tuple of net scores (zero-sum scores).
        """
        return tuple(
            sum(real_losses) - 4 * real_losses[i]
            for i in range(0, 4)
        )


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
        help='name of scores file; output written to `{scores.txt}.tsv`',
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
    except ScoreMaster.BadLineException as exception:
        line_number = exception.line_number
        message = exception.message
        print(
            f'Error (`{scores_file_name}`, line {line_number}): {message}'
        )
        sys.exit(1)

    tsv_file_name = f'{scores_file_name}.tsv'
    score_master.write_tsv(tsv_file_name)


if __name__ == '__main__':
    main()
