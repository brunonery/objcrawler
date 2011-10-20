#!/usr/bin/env python
"""google_helper.py: Helpers for Google related functions."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import apiclient.discovery as google_api
import collections
import math

SearchResult = collections.namedtuple('SearchResult', 'title snippet link')

def GoogleSearch(developer_key, cref, query, max_results=10):
    """Performs a web search using Google.

    Arguments:
    developer_key -- a developer API key.
    cref -- a reference to a Custom Search Engine (CSE).
    query -- the query to be performed.
    max_results -- the maximum number of results to obtain. Maximum is 100.

    Returns:
    A list containing a set of SearchResult (title, snippet, link).
    """
    service = google_api.build("customsearch", "v1", developerKey=developer_key)
    search_results = []
    n_pages = int(math.ceil(max_results/10.0))
    for page in range(n_pages):
        first_result_in_page = 10 * page + 1
        n_results_in_page = min(10, max_results - first_result_in_page + 1)
        response = service.cse().list(q=query,
                                      cref=cref,
                                      start=first_result_in_page,
                                      num=n_results_in_page).execute()
        print page, first_result_in_page, n_results_in_page, len(response['items'])
        for item in response['items']:
            search_results.append(
                SearchResult(item['title'], item['snippet'], item['link']))
    return search_results
