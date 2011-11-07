#!/usr/bin/env python
"""seeder_config_test.py: Tests for seeder_config.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from seeder_config import SeederConfig

import StringIO
import textwrap
import unittest

class SeederConfigTest(unittest.TestCase):
    def test_seeder_config_works(self):
        file_handle = StringIO.StringIO(textwrap.dedent("""
        [General]
        database_address: my_database_address
        
        [Google]
        developer_key: my_developer_key
        cref: my_cref
        """))
        config = SeederConfig(file_handle)
        self.assertEqual('my_database_address', config.database_address())
        self.assertEqual('my_developer_key', config.google_developer_key())
        self.assertEqual('my_cref', config.google_cref())
