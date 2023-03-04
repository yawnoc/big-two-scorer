#!/usr/bin/env python3

"""
# test_big2.py

Perform unit testing for `big2.py`.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import unittest

from big2 import get_duplicates, robust_divide, compute_fry_aware_loss


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


if __name__ == '__main__':
    unittest.main()
