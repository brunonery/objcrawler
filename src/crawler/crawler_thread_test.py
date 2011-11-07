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

def MockURLOpenWithException(exception, url):
    """Mock for urllib2.urlopen that throws an exception.

    Throws the specified exception when called. Should be built using
    functools.partial.
    """
    if exception == 'BadStatusLine':
        raise httplib.BadStatusLine('')
    elif exception == 'URLError':
        raise urllib2.URLError('')

def CreateFakeURLResource(type):
    URLResource = collections.namedtuple('URLResource', ['headers'])
    resource = URLResource(headers={'content-type': type})
    return resource

class CrawlerThreadTest(unittest.TestCase):
    def setUp(self):
        # Create test database and lock.
        self.database_handler = DatabaseHandler('sqlite:///:memory:')
        self.database_handler.init()
        self.url_lock = threading.Lock()
        
    def testPopNextURLAndMarkAsVisited(self):
        # Populate the test database.
        session = self.database_handler.create_session()
        session.add(URL('http://www.microsoft.com/', 2))
        session.add(URL('http://www.google.com/', 1))
        session.commit()
         # Test pop.
        crawler_thread = CrawlerThread(
            self.database_handler, None, self.url_lock)
        the_url = crawler_thread.PopNextURLAndMarkAsVisited()
        self.assertEqual('http://www.google.com/', the_url)
        # Test second pop.
        the_url = crawler_thread.PopNextURLAndMarkAsVisited()
        self.assertEqual('http://www.microsoft.com/', the_url)
        # No more pops.
        the_url = crawler_thread.PopNextURLAndMarkAsVisited()
        self.assertEqual(None, the_url)

    def testPopNextURLAndMarkAsVisitedHandlesCount(self):
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
        the_url = crawler_thread.PopNextURLAndMarkAsVisited()
        self.assertEqual('http://www.google.com/', the_url)
        # Test second pop.
        the_url = crawler_thread.PopNextURLAndMarkAsVisited()
        self.assertEqual('http://www.microsoft.com/', the_url)

    def testHandleURLWorks(self):
        mock_download_queue = mock.Mock(Queue.Queue)
        crawler_thread = CrawlerThread(None, mock_download_queue, None)
        crawler_thread.HandleHtmlResource = mock.Mock()
        with testfixtures.Replacer() as r:
            # HTML resource.
            html_resource = CreateFakeURLResource('text/html')
            r.replace('urllib2.urlopen', mock.Mock(return_value=html_resource))
            crawler_thread.HandleURL('http://www.fake.com/')
            crawler_thread.HandleHtmlResource.assert_called_with(html_resource)
            # Zip resource.
            zip_resource = CreateFakeURLResource('application/zip')
            r.replace('urllib2.urlopen', mock.Mock(return_value=zip_resource))
            crawler_thread.HandleURL('http://www.fake.com/')
            mock_download_queue.put.assert_called_with(zip_resource)
            # Plain text resource.
            text_resource = CreateFakeURLResource('text/plain')
            r.replace('urllib2.urlopen', mock.Mock(return_value=text_resource))
            crawler_thread.HandleURL('http://www.fake.com/')
            mock_download_queue.put.assert_called_with(text_resource)

    def testHandleURLIgnoreBadStatusLine(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            r.replace('urllib2.urlopen',
                      functools.partial(MockURLOpenWithException,
                                        'BadStatusLine'))
            crawler_thread.HandleURL('http://www.fake.com/')

    def testHandleURLIgnoreURLError(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            r.replace('urllib2.urlopen',
                      functools.partial(MockURLOpenWithException,
                                        'URLError'))
            crawler_thread.HandleURL('http://www.fake.com/')

    def testHandleURLIgnoreNonFetchableURL(self):
        crawler_thread = CrawlerThread(None, None, None)
        with testfixtures.Replacer() as r:
            mock_url_open = mock.Mock()
            r.replace('urllib2.urlopen', mock_url_open)
            mock_can_fetch_url = mock.Mock(return_value=False)
            r.replace('crawler.crawler_thread.can_fetch_url', mock_can_fetch_url)
            crawler_thread.HandleURL('http://www.fake.com/')
            self.assertTrue(mock_can_fetch_url.called)
            self.assertFalse(mock_url_open.called)

    def testHandleURLWithXeaWorks(self):
        crawler_thread = CrawlerThread(None, None, None)
        crawler_thread.HandleURL(u'http://\xea')
        # TODO(brunonery): add assert for logging.

    def testHandleHtmlResourceWorks(self):
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
        crawler_thread.HandleHtmlResource(file_handle)
        session = self.database_handler.create_session()
        query = session.query(URL)
        self.assertEqual(1, query.filter(URL.url == 'http://www.google.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.microsoft.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.test.com/links.html').count())

    def testHandleHtmlResourceIncrementsLinksTo(self):
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
        crawler_thread.HandleHtmlResource(file_handle)
        query = session.query(URL)
        results = query.filter(URL.url == 'http://www.google.com/')
        self.assertEqual(1, results.count())
        the_url = results.first()
        self.assertEqual(1001, the_url.links_to)

    def testHandleHtmlResourceIgnoresNonHttp(self):
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
        crawler_thread.HandleHtmlResource(file_handle)
        session = self.database_handler.create_session()
        query = session.query(URL)
        self.assertEqual(1, query.filter(URL.url == 'http://www.google.com/').count())
        self.assertEqual(0, query.filter(URL.url == 'ftp://ftp.microsoft.com/').count())
        self.assertEqual(1, query.filter(URL.url == 'http://www.test.com/links.html').count())
