#!/usr/bin/env python3

"""
# plot.py

Make interesting plots of the 2013 scores.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""


import csv


def read_scores(file_name):
    with open(file_name, 'r', encoding='utf-8', newline='') as file:
        rows = list(csv.DictReader(file, delimiter='\t'))

    return rows


def make_plot(rows, x_variable, y_variable):
    pass


def main():
    rows = read_scores('big-two-2013.txt.tsv')
    make_plot(
        rows,
        x_variable='real_losses_per_game',
        y_variable='win_fraction',
    )


if __name__ == '__main__':
    main()
