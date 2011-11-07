#!/usr/bin/env python
"""google_helper_test.py: Tests for google_helper.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from google_helper import GoogleSearch

import mock
import pickle
import testfixtures
import unittest

class GoogleApiMock():
    def __init__(self):
        self.service = mock.Mock()
        mock_search_engine = mock.Mock()
        mock_search_engine.list = self.mock_list
        self.cse = mock.Mock(return_value=mock_search_engine)

    def mock_list(self, q, cref, start, num):
        filename = ('test/data/googlesearch_%s_%d_%d.p' % (q, start, num))
        with open(filename, 'rb') as f:
            search_result = pickle.load(f)
        response = mock.Mock()
        response.execute = mock.Mock(return_value=search_result)
        return response

class GoogleSearchTest(unittest.TestCase):
    def testGoogleSearchWorks(self):
        with testfixtures.Replacer() as r:
            r.replace('apiclient.discovery.build', mock.Mock(return_value=GoogleApiMock()))
            search_results = GoogleSearch(
                'AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                '017513622067795982245:_iwk5xznrk0',
                'google')
            assert len(filter(lambda r: r.link == 'http://www.google.com/',
                              search_results)) > 0

    def testGoogleSearchWithMaxResultsWork(self):
        with testfixtures.Replacer() as r:
            r.replace('apiclient.discovery.build', mock.Mock(return_value=GoogleApiMock()))
            search_results = GoogleSearch(
                'AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                '017513622067795982245:_iwk5xznrk0',
                'google',
                max_results=20)
            assert len(search_results) <= 20
            search_results = GoogleSearch(
                'AIzaSyCrGh4R7a7-ayRQyh7nXPwuBy6O7F0VqRM',
                '017513622067795982245:_iwk5xznrk0',
                'google',
                max_results=13)
            assert len(search_results) <= 13
