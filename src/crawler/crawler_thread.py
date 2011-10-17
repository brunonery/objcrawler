#!/usr/bin/env python
"""crawler_thread.py: Implementation of the CrawlerThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from models.visitable_url import VisitableURL

import threading

class CrawlerThread(threading.Thread):
    def __init__(self, database_handler, visitable_url_lock):
        """Builds a CrawlerThread instance.

        Arguments:
        database_handler -- the database to connect to.
        visitable_url_lock -- the thread lock for the visitable_urls table.
        """
        threading.Thread.__init__(self)
        self.database_handler_ = database_handler
        self.visitable_url_lock_ = visitable_url_lock

    def run(self):
        pass

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
