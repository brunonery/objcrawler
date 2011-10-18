#!/usr/bin/env python
"""downloader_thread_test.py: Tests for downloader_thread.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from downloader_thread import DownloaderThread

import os
import unittest

class DownloaderThreadTest(unittest.TestCase):
    def testHandleZipResourceWorks(self):
        # Open Zip resource.
        file_handle = open('test/data/sample.zip')
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, 'test/tmp')
        downloader_thread.HandleZipResource(file_handle)
        assert os.path.exists('test/tmp/sample.blend')
        assert not os.path.exists('test/tmp/sample.txt')
