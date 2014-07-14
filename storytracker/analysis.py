import os
import gzip
import copy
import storytracker
from bs4 import BeautifulSoup


def open_archive_filepath(path):
    """
    Accepts a file path and returns a file object ready for analysis
    """
    # Split the file extension from the name
    name = os.path.basename(path)
    name, ext = os.path.splitext(name)
    # Extract the URL and timestamp from the file name
    url, timestamp = storytracker.reverse_archive_filename(name)
    # If it is gzipped, then open it that way
    if ext == '.gz':
        obj = gzip.open(path)
    # Otherwise handle it normally
    else:
        obj = open(path, "rb")
    return ArchivedURL(url, timestamp, obj.read())


class ArchivedURL(object):
    """
    An URL's archived HTML response with tools for analysis
    """
    def __init__(self, url, timestamp, html):
        self.url = url
        self.timestamp = timestamp
        self.html = html
        self.soup = BeautifulSoup(html)

    @property
    def hyperlinks(self):
        """
        Parse all of the hyperlinks from the HTML
        """
        link_list = []
        for a in self.soup.findAll("a", {"href": True}):
            obj = Hyperlink(a["href"])
            link_list.append(obj)
        return link_list


class ArchivedURLSet(list):
    """
    A list of archived URLs sorted by their timestamp
    """
    def append(self, obj):
        # Verify that the user is trying to add an ArchivedURL object
        if not isinstance(obj, ArchivedURL):
            raise TypeError("Only ArchivedURL objects can be added")

        # Check if the object is already in the list
        if obj in [o for o in list(self.__iter__())]:
            raise ValueError("This object is already in the list")

        # If it's all true, append it.
        super(ArchivedURLSet, self).append(copy.copy(obj))


class Hyperlink(object):
    """
    A hyperlink extracted from an archived URL with tools for analysis
    """
    def __init__(self, href):
        self.href = href
