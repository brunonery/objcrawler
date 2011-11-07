#!/usr/bin/env python
"""seeder.py: Binary: populates the crawler database with URLs to visit."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from google_helper import google_search
from models.url import URL
from seeder_config import SeederConfig

import argparse

parser = argparse.ArgumentParser(description='Seed the crawler with URLs to be visited.')
parser.add_argument('--config', action='store', type=str)
parser.add_argument('--use_google', action='store_true', default=False)
parser.add_argument('--query', action='store', type=str)
parser.add_argument('--max_results', action='store', type=int, default=10)
parser.add_argument('--source_file', action='store', type=str)

def seed_with_google(config, query, max_results):
    """Seeds the database using the results from a Google Search.

    Arguments:
    config -- the seeder config.
    query -- the query to be performed.
    max_results -- the maximum number of results.
    """
    # Obtain the search results.
    search_results = google_search(
        config.google_developer_key(), config.google_cref(), query, max_results)
    # Prepare the database.
    database_handler = DatabaseHandler(config.database_address())
    database_handler.init()
    # Add the results to the database.
    session = database_handler.create_session()
    for result in search_results:
        # Seed results always have the highest priority.
        session.add(URL(result.link, 0))
    session.commit()

def seed_with_list(config, filename):
    """Seeds the database using the links from a text file.

    Arguments:
    config -- the seeder config.
    filename -- the name of the file to be read.
    """
    f = open(filename, 'r')
    link_list = f.readlines()
    f.close()
    # Prepare the database.
    database_handler = DatabaseHandler(config.database_address())
    database_handler.init()
    # Add the results to the database.
    session = database_handler.create_session()
    for link in link_list:
        # Seed results always have the highest priority.
        session.add(URL(link, 0))
    session.commit()

if __name__ == "__main__":
    # TODO(brunonery): verify arguments and fail gracefully if necessary.
    args = parser.parse_args()
    config = SeederConfig(open(args.config))
    if args.use_google:
        seed_with_google(config, args.query, args.max_results)
    else:
        seed_with_list(config, args.source_file)
