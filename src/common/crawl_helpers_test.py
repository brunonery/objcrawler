#!/usr/bin/env python
"""crawl_helpers_test.py: Tests for crawl_helpers.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from crawl_helpers import can_fetch_url
from crawl_helpers import download_as_temporary_file
from crawl_helpers import filter_list_by_suffix
from crawl_helpers import generate_blender_filename_from_url
from crawl_helpers import get_links_from_html
from crawl_helpers import get_robot_parser_for_server
from crawl_helpers import get_url_priority
from crawl_helpers import is_blender_file

import io
import StringIO
import mock
import testfixtures
import unittest
import urllib2

class CanFetchURLTest(unittest.TestCase):
    def test_can_fetch_url_works(self):
        robot_parser = mock.Mock()
        robot_parser.can_fetch = mock.Mock(return_value=True)
        with testfixtures.Replacer() as r:
            mock_get_robot_parser = mock.Mock(return_value=robot_parser)
            r.replace('common.crawl_helpers.get_robot_parser_for_server',
                      mock_get_robot_parser)
            self.assertTrue(can_fetch_url('http://www.test.com/index.html'))
            mock_get_robot_parser.assert_called_with('http://www.test.com')
            robot_parser.can_fetch.assert_called_with(
                '*', 'http://www.test.com/index.html')
            
    def test_can_always_fetch_without_robot_parser(self):
        with testfixtures.Replacer() as r:
            mock_get_robot_parser = mock.Mock(return_value=None)
            r.replace('common.crawl_helpers.get_robot_parser_for_server',
                      mock_get_robot_parser)
            self.assertTrue(can_fetch_url('http://www.test.com/index.html'))
            mock_get_robot_parser.assert_called_with('http://www.test.com')

class DownloadAsTemporaryFileTest(unittest.TestCase):
    def test_download_as_temporary_file_works(self):
        test_file = StringIO.StringIO('content')
        with download_as_temporary_file(test_file) as file_handle:
            self.assertEqual('content', file_handle.read())

    def test_download_url_as_temporary_file_works(self):
        test_file = urllib2.urlopen('http://www.google.com')
        with download_as_temporary_file(test_file) as file_handle:
            self.assertEqual('<!doctype html>', file_handle.read(15))
        
class FilterListBySuffixTest(unittest.TestCase):
    def setUp(self):
        self.items = ['string1.suffix1',
                      'string2.suffix1',
                      'string3.suffix2',
                      'string4.suffix3']
        
    def test_filter_list_by_suffix_works(self):
        new_list = filter_list_by_suffix(self.items, '.suffix1')
        self.assertIn('string1.suffix1', new_list)
        self.assertIn('string2.suffix1', new_list)
        self.assertNotIn('string3.suffix2', new_list)
        self.assertNotIn('string4.suffix3', new_list)

class GenerateBlenderFilenameFromURLTest(unittest.TestCase):
    def test_generate_blender_filename_from_url_works(self):
        self.assertEqual(
            'file512f6a50eeacf57e8756e06b969d0b52.blend',
            generate_blender_filename_from_url('http://www.test.com/file.blend')
            )
        self.assertEqual(
            'e1ff2a98cda50cf2995c851ade665a88.blend',
            generate_blender_filename_from_url('http://www.test.com/folder/')
            )

class GetLinksFromHtmlTest(unittest.TestCase):
    def test_get_links_from_html_works(self):
        file_handle = StringIO.StringIO('<a href="http://www.test.com">t</a>')
        link_list = get_links_from_html(file_handle)
        self.assertIn('http://www.test.com', link_list)

    def test_empty_link_is_ignored(self):
        file_handle = StringIO.StringIO('<a href=></a><a href=""></a>')
        link_list = get_links_from_html(file_handle)
        self.assertEqual(0, len(list(link_list)))

    def test_section_links_are_ignored(self):
        file_handle = StringIO.StringIO('<a href="#section">s</a>')
        link_list = get_links_from_html(file_handle)
        self.assertEqual(0, len(list(link_list)))

    def test_section_marks_are_ignored(self):
        file_handle = StringIO.StringIO('<a name="section"/>')
        link_list = get_links_from_html(file_handle)
        self.assertEqual(0, len(list(link_list)))

    def test_beautiful_soup_bug_worked_around(self):
        with open('test/data/bs_bug.html') as original_file:
            file_handle = StringIO.StringIO(original_file.read())
            file_handle.url = 'bs_bug.html'
            link_list = get_links_from_html(file_handle)
        self.assertEqual(0, len(list(link_list)))

class GetRobotParserForServerTest(unittest.TestCase):
    def test_get_robot_parser_for_server_works(self):
        robot_parser = get_robot_parser_for_server('http://www.google.com')
        self.assertTrue(robot_parser.can_fetch('*', 'http://www.google.com/index.html'))

    def test_get_robot_parser_for_server_caches_results(self):
        robot_parser = get_robot_parser_for_server('http://www.google.com')
        robot_parser = get_robot_parser_for_server('http://www.google.com')
        robot_parser = get_robot_parser_for_server('http://www.microsoft.com')
        self.assertEqual(1, get_robot_parser_for_server.hits)
        self.assertEqual(2, get_robot_parser_for_server.misses)

    def test_get_robot_parser_for_server_handles_io_error(self):
        def mock_raise_io_error():
            raise IOError('error')
        
        mock_robot_parser = mock.Mock()
        mock_robot_parser.set_url = mock.Mock()
        mock_robot_parser.read = mock_raise_io_error
        with testfixtures.Replacer() as r:
            r.replace('robotparser.RobotFileParser', mock.Mock(return_value=mock_robot_parser))
            self.assertEqual(None, get_robot_parser_for_server('http://www.test.com'))
            self.assertTrue(mock_robot_parser.set_url.called)
            # TODO(brunonery): assert that logging was called.
        
class GetURLPriorityTest(unittest.TestCase):
    def test_get_url_priority_works(self):
        self.assertEqual(1, get_url_priority('test.zip'))
        self.assertEqual(1, get_url_priority('test.blend'))
        self.assertEqual(2, get_url_priority('test.html'))

class IsBlenderFileTest(unittest.TestCase):
    def test_is_blender_file_works(self):
        blender_file = StringIO.StringIO('BLENDERrestofthefile')
        self.assertTrue(is_blender_file(blender_file))
        noblender_file = StringIO.StringIO('NOBLENDERrestofthefile')
        self.assertFalse(is_blender_file(noblender_file))

    def test_is_blender_file_works_with_file(self):
        blender_file = open('test/data/sample.blend')
        self.assertTrue(is_blender_file(blender_file))
