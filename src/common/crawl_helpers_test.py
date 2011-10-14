#!/usr/bin/env python
"""crawl_helpers_test.py: Tests for crawl_helpers.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from crawl_helpers import FilterListBySuffix
from crawl_helpers import GetLinksFromHtml
import unittest
import StringIO

class FilterListBySuffixTest(unittest.TestCase):
    def setUp(self):
        self.items = ['string1.suffix1',
                      'string2.suffix1',
                      'string3.suffix2',
                      'string4.suffix3']
        
    def testFilterListBySuffixWorks(self):
        new_list = FilterListBySuffix(self.items, '.suffix1')
        assert len(new_list) == 2
        assert new_list[0] == 'string1.suffix1'
        assert new_list[1] == 'string2.suffix1'

class GetLinksFromHtmlTest(unittest.TestCase):
    def testGetLinksFromHtmlWorks(self):
        file_handle = StringIO.StringIO('<a href="http://www.test.com">')
        link_list = GetLinksFromHtml(file_handle)
        assert len(link_list) == 1
        assert link_list[0] == 'http://www.test.com'

    def testSectionLinksAreIgnored(self):
        file_handle = StringIO.StringIO('<a href="#section">')
        link_list = GetLinksFromHtml(file_handle)
        assert len(link_list) == 0

    def testSectionMarksAreIgnored(self):
        file_handle = StringIO.StringIO('<a name="section">')
        link_list = GetLinksFromHtml(file_handle)
        assert len(link_list) == 0
    
if __name__ == "__main__":
    unittest.main()

