#!/usr/bin/env python
"""downloader_thread.py: Implementation of the DownloaderThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import DownloadAsTemporaryFile
from common.crawl_helpers import FilterListBySuffix
from common.crawl_helpers import GenerateBlenderFilenameFromURL
from common.crawl_helpers import IsBlenderFile

import logging
import os
import struct
import threading
import zipfile

class DownloaderThread(threading.Thread):
    def __init__(self, download_queue, download_folder, zip_size_limit):
        threading.Thread.__init__(self)
        self.download_queue_ = download_queue
        self.download_folder_ = download_folder
        self.zip_size_limit_ = zip_size_limit

    def run(self):
        while True:
            resource = self.download_queue_.get()
            content_type = resource.headers['content-type']
            if content_type.startswith('application/zip'):
                self.HandleZipResource(resource)
            elif content_type.startswith('text/plain'):
                self.HandlePlainTextResource(resource)
            self.download_queue_.task_done()

    def HandleZipResource(self, resource):
        if ('content-length' not in resource.headers or
            int(resource.headers['content-length']) > self.zip_size_limit_):
            resource.close()
            return
        file_handle = DownloadAsTemporaryFile(resource)
        try:
            zip_handle = zipfile.ZipFile(file_handle)
            model_files = FilterListBySuffix(zip_handle.namelist(), ['.blend'])
            for model in model_files:
                zip_handle.extract(model, self.download_folder_)
        # We catch struct.error because of Python issue #4844.
        except (zipfile.BadZipfile, struct.error):
            logging.warning('Bad zip file: %s.' % (resource.url))

    def HandlePlainTextResource(self, resource):
        if IsBlenderFile(resource):
            self.HandleBlenderResource(resource)

    def HandleBlenderResource(self, resource):
        filename = GenerateBlenderFilenameFromURL(resource.url)
        file_handle = open(os.path.join(self.download_folder_, filename), 'wb')
        # We write BLENDER to the beginning of the file because IsBlenderFile
        # advances the stream by 7 characters but urllib2.urlopen objects don't
        # allow calling seek.
        file_handle.write('BLENDER')
        file_handle.write(resource.read())
        resource.close()
        file_handle.close()
