#!/usr/bin/env python
"""crawl_helpers.py: General helpers for the crawler."""
__author__ = "Bruno Nery"
__email__  = "brunonery@brunonery.com"

from contrib.cache_decorators import lru_cache

import BeautifulSoup
import logging
import md5
import os
import re
import robotparser
import tempfile
import urlparse

def CanFetchURL(url):
    """Tells if can be fetched according to robots.txt."""
    split_url = urlparse.urlsplit(url)
    server_url = urlparse.urlunsplit(
        (split_url.scheme, split_url.netloc, '', '', ''))
    robot_parser = GetRobotParserForServer(server_url)
    # If robots.txt cannot be fetched, any URL can be fetched from the server.
    if robot_parser is None:
        return True
    else:
        return robot_parser.can_fetch('*', url)
    
def DownloadAsTemporaryFile(resource):
    """Downloads a resource to a temporary file.

    Arguments:
    resource -- the resource to be downloaded.

    Returns:
    A handle to the temporary file.

    Side effects:
    Closes the resource.
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
    A generator containing the items whose suffix is contained in suffixes.
    """
    return (i for i in items if any (s for s in suffixes if i.endswith(s)))

def GenerateBlenderFilenameFromURL(url):
    """Generates a blender filename from a URL.

    Extracts the filename (minus extension) from the URL, adding the md5 hash
    and the .blend extension to it. If no filename is found in the URL, the
    filename will consist of the md5 hash plus the .blend extension.

    Arguments:
    url -- the URL to use when generating the blender filename.

    Returns:
    A blender filename.
    """
    path = urlparse.urlsplit(url).path
    name = os.path.basename(path)
    m = md5.new()
    m.update(url)
    return name.split('.')[0] + m.hexdigest() + '.blend'
    
def GetLinksFromHtml(file_handle):
    """Returns a list with all the links contained in a HTML file.

    Arguments:
    file_handle -- a handle to the HTML file.

    Returns:
    A generator containing the links from the HTML file.
    """
    try:
        soup = BeautifulSoup.BeautifulSoup(file_handle)
    except TypeError:
        # This error is known to be a BeautifulSoup bug and is logged for
        # statistical reasons.
        logging.warning('Misbehaving HTML triggered BeautifulSoup bug (%s)',
                        file_handle.url)
        return []
    # Check only <a ...> tags with a 'href' attribute, ignoring section links.
    return (link['href'] for link in
            soup.findAll("a", attrs={'href': re.compile('^[^#].*')}))

@lru_cache()
def GetRobotParserForServer(server_url):
    """Downloads and parses the robots.txt file for a given server.

    Arguments:
    server_url -- the server to download robots.txt from.

    Returns:
    A robotparser.RobotFileParser object. None, if it cannot obtain the
    robots.txt file for some reason.
    """
    robot_parser = robotparser.RobotFileParser()
    robot_parser.set_url(urlparse.urljoin(server_url, 'robots.txt'))
    try:
        robot_parser.read()
    except IOError as io_error:
        logging.warning(
            'IOError getting robots.txt for %s (%s).', server_url, io_error)
        return None
    return robot_parser
  
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

    Side effects:
    Seek forward 7 bytes in the file_handle stream.
    """
    return (file_handle.read(7) == 'BLENDER')
