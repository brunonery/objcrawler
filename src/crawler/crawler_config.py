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
        self.download_folder_ = config.get('General', 'download_folder')
        self.zip_size_limit_ = config.getint('General', 'zip_size_limit')

    def database_address(self):
        return self.database_address_

    def download_folder(self):
        return self.download_folder_

    def zip_size_limit(self):
        return self.zip_size_limit_
