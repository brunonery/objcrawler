#!/usr/bin/env python
"""downloader_thread_test.py: Tests for downloader_thread.py."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from downloader_thread import DownloaderThread

import io
import mock
import os
import StringIO
import testfixtures
import unittest

class DownloaderThreadTest(unittest.TestCase):
    zip_size_limit = 30000
    def testHandleZipResourceWorks(self):
        # Open Zip resource.
        file_handle = io.open('test/data/sample.zip', 'rb')
        file_handle.headers = {'content-length': '27007'}
        # Test the Zip handler.
        downloader_thread = DownloaderThread(
            None, 'test/tmp', self.zip_size_limit)
        downloader_thread.HandleZipResource(file_handle)
        assert os.path.exists('test/tmp/sample.blend')
        assert not os.path.exists('test/tmp/sample.txt')

    def testHandleZipResourceIgnoresNonZipFiles(self):
        # Create non-Zip resource.
        file_handle = StringIO.StringIO('nozipfile')
        file_handle.url = 'nozipfile.zip'
        file_handle.headers = {'content-length': '9'}
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, None, self.zip_size_limit)
        downloader_thread.HandleZipResource(file_handle)

    def testHandleZipResourceIgnoresFaultyZipFiles(self):
        # Open Zip resource.
        file_handle = io.open('test/data/faulty.zip', 'rb')
        file_handle.url = 'faulty.zip'
        file_handle.headers = {'content-length': '27006'}
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, None, self.zip_size_limit)
        downloader_thread.HandleZipResource(file_handle)

    def testHandleZipResourceIgnoresBigFiles(self):
        # Create non-Zip resource.
        file_handle = io.open('test/data/sample.zip', 'rb')
        file_handle.headers = {'content-length': str(self.zip_size_limit + 1)} 
        # Test the Zip handler.
        downloader_thread = DownloaderThread(None, None, self.zip_size_limit)
        with testfixtures.Replacer() as r:
            mock_download_as_temporary_file = mock.Mock(return_value=file_handle)
            r.replace('crawler.downloader_thread.DownloadAsTemporaryFile',
                      mock_download_as_temporary_file)
            downloader_thread.HandleZipResource(file_handle)
            assert not mock_download_as_temporary_file.called
    
    def testHandlePlainTextResourceWorks(self):
        downloader_thread = DownloaderThread(None, None, 0)
        downloader_thread.HandleBlenderResource = mock.Mock()
        with testfixtures.Replacer() as r:
            r.replace('crawler.downloader_thread.IsBlenderFile',
                      mock.Mock(return_value=True))
            downloader_thread.HandlePlainTextResource(None)
            downloader_thread.HandleBlenderResource.assert_called_with(None)

    def testHandleBlenderResourceWorks(self):
        downloader_thread = DownloaderThread(None, 'test/tmp', 0)
        with testfixtures.Replacer() as r:
            r.replace('crawler.downloader_thread.GenerateBlenderFilenameFromURL',
                      mock.Mock(return_value='fake.blend'))
            fake_handle = StringIO.StringIO('')
            fake_handle.url = 'fake.blend'
            downloader_thread.HandleBlenderResource(fake_handle)
            assert os.path.exists('test/tmp/fake.blend')
