#!/usr/bin/env python3

"""
# test_big2.py

Perform unit testing for `big2.py`.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import unittest

from big2 import get_duplicates, robust_divide, compute_fry_aware_loss
from big2 import ScoreMaster


class TestBig2(unittest.TestCase):
    def test_get_duplicates(self):
        self.assertEqual(get_duplicates([]), [])
        self.assertEqual(get_duplicates([1, 2, 3]), [])
        self.assertEqual(get_duplicates([1, 1, 2, 3, 'x', 'y', 'x']), [1, 'x'])
        self.assertEqual(get_duplicates(['a', 'b', 'c', 'b']), ['b'])

    def test_robust_divide(self):
        self.assertEqual(robust_divide(0, 0), None)
        self.assertEqual(robust_divide(1, 0), None)
        self.assertAlmostEqual(robust_divide(1, 1), 1)
        self.assertAlmostEqual(robust_divide(1, 2), 0.5)
        self.assertAlmostEqual(robust_divide(100, 2), 50)

    def test_compute_fry_aware_loss(self):
        self.assertEqual(compute_fry_aware_loss(1, fry_threshold=10), 1)
        self.assertEqual(compute_fry_aware_loss(9, fry_threshold=10), 9)
        self.assertEqual(compute_fry_aware_loss(10, fry_threshold=10), 20)
        self.assertEqual(compute_fry_aware_loss(11, fry_threshold=10), 22)
        self.assertEqual(compute_fry_aware_loss(12, fry_threshold=10), 24)
        self.assertEqual(compute_fry_aware_loss(13, fry_threshold=10), 39)
        self.assertEqual(compute_fry_aware_loss(100, fry_threshold=10), 300)

        self.assertEqual(compute_fry_aware_loss(1, fry_threshold=11), 1)
        self.assertEqual(compute_fry_aware_loss(9, fry_threshold=11), 9)
        self.assertEqual(compute_fry_aware_loss(10, fry_threshold=11), 10)
        self.assertEqual(compute_fry_aware_loss(11, fry_threshold=11), 22)
        self.assertEqual(compute_fry_aware_loss(12, fry_threshold=11), 24)
        self.assertEqual(compute_fry_aware_loss(13, fry_threshold=11), 39)
        self.assertEqual(compute_fry_aware_loss(100, fry_threshold=11), 300)

        self.assertEqual(compute_fry_aware_loss(1, fry_threshold=500), 1)
        self.assertEqual(compute_fry_aware_loss(9, fry_threshold=500), 9)
        self.assertEqual(compute_fry_aware_loss(10, fry_threshold=500), 10)
        self.assertEqual(compute_fry_aware_loss(11, fry_threshold=500), 11)
        self.assertEqual(compute_fry_aware_loss(12, fry_threshold=500), 12)
        self.assertEqual(compute_fry_aware_loss(13, fry_threshold=500), 13)
        self.assertEqual(compute_fry_aware_loss(100, fry_threshold=500), 100)

    def test_score_master_parse_fry_threshold(self):
        self.assertRaises(
            ScoreMaster.FryThresholdTooLowException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'F=0',
        )
        self.assertRaises(
            ScoreMaster.FryThresholdTooLowException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'F=9',
        )
        try:
            ScoreMaster.parse('F=10')
        except ScoreMaster.FryThresholdTooLowException:
            self.fail('ScoreMaster.FryThresholdTooLowException raised erroneously')

    def test_score_master_parse_duplicate_names(self):
        self.assertRaises(
            ScoreMaster.DuplicatePlayerNamesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A A B C',
        )
        self.assertRaises(
            ScoreMaster.DuplicatePlayerNamesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A A A A',
        )
        try:
            ScoreMaster.parse('A B C D')
        except ScoreMaster.DuplicatePlayerNamesException:
            self.fail('ScoreMaster.DuplicatePlayerNamesException raised erroneously')

    def test_score_master_no_players(self):
        self.assertRaises(
            ScoreMaster.NoPlayersException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            '0 1 2 3',
        )

    def test_score_master_parse_non_single_winner(self):
        self.assertRaises(
            ScoreMaster.NonSingleWinnerException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 1 2 3 4',
        )
        self.assertRaises(
            ScoreMaster.NonSingleWinnerException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 0 1 2',
        )
        self.assertRaises(
            ScoreMaster.NonSingleWinnerException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 0 0 0',
        )
        try:
            ScoreMaster.parse('A B C D \n 0 1 2 3')
        except ScoreMaster.NonSingleWinnerException:
            self.fail('ScoreMaster.NonSingleWinnerException raised erroneously')

    def test_score_master_multiple_takes(self):
        self.assertRaises(
            ScoreMaster.MultipleTakesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 1t 2t 3',
        )
        self.assertRaises(
            ScoreMaster.MultipleTakesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 1t 2t 3t',
        )
        try:
            ScoreMaster.parse('A B C D \n 0 1 2 3')
        except ScoreMaster.MultipleTakesException:
            self.fail('ScoreMaster.MultipleTakesException raised erroneously')
        try:
            ScoreMaster.parse('A B C D \n 0 1 2t 3')
        except ScoreMaster.MultipleTakesException:
            self.fail('ScoreMaster.MultipleTakesException raised erroneously')

    def test_score_master_winner_takes(self):
        self.assertRaises(
            ScoreMaster.WinnerTakesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0t 1 2 3',
        )
        try:
            ScoreMaster.parse('A B C D \n 0 1 2t 3')
        except ScoreMaster.WinnerTakesException:
            self.fail('ScoreMaster.WinnerTakesException raised erroneously')

    def test_score_master_invalid_line(self):
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'abc',
        )
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            '1989-06-04 !',
        )
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'F = 13',
        )
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C# D',
        )
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C* D',
        )
        self.assertRaises(
            ScoreMaster.InvalidLineException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B 3C D',
        )


if __name__ == '__main__':
    unittest.main()
