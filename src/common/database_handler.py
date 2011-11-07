#!/usr/bin/env python
"""database_handler.py: Contains the DatabaseHandler class."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from models.model_base import Base

import sqlalchemy
import sqlalchemy.orm

class DatabaseHandler():
    """Proxy class to access databases."""
    def __init__(self, database_address):
        """Creates a DatabaseHandler instance.

        Arguments:
        database_address -- the address of the database to be accessed.
        """
        self.engine_ = sqlalchemy.create_engine(database_address)
        self.session_maker_ = sqlalchemy.orm.sessionmaker(bind=self.engine_)

    def Init(self):
        # Create all tables that don't exist.
        Base.metadata.create_all(self.engine_)

    def CreateSession(self):
        return self.session_maker_()
