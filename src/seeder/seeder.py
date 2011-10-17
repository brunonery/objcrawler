#!/usr/bin/env python
"""seeder.py: Binary: populates the crawler database with URLs to visit."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from common.database_handler import DatabaseHandler
from google_helper import GoogleSearch
from models.visitable_url import VisitableURL
from seeder_config import SeederConfig

import argparse

parser = argparse.ArgumentParser(description='Seed the crawler with URLs to be visited.')
parser.add_argument('--config', action='store', type=str)
parser.add_argument('--use_google', action='store_true', default=False)
parser.add_argument('--query', action='store', type=str)

def SeedWithGoogle(config, query):
    """Seeds the database using the results from a Google Search.

    Arguments:
    config -- the seeder config.
    query -- the query to be performed.
    """
    # Obtain the search results.
    search_results = GoogleSearch(
        config.google_developer_key(), config.google_cref(), query)
    # Prepare the database.
    database_handler = DatabaseHandler(config.database_address())
    database_handler.Init()
    # Add the results to the database.
    session = database_handler.CreateSession()
    for i in range(len(search_results)):
        session.add(VisitableURL(search_results[i].link, i))
    session.commit()

if __name__ == "__main__":
    # TODO(brunonery): verify arguments and fail gracefully if necessary.
    args = parser.parse_args()
    config = SeederConfig(open(args.config))
    if args.use_google:
        SeedWithGoogle(config, args.query)
