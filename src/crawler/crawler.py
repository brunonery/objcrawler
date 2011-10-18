#!/usr/bin/env python
"""seeder.py: Binary: crawls the web looking for 3D object models."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from crawler_config import CrawlerConfig
from crawler_thread import CrawlerThread
from downloader_thread import DownloaderThread

import argparse
import Queue
import threading

parser = argparse.ArgumentParser(
    description='Crawls the web looking for 3D object models.')
parser.add_argument('--config', action='store', type=str)
parser.add_argument('--instances', action='store', type=int, default=10)

if __name__ == "__main__":
    # TODO(brunonery): verify arguments and fail gracefully if necessary.
    args = parser.parse_args()
    config = CrawlerConfig(open(args.config))
    # Prepare database and locks.
    database_handler = DatabaseHandler(config.database_address())
    database_handler.Init()
    visitable_url_lock = threading.Lock()
    visited_url_lock = threading.Lock()
    # Prepare download queue.
    download_queue = Queue.Queue()
    # Start all threads.
    crawler_thread_list = []
    for i in range(args.instances):
        current_thread = CrawlerThread(database_handler,
                                       download_queue,
                                       visitable_url_lock,
                                       visited_url_lock)
        crawler_thread_list.append(current_thread)
        current_thread.start()
    downloader_thread_list = []
    # TODO(brunonery): have different number of crawler and downloader threads.
    for i in range(args.instances):
        current_thread = DownloaderThread(download_queue)
        current_thread.daemon = True
        downloader_thread_list.append(current_thread)
        current_thread.start()
    # Wait for all crawler threads to finish.
    for thread in crawler_thread_list:
        thread.join()
