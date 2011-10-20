#!/usr/bin/env python
"""google_helper_test.py: Tests for google_helper.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from google_helper import GoogleSearch

import unittest

class GoogleSearchTest(unittest.TestCase):
    # Attention: these test is flaky for a set of reasons: the number of
    # requests per day is limited, and the first 10 results for Google might not
    # contain 'http://www.google.com' (but this is less probable).
    def testGoogleSearchWorks(self):
        search_results = GoogleSearch('AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                                      '017513622067795982245:_iwk5xznrk0',
                                      'Google')
        assert len(filter(lambda r: r.link == 'http://www.google.com/',
                          search_results)) > 0

    def testGoogleSearchWithMaxResultsWork(self):
        search_results = GoogleSearch('AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                                      '017513622067795982245:_iwk5xznrk0',
                                      'Google',
                                      max_results=20)
        assert len(search_results) == 20
        search_results = GoogleSearch('AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                                      '017513622067795982245:_iwk5xznrk0',
                                      'Google',
                                      max_results=13)
        assert len(search_results) == 13
