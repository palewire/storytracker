import os
import six
import copy
import gzip
if six.PY2:
    import unicodecsv as csv
else:
    import csv
import storytracker
from six import BytesIO
from bs4 import BeautifulSoup
from .toolbox import UnicodeMixin
try:
    from urlparse import urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse


class ArchivedURL(UnicodeMixin):
    """
    An URL's archived HTML with tools for analysis
    """
    def __init__(self, url, timestamp, html):
        self.url = url
        self.timestamp = timestamp
        self.html = html
        self.soup = BeautifulSoup(html)
        # Attributes that come in handy below
        self.archive_path = None
        self._hyperlinks = []
        self._images = []

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

    def __unicode__(self):
        return six.text_type("%s@%s" % (self.url, self.timestamp))

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

    def get_hyperlinks(self, force=False):
        """
        Parses all of the hyperlinks from the HTML and returns a list of
        Hyperlink objects.

        The list is cached after it is first accessed.

        Set the `force` kwargs to True to regenerate it from scratch.
        """
        # If we already have the list, return it
        if self._hyperlinks and not force:
            return self._hyperlinks

        # Target the <body> tag if it exists since
        # we don't care what's in the <head>
        target = self.soup
        if hasattr(target, 'body'):
            target = target.body

        # Loop through all <a> tags with href attributes
        # and convert them to Hyperlink objects
        link_list = []
        for i, a in enumerate(target.findAll("a", {"href": True})):
            # Search out any images
            images = []
            for img in a.findAll("img", {"src": True}):
                image_obj = Image(img["src"])
                try:
                    images.append(image_obj)
                except ValueError:
                    pass
            # Create the Hyperlink object
            hyperlink_obj = Hyperlink(a["href"], a.string, i, images)
            # Add to the link list
            link_list.append(hyperlink_obj)

        # Stuff that list in our cache and then pass it out
        self._hyperlinks = link_list
        return link_list
    hyperlinks = property(get_hyperlinks)

    def write_hyperlinks_csv_to_file(self, file):
        """
        Returns the provided file object with a ready-to-serve CSV list of
        all hyperlinks extracted from the HTML.
        """
        writer = csv.writer(file)
        headers = [
            "archive_url",
            "archive_timestamp",
            "url_href",
            "url_domain",
            "url_string",
            "url_index",
        ]
        writer.writerow(headers)
        for h in self.hyperlinks:
            row = list(
                map(six.text_type, [self.url, self.timestamp])
            ) + h.__csv__()
            writer.writerow(row)
        file.seek(0)
        return file

    def get_images(self, force=False):
        """
        Parse the archived HTML for images and returns them as a list
        of Image objects.

        The list is cached after it is first accessed.

        Set the `force` kwargs to True to regenerate it from scratch.
        """
        # If we already have the list, return it
        if self._images and not force:
            return self._images

        # Target the <body> tag if it exists since
        # we don't care what's in the <head>
        target = self.soup
        if hasattr(target, 'body'):
            target = target.body

        # Loop through all <img> tags with src attributes
        # and convert them to Image objects
        image_list = []
        for img in target.findAll("img", {"src": True}):
            # Create the Image object
            image_obj = Image(img["src"])
            # Add to the image list
            image_list.append(image_obj)

        # Stuff that list in our cache and then pass it out
        self._images = image_list
        return image_list
    images = property(get_images)


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


class Hyperlink(UnicodeMixin):
    """
    A hyperlink extracted from an archived URL.
    """
    def __init__(self, href, string, index, images=[]):
        self.href = href
        self.string = string
        self.index = index
        self.domain = urlparse(href).netloc
        self.images = images

    def __eq__(self, other):
        """
        Tests whether this object is equal to something else.
        """
        if not isinstance(other, Image):
            return NotImplemented
        if self.href == other.href:
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

    def __unicode__(self):
        if len(self.href) > 40:
            return six.text_type("%s..." % self.href[:40])
        else:
            return six.text_type(self.href)

    def __csv__(self):
        """
        Returns a list of values ready to be written to a CSV file object
        """
        row = [
            self.href,
            self.domain,
            self.string or '',
            self.index,
        ]
        return list(map(six.text_type, row))


class Image(UnicodeMixin):
    """
    An image extracted from an archived URL.
    """
    def __init__(self, src):
        self.src = src

    def __eq__(self, other):
        """
        Tests whether this object is equal to something else.
        """
        if not isinstance(other, Image):
            return NotImplemented
        if self.src == other.src:
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

    def __unicode__(self):
        if len(self.src) > 40:
            return six.text_type("%s..." % self.src[:40])
        else:
            return six.text_type(self.src)
