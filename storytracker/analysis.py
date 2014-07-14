import os
import copy
import gzip
import storytracker
from six import BytesIO
from bs4 import BeautifulSoup


class ArchivedURL(object):
    """
    An URL's archived HTML with tools for analysis
    """
    def __init__(self, url, timestamp, html):
        self.url = url
        self.timestamp = timestamp
        self.html = html
        self.soup = BeautifulSoup(html)
        self.archive_path = None

    def __eq__(self, other):
        """
        Tests whether this object is equal to something else.
        """
        if not isinstance(other, ArchivedURL):
            return NotImplemented
        if self.url == other.url:
            if self.timestamp == other.timestamp:
                if self.html == other.html:
                    return True
        return False

    def __ne__(self, other):
        """
        Tests whether this object is unequal to something else.
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @property
    def archive_filename(self):
        """
        Returns a file name for this archive using storytracker's naming scheme
        """
        return storytracker.create_archive_filename(self.url, self.timestamp)

    @property
    def gzip(self):
        """
        Returns HTML as a stream of gzipped data
        """
        out = BytesIO()
        with gzip.GzipFile(fileobj=out, mode="wb") as f:
            f.write(self.html.encode("utf-8"))
        return out.getvalue()

    def write_gzip_to_directory(self, path):
        """
        Writes gzipped HTML data to a file in the provided directory path
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        self.archive_path = os.path.join(path, "%s.gz" % self.archive_filename)
        fileobj = open(self.archive_path, 'wb')
        with gzip.GzipFile(fileobj=fileobj, mode="wb") as f:
            f.write(self.html.encode("utf-8"))
        return self.archive_path

    def write_html_to_directory(self, path):
        """
        Writes HTML data to a file in the provided directory path
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        self.archive_path = os.path.join(
            path,
            "%s.html" % self.archive_filename
        )
        with open(self.archive_path, 'wb') as f:
            f.write(self.html.encode("utf-8"))
        return self.archive_path

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
    A list of archived URLs
    """
    def __init__(self, obj_list):
        # Create a list to put objects after we've checked them out
        safe_list = []
        for obj in obj_list:

            # Verify that the user is trying to add an ArchivedURL object
            if not isinstance(obj, ArchivedURL):
                raise TypeError("Only ArchivedURL objects can be added")

            # Check if the object is already in the list
            if obj in safe_list:
                raise ValueError("This object is already in the list")

            # Add to safe list
            safe_list.append(obj)

        # Do the normal list start up
        super(ArchivedURLSet, self).__init__(obj_list)

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
