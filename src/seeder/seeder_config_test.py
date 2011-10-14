#!/usr/bin/env python
"""seeder_config_test.py: Tests for seeder_config.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import StringIO
import textwrap
import unittest

from seeder_config import SeederConfig

class SeederConfigTest(unittest.TestCase):
    def testSeederConfigWorks(self):
        file_handle = StringIO.StringIO(textwrap.dedent("""
        [General]
        database_address: my_database_address
        
        [Google]
        developer_key: my_developer_key
        cref: my_cref
        """))
        config = SeederConfig(file_handle)
        assert config.database_address() == 'my_database_address'
        assert config.google_developer_key() == 'my_developer_key'
        assert config.google_cref() == 'my_cref'
