#!/usr/bin/env python
"""visited_url.py: Contains the VisitedURL database model."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from model_base import Base

import md5
import sqlalchemy


class VisitedURL(Base):
    """Database model representing an already visited URL."""
    __tablename__ = 'visited_urls'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    url_md5 = sqlalchemy.Column(sqlalchemy.Binary(16))

    def __init__(self, url):
        """Creates a VisitedURL instance.

        Arguments:
        url -- the URL to be visited.
        """
        m = md5.new()
        print url
        m.update(url.encode('utf-8'))
        self.url_md5 = m.digest()
