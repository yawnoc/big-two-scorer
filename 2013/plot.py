#!/usr/bin/env python3

"""
# plot.py

Make interesting plots of the 2013 scores.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""


import csv

import matplotlib.pyplot as plt


def read_scores(file_name):
    with open(file_name, 'r', encoding='utf-8', newline='') as file:
        rows = list(csv.DictReader(file, delimiter='\t'))

    return rows


def make_plot(rows, x_variable, y_variable):
    regular_rows = [r for r in rows if r['is_regular'] == 'True']

    x_values = [float(r[x_variable]) for r in regular_rows]
    y_values = [float(r[y_variable]) for r in regular_rows]
    names = [r['name'] for r in regular_rows]
    data_count = len(regular_rows)

    figure, axes = plt.subplots()
    axes.scatter(
        x_values,
        y_values,
        s=100,
        facecolors='none',
        edgecolors=(data_count - 1) * ['blue'] + ['red'],
    )
    for x, y, name in zip(x_values, y_values, names):
        axes.annotate(
            name,
            (x, y),
            xytext=(7, 2),
            textcoords='offset points',
        )

    axes.set(
        title=f'{x_variable} vs {y_variable}',
        xlabel=x_variable,
        ylabel=y_variable,
    )
    axes.grid(True)

    plt.savefig(f'{x_variable}-vs-{y_variable}.svg')


def main():
    rows = read_scores('big-two-2013.txt.tsv')
    make_plot(
        rows,
        x_variable='real_losses_per_game',
        y_variable='win_fraction',
    )


if __name__ == '__main__':
    main()
