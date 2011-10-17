#!/usr/bin/env python
"""crawler_thread.py: Implementation of the CrawlerThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import GetLinksFromHtml
from models.visitable_url import VisitableURL
from models.visited_url import VisitedURL

import threading

class CrawlerThread(threading.Thread):
    def __init__(self, database_handler, visitable_url_lock, visited_url_lock):
        """Builds a CrawlerThread instance.

        Arguments:
        database_handler -- the database to connect to.
        visitable_url_lock -- the thread lock for the visitable_urls table.
        visited_url_lock -- the thread lock for the visited_urls table.
        """
        threading.Thread.__init__(self)
        self.database_handler_ = database_handler
        self.visitable_url_lock_ = visitable_url_lock
        self.visited_url_lock_ = visited_url_lock

    def run(self):
        while True:
            next_url = self.PopVisitableURL()
            # No more URLs to be visited.
            if not next_url:
                break
            # Avoid visiting an URL more than once.
            if self.CheckURLAndMarkAsVisited(next_url.url):
                continue
            self.HandleURL(next_url.url)

    def PopVisitableURL(self):
        """Pop the highest priority URL from visitable_urls table.
        
        Returns:
        A VisitableURL instance containing the highest priority URL. None if the
        table is empty.
        """
        self.visitable_url_lock_.acquire()
        session = self.database_handler_.CreateSession()
        query = session.query(VisitableURL).order_by(VisitableURL.priority)
        the_url = query.first()
        if the_url:
            session.delete(the_url)
            session.commit()
        self.visitable_url_lock_.release()
        return the_url

    def CheckURLAndMarkAsVisited(self, url):
        """Check if the URL has already been visited and mark it as visited.

        Arguments:
        url -- the URL to be checked.
        
        Returns:
        True if the URL was already visited. False otherwise.
        """
        self.visited_url_lock_.acquire()
        the_url = VisitedURL(url)
        session = self.database_handler_.CreateSession()
        query = session.query(VisitedURL)
        result = query.filter(VisitedURL.url_md5 == the_url.url_md5)
        if result.count() == 0:
            url_is_visited = False
            session.add(the_url)
            session.commit()
        else:
            url_is_visited = True
        self.visited_url_lock_.release()
        return url_is_visited

    def HandleURL(self, url):
        """Obtain URL resource and handle it according to type.

        Arguments:
        url -- the URL of the resource to be processed.
        """
        resource = urllib2.open(url)
        if not 'content-type' in resource.headers:
            return
        content_type = resource.headers['content-type']
        if content_type.startswith('text/html'):
            self.HandleHTMLResource(resource)
        # elif content_type.startswith('application/zip'):
        #     self.HandleZIPResource(resource)
        # elif content_type.startswith('text/plain'):
        #     self.HandleBlenderResource(resource)
        resource.close()

    def HandleHtmlResource(self, resource):
        """Extract links from HTML resource and add them to the database.

        Arguments:
        resource -- the HTML resource to be processed.
        """
        link_list = GetLinksFromHtml(resource)
        self.visitable_url_lock_.acquire()
        session = self.database_handler_.CreateSession()
        for i in range(len(link_list)):
            session.add(VisitableURL(link_list[i], i))
        session.commit()
        self.visitable_url_lock_.release()
