#!/usr/bin/env python
"""seeder.py: Binary: crawls the web looking for 3D object models."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from crawler_config import CrawlerConfig
from crawler_thread import CrawlerThread

import argparse
import threading

parser = argparse.ArgumentParser(
    description='Crawls the web looking for 3D object models.')
parser.add_argument('--config', action='store', type=str)
# TODO(brunonery): add argument for number of threads (with default).

if __name__ == "__main__":
    # TODO(brunonery): verify arguments and fail gracefully if necessary.
    args = parser.parse_args()
    config = CrawlerConfig(open(args.config))
    database_handler = DatabaseHandler(config.database_address())
    database_handler.Init()
    visitable_url_lock = threading.Lock()
    visited_url_lock = threading.Lock()
    thread_list = []
    for i in range(10):
        current_thread = CrawlerThread(database_handler,
                                       visitable_url_lock,
                                       visited_url_lock)
        thread_list.append(current_thread)
        current_thread.start()
        
    for thread in thread_list:
        thread.join()
