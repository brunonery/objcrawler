#!/usr/bin/env python
"""crawler_config.py: Config helper for the crawler binary."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import ConfigParser

class CrawlerConfig():
    """Contains the configuration for the crawler binary."""
    def __init__(self, file_handle):
        """Builds a CrawlerConfig instance from a file."""
        config = ConfigParser.ConfigParser()
        config.readfp(file_handle)
        self.database_address_ = config.get('General', 'database_address')

    def database_address(self):
        return self.database_address_
