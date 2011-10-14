from apiclient.discovery import build
from collections import namedtuple

SearchResult = namedtuple('SearchResult', 'title snippet url')

def GoogleSearch(developer_key, cref, query):
    service = build("customsearch", "v1", developerKey=developer_key)
    response = service.cse().list(q=query, cref=cref).execute()
    search_results = []
    for item in response['items']:
        search_results.append(SearchResult(item['title'], item['snippet'], item['link']))
    return search_results
