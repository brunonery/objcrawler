#!/usr/bin/env python
"""crawler_thread.py: Implementation of the CrawlerThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import CanFetchURL
from common.crawl_helpers import GetLinksFromHtml
from common.crawl_helpers import GetURLPriority
from models.url import URL

import httplib
import logging
import threading
import urllib2
import urlparse

class CrawlerThread(threading.Thread):
    def __init__(self,
                 database_handler,
                 download_queue,
                 url_lock):
        """Builds a CrawlerThread instance.

        Arguments:
        database_handler -- the database to connect to.
        url_lock -- the thread lock for the urls table.
        """
        threading.Thread.__init__(self)
        self.database_handler_ = database_handler
        self.download_queue_ = download_queue
        self.url_lock_ = url_lock

    def run(self):
        while True:
            next_url = self.PopNextURLAndMarkAsVisited()
            # No more URLs to be visited.
            if next_url is None:
                break
            self.HandleURL(next_url)
        # Wait for all remaining items to be processed.
        self.download_queue_.join()

    def PopNextURLAndMarkAsVisited(self):
        """Get the next URL to be visited and mark it as visited.
        
        Returns:
        A URL address containing the URL with the highest priority and the
        biggest link_to count. None if there are no more URLs in the database.
        """
        self.url_lock_.acquire()
        try:
            session = self.database_handler_.CreateSession()
            query = session.query(URL)
            results = query.filter(URL.visited == False).order_by(
                URL.priority, URL.links_to.desc())
            url_record = results.first()
            if url_record:
                url_record.visited = True
                the_url = url_record.url
                session.commit()
            else:
                the_url = None
        finally:
            self.url_lock_.release()
        return the_url

    def HandleURL(self, url):
        """Obtain URL resource and handle it according to type.

        Arguments:
        url -- the URL of the resource to be processed.
        """
        # Avoid fetching URLs not allowed by a robots.txt file.
        # TODO(brunonery): find a way of encode('utf-8') automagically.
        if not CanFetchURL(url.encode('utf-8')):
            return
        try:
            resource = urllib2.urlopen(url.encode('utf-8'))
        except urllib2.URLError as url_error:
            logging.warning('Problem opening %s (%s).', url, url_error)
            return
        except httplib.BadStatusLine:
            logging.warning('Bad status line in %s.', url)
            return
        if not 'content-type' in resource.headers:
            return
        content_type = resource.headers['content-type']
        if content_type.startswith('text/html'):
            self.HandleHtmlResource(resource)
        elif content_type.startswith('application/zip'):
            self.download_queue_.put(resource)
        elif content_type.startswith('text/plain'):
            self.download_queue_.put(resource)

    def HandleHtmlResource(self, resource):
        """Extract links from HTML resource and add them to the database.

        Arguments:
        base_url -- the HTML resource URL.
        resource -- the HTML resource to be processed.
        """
        link_list = GetLinksFromHtml(resource)
        resource.close()
        self.url_lock_.acquire()
        session = self.database_handler_.CreateSession()
        for link in link_list:
            new_url = URL(urlparse.urljoin(resource.url, link),
                          GetURLPriority(link))
            if not new_url.url.startswith('http'):
                continue
            query = session.query(URL)
            result = query.filter(URL.url_md5 == new_url.url_md5)
            if result.count() == 0:
                session.add(new_url)
            else:
                the_url = result.first()
                the_url.links_to += 1
        session.commit()
        self.url_lock_.release()
