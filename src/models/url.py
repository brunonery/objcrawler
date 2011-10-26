#!/usr/bin/env python
"""url.py: Contains the URL database model."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from model_base import Base

import md5
import sqlalchemy

class URL(Base):
    """Database model representing a URL."""
    __tablename__ = 'urls'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    url = sqlalchemy.Column(sqlalchemy.String)
    url_md5 = sqlalchemy.Column(sqlalchemy.Binary(16), index=True)
    visited = sqlalchemy.Column(sqlalchemy.Boolean, index=True)
    priority = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    links_to = sqlalchemy.Column(sqlalchemy.Integer, index=True)

    def __init__(self, url, priority):
        """Creates a URL instance.

        Arguments:
        url -- the URL address.
        priority -- an integer representing the priority (small numbers should
        be visited first).
        """
        self.url = url
        m = md5.new()
        m.update(url.encode('utf-8'))
        self.url_md5 = m.digest()
        self.visited = False
        self.priority = priority
        # Each new URL starts with one link to it.
        self.links_to = 1
