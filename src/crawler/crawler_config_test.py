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
        """))
        config = CrawlerConfig(file_handle)
        assert config.database_address() == 'my_database_address'
