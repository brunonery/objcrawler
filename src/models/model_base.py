#!/usr/bin/env python
"""model_base.py: Contains the Base class for all database models."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()
