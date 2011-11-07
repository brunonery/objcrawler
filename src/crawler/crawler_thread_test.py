#!/usr/bin/env python
"""crawler_thread_test.py: Tests for crawler_thread.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from crawler_thread import CrawlerThread
from models.url import URL

import collections
import functools
import httplib
import mock
import Queue
import StringIO
import threading
import testfixtures
import textwrap
import unittest
import urllib2

def mock_url_open_with_exception(exception, url):
    """Mock for urllib2.urlopen that throws an exception.

    Throws the specified exception when called. Should be built using
    functools.partial.
    """
    if exception == 'BadStatusLine':
        raise httplib.BadStatusLine('')
    elif exception == 'URLError':
        raise urllib2.URLError('')

def create_fake_url_resource(type):
    URLResource = collections.namedtuple('URLResource', ['headers'])
    resource = URLResource(headers={'content-type': type})
    return resource

class CrawlerThreadTest(unittest.TestCase):
    def setUp(self):
        # Create test database and lock.
        self.database_handler = DatabaseHandler('sqlite:///:memory:')
        self.database_handler.init()
        self.url_lock = threading.Lock()
        
    def test_pop_next_url_and_mark_as_visited_works(self):
        # Populate the test database.
        session = self.database_handler.create_session()
        session.add(URL('http://www.microsoft.com/', 2))
        session.add(URL('http://www.google.com/', 1))
        session.commit()
         # Test pop.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        the_url = crawler_thread.pop_next_url_and_mark_as_visited()
        self.assertEqual('http://www.google.com/', the_url)
        # Test second pop.
        the_url = crawler_thread.pop_next_url_and_mark_as_visited()
        self.assertEqual('http://www.microsoft.com/', the_url)
        # No more pops.
        the_url = crawler_thread.pop_next_url_and_mark_as_visited()
        self.assertEqual(None, the_url)

    def test_pop_next_url_and_mark_as_visited_handles_count(self):
        # Populate the test database.
        session = self.database_handler.create_session()
        the_url = URL('http://www.microsoft.com/', 1)
        the_url.links_to = 500
        session.add(the_url)
        the_url = URL('http://www.google.com/', 1)
        the_url.links_to = 1000
        session.add(the_url)
        session.commit()
         # Test pop.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        the_url = crawler_thread.pop_next_url_and_mark_as_visited()
        self.assertEqual('http://www.google.com/', the_url)
        # Test second pop.
        the_url = crawler_thread.pop_next_url_and_mark_as_visited()
        self.assertEqual('http://www.microsoft.com/', the_url)

    def test_handle_url_works(self):
        mock_download_queue = mock.Mock(Queue.Queue)
        crawler_thread = CrawlerThread(None, mock_download_queue, None)
        crawler_thread.handle_html_resource = mock.Mock()
        with testfixtures.Replacer() as r:
            # HTML resource.
            html_resource = create_fake_url_resource('text/html')
            r.replace('urllib2.urlopen', mock.Mock(return_value=html_resource))
            crawler_thread.handle_url('http://www.fake.com/')
            crawler_thread.handle_html_resource.assert_called_with(html_resource)
            # Zip resource.
            zip_resource = create_fake_url_resource('application/zip')
            r.replace('urllib2.urlopen', mock.Mock(return_value=zip_resource))
            crawler_thread.handle_url('http://www.fake.com/')
            mock_download_queue.put.assert_called_with(zip_resource)
            # Plain text resource.
            text_resource = create_fake_url_resource('text/plain')
            r.replace('urllib2.urlopen', mock.Mock(return_value=text_resource))
            crawler_thread.handle_url('http://www.fake.com/')
            mock_download_queue.put.assert_called_with(text_resource)

    def test_handle_url_ignores_bad_status_line(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            r.replace('urllib2.urlopen',
                      functools.partial(mock_url_open_with_exception,
                                        'BadStatusLine'))
            crawler_thread.handle_url('http://www.fake.com/')

    def test_handle_url_ignores_url_error(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            r.replace('urllib2.urlopen',
                      functools.partial(mock_url_open_with_exception,
                                        'URLError'))
            crawler_thread.handle_url('http://www.fake.com/')

    def test_handle_url_ignores_non_fetchable_url(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            mock_url_open = mock.Mock()
            r.replace('urllib2.urlopen', mock_url_open)
            mock_can_fetch_url = mock.Mock(return_value=False)
            r.replace('crawler.crawler_thread.can_fetch_url', mock_can_fetch_url)
            crawler_thread.handle_url('http://www.fake.com/')
            self.assertTrue(mock_can_fetch_url.called)
            self.assertFalse(mock_url_open.called)

    def test_handle_url_with_xea_works(self):
        crawler_thread = CrawlerThread(None, None, None)
        crawler_thread.handle_url(u'http://\xea')
        # TODO(brunonery): add assert for logging.

    def test_handle_html_resource_works(self):
        # Create test file.
        file_handle = StringIO.StringIO(textwrap.dedent("""
        <a href='HTTP://www.google.com/'>Google</a>
        <a href='http://www.microsoft.com/'>Microsoft</a>
        <a href='links.html'>Links</a>
        """))
        file_handle.url = 'http://www.test.com'
         # Test handling of HTML resource.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        crawler_thread.handle_html_resource(file_handle)
        session = self.database_handler.create_session()
        query = session.query(URL)
        self.assertEqual(1, query.filter(URL.url == 'http://www.google.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.microsoft.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.test.com/links.html').count())

    def test_handle_html_resource_increment_links_to(self):
        # Populate the test database.
        session = self.database_handler.create_session()
        the_url = URL('http://www.google.com/', 1)
        the_url.links_to = 1000
        session.add(the_url)
        session.commit()
        # Create test file.
        file_handle = StringIO.StringIO(textwrap.dedent("""
        <a href='http://www.google.com/'>Google</a>
        """))
        file_handle.url = 'http://www.test.com'
        # Test handling of HTML resource.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        crawler_thread.handle_html_resource(file_handle)
        query = session.query(URL)
        results = query.filter(URL.url == 'http://www.google.com/')
        self.assertEqual(1, results.count())
        the_url = results.first()
        self.assertEqual(1001, the_url.links_to)

    def test_handle_html_ignores_non_http(self):
        # Create test file.
        file_handle = StringIO.StringIO(textwrap.dedent("""
        <a href='http://www.google.com/'>Google</a>
        <a href='ftp://ftp.microsoft.com/'>Microsoft</a>
        <a href='links.html'>Links</a>
        """))
        file_handle.url = 'http://www.test.com'
         # Test handling of HTML resource.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        crawler_thread.handle_html_resource(file_handle)
        session = self.database_handler.create_session()
        query = session.query(URL)
        self.assertEqual(1, query.filter(URL.url == 'http://www.google.com/').count())
        self.assertEqual(0, query.filter(URL.url == 'ftp://ftp.microsoft.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.test.com/links.html').count())
