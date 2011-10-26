#!/usr/bin/env python
"""crawl_helpers_test.py: Tests for crawl_helpers.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from crawl_helpers import CanFetchURL
from crawl_helpers import DownloadAsTemporaryFile
from crawl_helpers import FilterListBySuffix
from crawl_helpers import GenerateBlenderFilenameFromURL
from crawl_helpers import GetLinksFromHtml
from crawl_helpers import GetRobotParserForServer
from crawl_helpers import GetURLPriority
from crawl_helpers import IsBlenderFile

import StringIO
import mock
import testfixtures
import unittest
import urllib2

class CanFetchURLTest(unittest.TestCase):
    def testCanFetchURLWorks(self):
        robot_parser = mock.Mock()
        robot_parser.can_fetch = mock.Mock(return_value=True)
        with testfixtures.Replacer() as r:
            mock_get_robot_parser = mock.Mock(return_value=robot_parser)
            r.replace('common.crawl_helpers.GetRobotParserForServer',
                      mock_get_robot_parser)
            assert CanFetchURL('http://www.test.com/index.html')
            mock_get_robot_parser.assert_called_with('http://www.test.com')
            robot_parser.can_fetch.assert_called_with(
                '*', 'http://www.test.com/index.html')
            
    def testCanAlwaysFetchWithoutRobotParser(self):
        with testfixtures.Replacer() as r:
            mock_get_robot_parser = mock.Mock(return_value=None)
            r.replace('common.crawl_helpers.GetRobotParserForServer',
                      mock_get_robot_parser)
            assert CanFetchURL('http://www.test.com/index.html')
            mock_get_robot_parser.assert_called_with('http://www.test.com')

class DownloadAsTemporaryFileTest(unittest.TestCase):
    def testDownloadAsTemporaryFileWorks(self):
        test_file = StringIO.StringIO('content')
        file_handle = DownloadAsTemporaryFile(test_file)
        assert file_handle.read() == 'content'
        file_handle.close()

    def testDownloadURLAsTemporaryFileWorks(self):
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

class GenerateBlenderFilenameFromURLTest(unittest.TestCase):
    def testGenerateBlenderFileFromURLWorks(self):
        assert (
            GenerateBlenderFilenameFromURL('http://www.test.com/file.blend') ==
            'file512f6a50eeacf57e8756e06b969d0b52.blend'
            )
        assert (
            GenerateBlenderFilenameFromURL('http://www.test.com/folder/') ==
            'e1ff2a98cda50cf2995c851ade665a88.blend'
            )

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

class GetRobotParserForServerTest(unittest.TestCase):
    def testGetRobotParserForServerWorks(self):
        robot_parser = GetRobotParserForServer('http://www.google.com')
        assert robot_parser.can_fetch('*', 'http://www.google.com/index.html')

    def testGetRobotParserForServerCachesResults(self):
        robot_parser = GetRobotParserForServer('http://www.google.com')
        robot_parser = GetRobotParserForServer('http://www.google.com')
        robot_parser = GetRobotParserForServer('http://www.microsoft.com')
        assert GetRobotParserForServer.hits == 1
        assert GetRobotParserForServer.misses == 2

    def testGetRobotParserForServerHandlesIOError(self):
        def MockRaiseIOError():
            raise IOError('error')
        
        mock_robot_parser = mock.Mock()
        mock_robot_parser.set_url = mock.Mock()
        mock_robot_parser.read = MockRaiseIOError
        with testfixtures.Replacer() as r:
            r.replace('robotparser.RobotFileParser', mock.Mock(return_value=mock_robot_parser))
            assert GetRobotParserForServer('http://www.test.com') == None
            assert mock_robot_parser.set_url.called
            # TODO(brunonery): assert that logging was called.
        
class GetURLPriorityTest(unittest.TestCase):
    def testGetURLPriorityWorks(self):
        assert GetURLPriority('test.zip') == 1
        assert GetURLPriority('test.blend') == 1
        assert GetURLPriority('test.html') == 2

class IsBlenderFileTest(unittest.TestCase):
    def testIsBlenderFileWorks(self):
        blender_file = StringIO.StringIO('BLENDERrestofthefile')
        assert IsBlenderFile(blender_file)
        noblender_file = StringIO.StringIO('NOBLENDERrestofthefile')
        assert not IsBlenderFile(noblender_file)

    def testIsBlenderFileWorksWithFile(self):
        blender_file = open('test/data/sample.blend')
        assert IsBlenderFile(blender_file)
