#!/usr/bin/env python
"""crawl_helpers_test.py: Tests for crawl_helpers.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from crawl_helpers import DownloadAsTemporaryFile
from crawl_helpers import FilterListBySuffix
from crawl_helpers import GetLinksFromHtml
from crawl_helpers import GetUrlPriority
from crawl_helpers import IsBlenderFile

import StringIO
import unittest
import urllib2

class DownloadAsTemporaryFileTest(unittest.TestCase):
    def testDownloadAsTemporaryFileWorks(self):
        test_file = StringIO.StringIO('content')
        file_handle = DownloadAsTemporaryFile(test_file)
        assert file_handle.read() == 'content'
        file_handle.close()

    def testDownloadUrlAsTemporaryFileWorks(self):
        test_file = urllib2.urlopen('http://www.google.com')
        file_handle = DownloadAsTemporaryFile(test_file)
        assert file_handle.read(15) == '<!doctype html>'
        file_handle.close()
        
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

class GetUrlPriorityTest(unittest.TestCase):
    def testGetUrlPriorityWorks(self):
        assert GetUrlPriority('test.zip') == 1
        assert GetUrlPriority('test.blend') == 1
        assert GetUrlPriority('test.html') == 2

class IsBlenderFileTest(unittest.TestCase):
    def testIsBlenderFileWorks(self):
        blender_file = StringIO.StringIO('BLENDERrestofthefile')
        assert IsBlenderFile(blender_file)
        noblender_file = StringIO.StringIO('NOBLENDERrestofthefile')
        assert not IsBlenderFile(noblender_file)

    def testIsBlenderFileWorksWithFile(self):
        blender_file = open('test/data/sample.blend')
        assert IsBlenderFile(blender_file)
