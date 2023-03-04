#!/usr/bin/env python3

"""
# test_big2.py

Perform unit testing for `big2.py`.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import unittest

from big2 import get_duplicates, robust_divide


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


if __name__ == '__main__':
    unittest.main()
