#!/usr/bin/env python
"""downloader_thread.py: Implementation of the DownloaderThread."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.crawl_helpers import download_as_temporary_file
from common.crawl_helpers import filter_list_by_suffix
from common.crawl_helpers import generate_blender_filename_from_url
from common.crawl_helpers import is_blender_file

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
            logging.warning(
                'Zip file is too big or doesn\'t contain size information (%s).',
                resource.url)
            resource.close()
            return
        file_handle = download_as_temporary_file(resource)
        try:
            zip_handle = zipfile.ZipFile(file_handle)
            model_files = filter_list_by_suffix(zip_handle.namelist(), ['.blend'])
            for model in model_files:
                zip_handle.extract(model, self.download_folder_)
        # We catch struct.error because of Python issue #4844.
        except (zipfile.BadZipfile, struct.error):
            logging.warning('Bad zip file: %s.' % (resource.url))

    def HandlePlainTextResource(self, resource):
        if is_blender_file(resource):
            self.HandleBlenderResource(resource)

    def HandleBlenderResource(self, resource):
        filename = generate_blender_filename_from_url(resource.url)
        file_handle = open(os.path.join(self.download_folder_, filename), 'wb')
        # We write BLENDER to the beginning of the file because IsBlenderFile
        # advances the stream by 7 characters but urllib2.urlopen objects don't
        # allow calling seek.
        file_handle.write('BLENDER')
        file_handle.write(resource.read())
        resource.close()
        file_handle.close()
