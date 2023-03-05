# big-two-scorer

A Python scorer for Big Two (鋤大弟).

Licensed under MIT No Attribution (MIT-0), see [LICENSE].


## Usage

```bash
$ path/to/big2.py [-h] [-v] scores.txt

Score some games of Big Two (鋤大弟).

positional arguments:
  scores.txt     name of scores file; output written to `{scores.txt}.tsv`

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```


## Scores file syntax

The scorer reads a plain-text file of Big Two scores.
Each line must have one of the following forms:

| Form | Meaning |
| - | - |
| `<yyyy>-<mm>-<dd>` | a date |
| `F=<threshold>` | a declaration of fry threshold (default 10) |
| `<P1> <P2> <P3> <P4>` | a list of player names (no hashes, asterisks, or leading digits) |
| `<L1> <L2> <L3> <L4>` | a list of losses (number of cards with optional suffix `t` for a player taking on all losses) |
| `# <comment>` | a comment, also allowed at the end of the forms above |


[LICENSE]: LICENSE
