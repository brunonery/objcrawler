#!/usr/bin/env python
"""crawler_thread_test.py: Tests for crawler_thread.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from crawler_thread import CrawlerThread
from models.visitable_url import VisitableURL
from models.visited_url import VisitedURL

import StringIO
import threading
import textwrap
import unittest

class CrawlerThreadTest(unittest.TestCase):
    def testPopVisitableURLWorks(self):
        # Create test database and lock.
        database_handler = DatabaseHandler('sqlite:///:memory:')
        database_handler.Init()
        visitable_url_lock = threading.Lock()
        # Populate the test database.
        session = database_handler.CreateSession()
        session.add(VisitableURL('http://www.microsoft.com/', 2))
        session.add(VisitableURL('http://www.google.com/', 1))
        session.commit()
         # Test pop.
        crawler_thread = CrawlerThread(
            database_handler, None, visitable_url_lock, None)
        the_url = crawler_thread.PopVisitableURL()
        assert the_url.url == 'http://www.google.com/'
        assert the_url.priority == 1
        # Test second pop.
        the_url = crawler_thread.PopVisitableURL()
        assert the_url.url == 'http://www.microsoft.com/'
        assert the_url.priority == 2
        # No more pops.
        the_url = crawler_thread.PopVisitableURL()
        assert the_url == None

    def testCheckURLAndMarkAsVisitedWorks(self):
        # Create test database and lock.
        database_handler = DatabaseHandler('sqlite:///:memory:')
        database_handler.Init()
        visited_url_lock = threading.Lock()
        # Populate the test database.
        session = database_handler.CreateSession()
        session.add(VisitedURL('http://www.microsoft.com/'))
        session.add(VisitedURL('http://www.google.com/'))
        session.commit()
         # Test check.
        crawler_thread = CrawlerThread(
            database_handler, None, None, visited_url_lock)
        assert crawler_thread.CheckURLAndMarkAsVisited('http://www.google.com/') 
        assert crawler_thread.CheckURLAndMarkAsVisited('http://www.microsoft.com/')
        assert not crawler_thread.CheckURLAndMarkAsVisited('http://www.facebook.com/')
        assert crawler_thread.CheckURLAndMarkAsVisited('http://www.facebook.com/')

    def testHandleHtmlResourceWorks(self):
        # Create test database and lock.
        database_handler = DatabaseHandler('sqlite:///:memory:')
        database_handler.Init()
        visitable_url_lock = threading.Lock()
        # Create test file.
        file_handle = StringIO.StringIO(textwrap.dedent("""
        <a href='http://www.google.com/'>Google</a>
        <a href='http://www.microsoft.com/'>Microsoft</a>
        <a href='links.html'>Links</a>
        """))
        file_handle.url = 'http://www.test.com'
         # Test handling of HTML resource.
        crawler_thread = CrawlerThread(
            database_handler, None, visitable_url_lock, None)
        crawler_thread.HandleHtmlResource(file_handle)
        session = database_handler.CreateSession()
        query = session.query(VisitableURL)
        assert query.filter(VisitableURL.url == 'http://www.google.com/').count() == 1
        assert query.filter(VisitableURL.url == 'http://www.microsoft.com/').count() == 1
        assert query.filter(VisitableURL.url == 'http://www.test.com/links.html').count() == 1
