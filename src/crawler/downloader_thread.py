#!/usr/bin/env python
"""downloader_thread.py: Implementation of the DownloaderThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import IsBlenderFile

import logging
import threading

class DownloaderThread(threading.Thread):
    def __init__(self, download_queue):
        threading.Thread.__init__(self)
        self.download_queue_ = download_queue

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
        pass

    def HandlePlainTextResource(self, resource):
        pass
