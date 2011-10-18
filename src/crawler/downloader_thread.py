#!/usr/bin/env python
"""downloader_thread.py: Implementation of the DownloaderThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import DownloadAsTemporaryFile
from common.crawl_helpers import FilterListBySuffix
from common.crawl_helpers import IsBlenderFile

import logging
import threading
import zipfile

class DownloaderThread(threading.Thread):
    def __init__(self, download_queue, download_folder):
        threading.Thread.__init__(self)
        self.download_queue_ = download_queue
        self.download_folder_ = download_folder

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
        # TODO(brunonery): limit the size of Zip files that are downloaded.
        file_handle = DownloadAsTemporaryFile(resource)
        try:
            zip_handle = zipfile.ZipFile(file_handle)
            model_files = FilterListBySuffix(zip_handle.namelist(), ['.blend'])
            for model in model_files:
                zip_handle.extract(model, self.download_folder_)
        except zipfile.BadZipfile:
            logging.warning('Bad zip file: %s.' % (resource.url))

    def HandlePlainTextResource(self, resource):
        pass
