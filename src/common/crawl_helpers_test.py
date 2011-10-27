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
            self.assertTrue(CanFetchURL('http://www.test.com/index.html'))
            mock_get_robot_parser.assert_called_with('http://www.test.com')
            robot_parser.can_fetch.assert_called_with(
                '*', 'http://www.test.com/index.html')
            
    def testCanAlwaysFetchWithoutRobotParser(self):
        with testfixtures.Replacer() as r:
            mock_get_robot_parser = mock.Mock(return_value=None)
            r.replace('common.crawl_helpers.GetRobotParserForServer',
                      mock_get_robot_parser)
            self.assertTrue(CanFetchURL('http://www.test.com/index.html'))
            mock_get_robot_parser.assert_called_with('http://www.test.com')

class DownloadAsTemporaryFileTest(unittest.TestCase):
    def testDownloadAsTemporaryFileWorks(self):
        test_file = StringIO.StringIO('content')
        file_handle = DownloadAsTemporaryFile(test_file)
        self.assertEqual('content', file_handle.read())
        file_handle.close()

    def testDownloadURLAsTemporaryFileWorks(self):
        test_file = urllib2.urlopen('http://www.google.com')
        file_handle = DownloadAsTemporaryFile(test_file)
        self.assertEqual('<!doctype html>', file_handle.read(15))
        file_handle.close()
        
class FilterListBySuffixTest(unittest.TestCase):
    def setUp(self):
        self.items = ['string1.suffix1',
                      'string2.suffix1',
                      'string3.suffix2',
                      'string4.suffix3']
        
    def testFilterListBySuffixWorks(self):
        new_list = FilterListBySuffix(self.items, '.suffix1')
        self.assertIn('string1.suffix1', new_list)
        self.assertIn('string2.suffix1', new_list)
        self.assertNotIn('string3.suffix2', new_list)
        self.assertNotIn('string4.suffix3', new_list)

class GenerateBlenderFilenameFromURLTest(unittest.TestCase):
    def testGenerateBlenderFileFromURLWorks(self):
        self.assertEqual(
            'file512f6a50eeacf57e8756e06b969d0b52.blend',
            GenerateBlenderFilenameFromURL('http://www.test.com/file.blend')
            )
        self.assertEqual(
            'e1ff2a98cda50cf2995c851ade665a88.blend',
            GenerateBlenderFilenameFromURL('http://www.test.com/folder/')
            )

class GetLinksFromHtmlTest(unittest.TestCase):
    def testGetLinksFromHtmlWorks(self):
        file_handle = StringIO.StringIO('<a href="http://www.test.com">t</a>')
        link_list = GetLinksFromHtml(file_handle)
        self.assertIn('http://www.test.com', link_list)

    def testEmptyLinkIsIgnored(self):
        file_handle = StringIO.StringIO('<a href=></a><a href=""></a>')
        link_list = GetLinksFromHtml(file_handle)
        self.assertEqual(0, len(list(link_list)))

    def testSectionLinksAreIgnored(self):
        file_handle = StringIO.StringIO('<a href="#section">s</a>')
        link_list = GetLinksFromHtml(file_handle)
        self.assertEqual(0, len(list(link_list)))

    def testSectionMarksAreIgnored(self):
        file_handle = StringIO.StringIO('<a name="section"/>')
        link_list = GetLinksFromHtml(file_handle)
        self.assertEqual(0, len(list(link_list)))

class GetRobotParserForServerTest(unittest.TestCase):
    def testGetRobotParserForServerWorks(self):
        robot_parser = GetRobotParserForServer('http://www.google.com')
        self.assertTrue(robot_parser.can_fetch('*', 'http://www.google.com/index.html'))

    def testGetRobotParserForServerCachesResults(self):
        robot_parser = GetRobotParserForServer('http://www.google.com')
        robot_parser = GetRobotParserForServer('http://www.google.com')
        robot_parser = GetRobotParserForServer('http://www.microsoft.com')
        self.assertEqual(1, GetRobotParserForServer.hits)
        self.assertEqual(2, GetRobotParserForServer.misses)

    def testGetRobotParserForServerHandlesIOError(self):
        def MockRaiseIOError():
            raise IOError('error')
        
        mock_robot_parser = mock.Mock()
        mock_robot_parser.set_url = mock.Mock()
        mock_robot_parser.read = MockRaiseIOError
        with testfixtures.Replacer() as r:
            r.replace('robotparser.RobotFileParser', mock.Mock(return_value=mock_robot_parser))
            self.assertEqual(None, GetRobotParserForServer('http://www.test.com'))
            self.assertTrue(mock_robot_parser.set_url.called)
            # TODO(brunonery): assert that logging was called.
        
class GetURLPriorityTest(unittest.TestCase):
    def testGetURLPriorityWorks(self):
        self.assertEqual(1, GetURLPriority('test.zip'))
        self.assertEqual(1, GetURLPriority('test.blend'))
        self.assertEqual(2, GetURLPriority('test.html'))

class IsBlenderFileTest(unittest.TestCase):
    def testIsBlenderFileWorks(self):
        blender_file = StringIO.StringIO('BLENDERrestofthefile')
        self.assertTrue(IsBlenderFile(blender_file))
        noblender_file = StringIO.StringIO('NOBLENDERrestofthefile')
        self.assertFalse(IsBlenderFile(noblender_file))

    def testIsBlenderFileWorksWithFile(self):
        blender_file = open('test/data/sample.blend')
        self.assertTrue(IsBlenderFile(blender_file))
