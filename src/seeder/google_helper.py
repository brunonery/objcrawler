#!/usr/bin/env python
"""google_helper.py: Helpers for Google related functions."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from apiclient.discovery import build
from collections import namedtuple

SearchResult = namedtuple('SearchResult', 'title snippet link')

def GoogleSearch(developer_key, cref, query):
    """Performs a web search using Google.

    Arguments:
    developer_key -- a developer API key.
    cref -- a reference to a Custom Search Engine (CSE).
    query -- the query to be performed.

    Returns:
    A list containing a set of SearchResult (title, snippet, link).
    """
    service = build("customsearch", "v1", developerKey=developer_key)
    response = service.cse().list(q=query, cref=cref).execute()
    search_results = []
    for item in response['items']:
        search_results.append(SearchResult(item['title'], item['snippet'], item['link']))
    return search_results
