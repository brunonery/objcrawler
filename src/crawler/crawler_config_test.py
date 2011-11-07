#!/usr/bin/env python
"""crawler_config_test.py: Tests for crawler_config.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from crawler_config import CrawlerConfig

import StringIO
import textwrap
import unittest

class CrawlerConfigTest(unittest.TestCase):
    def testCrawlerConfigWorks(self):
        file_handle = StringIO.StringIO(textwrap.dedent("""
        [General]
        database_address: my_database_address
        download_folder: my_download_folder
        zip_size_limit: 30000
        """))
        config = CrawlerConfig(file_handle)
        self.assertEqual('my_database_address', config.database_address())
        self.assertEqual('my_download_folder', config.download_folder())
        self.assertEqual(30000, config.zip_size_limit())
