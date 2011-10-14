#!/usr/bin/env python
"""seeder_config.py: Config helper for the seeder binary."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import ConfigParser

class SeederConfig():
    """Contains the configuration for the seeder binary."""
    def __init__(self, file_handle):
        """Builds a SeederConfig instance from a file."""
        config = ConfigParser.ConfigParser()
        config.readfp(file_handle)
        self.google_developer_key_ = config.get('Google', 'developer_key')
        self.google_cref_ = config.get('Google', 'cref')

    def google_developer_key(self):
        return self.google_developer_key_

    def google_cref(self):
        return self.google_cref_
