#!/usr/bin/env python
"""downloader_thread_test.py: Tests for downloader_thread.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from downloader_thread import DownloaderThread

import io
import os
import StringIO
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

    def testHandleZipResourceIgnoresNonZipFiles(self):
        # Create non-Zip resource.
        file_handle = StringIO.StringIO('nozipfile')
        file_handle.url = 'nozipfile.zip'
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, None)
        downloader_thread.HandleZipResource(file_handle)

    def testHandleZipResourceIgnoresFaultyZipFiles(self):
        # Open Zip resource.
        file_handle = io.open('test/data/faulty.zip', 'rb')
        file_handle.url = 'faulty.zip'
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, None)
        downloader_thread.HandleZipResource(file_handle)
