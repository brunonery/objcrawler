#!/usr/bin/env python
"""crawl_helpers.py: General helpers for the crawler."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

import BeautifulSoup
import re
import tempfile

def DownloadAsTemporaryFile(resource):
    """Downloads a resource to a temporary file.

    Arguments:
    resource -- the resource to be downloaded.

    Returns:
    A handle to the temporary file.
    """
    file_handle = tempfile.TemporaryFile()
    file_handle.write(resource.read())
    resource.close()
    file_handle.seek(0)
    return file_handle
    
def FilterListBySuffix(items, suffixes):
    """Filters a list.

    Arguments:
    items -- a list of strings.
    suffixes -- the allowed suffixes.

    Returns:
    A list containing only the items whose suffix is contained in suffixes.
    """
    new_list = []
    for item in items:
        for suffix in suffixes:
            if item.endswith(suffix):
                new_list.append(item)
                continue
    return new_list

def GetLinksFromHtml(file_handle):
    """Returns a list with all the links contained in a HTML file.

    Arguments:
    file_handle -- a handle to the HTML file.

    Returns:
    A list containing the links contained in the HTML file.
    """
    soup = BeautifulSoup.BeautifulSoup(file_handle)
    link_list = []
    # Check only <a ...> tags with a 'href' attribute.
    for link in soup.findAll("a", attrs={'href': re.compile(".*")}):
        href = link['href']
        # Ignore section links.
        if not href.startswith('#'):
            link_list.append(href)
    return link_list

def GetURLPriority(url):
    """Obtains a URL priority.

    Arguments:
    url -- the URL to be evaluated.

    Returns:
    The URL priority. A smaller number indicates higher priority.
    """
    # Zip and 3D models should be handled first.
    if url.endswith('zip') or url.endswith('blend'):
        return 1
    else:
        return 2

def IsBlenderFile(file_handle):
    """Tells if a file is a blender one.

    Arguments:
    file_handle -- a handle to the file.

    Returns:
    True if the file is a blender one, False otherwise.
    """
    return (file_handle.read(7) == 'BLENDER')
