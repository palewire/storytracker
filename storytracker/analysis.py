import os
import six
import math
import copy
import gzip
import tempfile
import storytracker
import storysniffer
from six import BytesIO
from selenium import webdriver
from .toolbox import UnicodeMixin
from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw
if six.PY2:
    import unicodecsv as csv
else:
    import csv
try:
    from urlparse import urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse


class ArchivedURL(UnicodeMixin):
    """
    An URL's archived HTML with tools for analysis
    """
    def __init__(
        self, url, timestamp, html, archive_path=None,
        browser_width=1024, browser_height=768
    ):
        self.url = url
        self.timestamp = timestamp
        self.html = html
        # Attributes that come in handy below
        self.archive_path = archive_path
        self._height = None
        self._width = None
        self._hyperlinks = []
        self._images = []
        self.browser = None
        self.browser_width = browser_width
        self.browser_height = browser_height

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

    def open_browser(self):
        """
        Open the web browser we will use to simulate the website for analysis.
        """
        # Just stop now if it already exists
        if self.browser:
            return
        try:
            # First try PhantomJS
            self.browser = webdriver.PhantomJS()
        except:
            # If it isn't installed try Firefox
            self.browser = webdriver.Firefox()

        # Size the browser
        self.browser.set_window_size(self.browser_width, self.browser_height)

        # Check if an archived HTML file exists, if not create one
        # so our selenium browser has something to read.
        if not self.archive_path or not self.archive_path.endswith("html"):
            tmpdir = tempfile.mkdtemp()
            self.write_html_to_directory(tmpdir)
        self.browser.get("file://%s" % self.archive_path)

    def close_browser(self):
        """
        Close the web browser we use to simulate the website.
        """
        # Just stop now if it doesn't exist
        if not self.browser:
            return
        # Close it
        self.browser.close()
        # Null out the value
        self.browser = None

    def analyze(self):
        """
        Force all of the normally lazy-loading analysis methods to run
        and cache the results.
        """
        self.open_browser()
        self.get_height(force=True)
        self.get_width(force=True)
        self.get_hyperlinks(force=True)
        self.get_images(force=True)
        self.close_browser()

    def get_cell(self, x, y, cell_size=256):
        """
        Returns the grid cell where the provided x and y coordinates
        appear on the page.
        """
        xgroup = int(math.floor(float(x) / cell_size))
        # Convert the x value to a letter ala chess notation
        xgroup = chr(xgroup + ord('a'))
        ygroup = int(math.ceil(float(y) / cell_size))
        return '%s%s' % (xgroup, ygroup)

    def get_height(self, force=False):
        # If we already have it return it
        if self._height and not force:
            return self._height

        # Open the browser if it's not already open
        if not self.browser:
            self.open_browser()

        # Stuff that list in our cache and then pass it out
        self._height = self.browser.execute_script(
            "return document.body.scrollHeight"
        )
        return self._height
    height = property(get_height)

    def get_width(self, force=False):
        # If we already have it return it
        if self._width and not force:
            return self._width

        # Open the browser if it's not already open
        if not self.browser:
            self.open_browser()

        # Stuff that list in our cache and then pass it out
        self._width = self.browser.execute_script(
            "return document.body.scrollWidth"
        )
        return self._width
    width = property(get_width)

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

        # Open the browser if it's not already open
        if not self.browser:
            self.open_browser()

        # Loop through all <a> tags with href attributes
        # and convert them to Hyperlink objects
        obj_list = []
        link_list = self.browser.find_elements_by_tag_name("a")
        link_list = [
            a for a in link_list if a.get_attribute("href") and a.text
        ]
        for i, a in enumerate(link_list):
            # Search out any images
            image_obj_list = []
            img_list = a.find_elements_by_tag_name("img")
            img_list = [o for o in img_list if o.get_attribute("src")]
            for img in img_list:
                ilocation = img.location
                isize = img.size
                image_obj = Image(
                    img.get_attribute("src"),
                    width=isize['width'],
                    height=isize['height'],
                    x=ilocation['x'],
                    y=ilocation['y'],
                    cell=self.get_cell(ilocation['x'], ilocation['y']),
                )
                try:
                    image_obj_list.append(image_obj)
                except ValueError:
                    pass
            # Create the Hyperlink object
            alocation = a.location
            asize = a.size
            hyperlink_obj = Hyperlink(
                a.get_attribute("href"),
                a.text,
                i,
                images=image_obj_list,
                width=asize['width'],
                height=asize['height'],
                x=alocation['x'],
                y=alocation['y'],
                cell=self.get_cell(alocation['x'], alocation['y']),
                font_size=a.value_of_css_property("font-size"),
            )
            # Add to the link list
            obj_list.append(hyperlink_obj)

        # Stuff that list in our cache and then pass it out
        self._hyperlinks = obj_list
        return obj_list
    hyperlinks = property(get_hyperlinks)

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

        # Open the browser if it's not already open
        if not self.browser:
            self.open_browser()

        # Loop through all <img> tags with src attributes
        # and convert them to Image objects
        obj_list = []
        img_list = self.browser.find_elements_by_tag_name("img")
        img_list = [i for i in img_list if i.get_attribute("src")]
        for img in img_list:
            # Create the Image object
            location = img.location
            size = img.size
            image_obj = Image(
                img.get_attribute("src"),
                width=size['width'],
                height=size['height'],
                x=location['x'],
                y=location['y'],
                cell=self.get_cell(location['x'], location['y']),
            )
            # Add to the image list
            obj_list.append(image_obj)

        # Stuff that list in our cache and then pass it out
        self._images = obj_list
        return obj_list
    images = property(get_images)

    @property
    def largest_image(self):
        """
        Returns the Image with the greatest area in size
        """
        try:
            return sorted(self.images, key=lambda x: x.area, reverse=True)[0]
        except IndexError:
            return None

    def write_hyperlinks_csv_to_file(self, file):
        """
        Returns the provided file object with a ready-to-serve CSV list of
        all hyperlinks extracted from the HTML.
        """
        # Create a CSV writer object out of the file
        writer = csv.writer(file)

        # Load up all the row
        row_list = []
        for h in self.hyperlinks:
            row = list(
                map(six.text_type, [self.url, self.timestamp])
            ) + h.__csv__()
            row_list.append(row)

        # Create the headers, which will change depending on how many
        # images are found in the urls
        headers = [
            "archive_url",
            "archive_timestamp",
            "url_href",
            "url_domain",
            "url_string",
            "url_index",
            "url_is_story",
            "url_width",
            "url_height",
            "url_x",
            "url_y",
            "url_cell",
            "url_font_size",
        ]
        longest_row = max([len(r) for r in row_list])
        for i in range(int(((longest_row - len(headers))/8))):
            headers.append("image_%s_src" % (i + 1))
            headers.append("image_%s_width" % (i + 1))
            headers.append("image_%s_height" % (i + 1))
            headers.append("image_%s_orientation" % (i + 1))
            headers.append("image_%s_area" % (i + 1))
            headers.append("image_%s_x" % (i + 1))
            headers.append("image_%s_y" % (i + 1))
            headers.append("image_%s_cell" % (i + 1))

        # Write it out to the file
        writer.writerow(headers)
        writer.writerows(row_list)

        # Reboot the file and pass it back out
        file.seek(0)
        return file

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

    def write_illustration_to_directory(self, path):
        """
        Writes out a visualization of the hyperlinks and images on the page
        as a JPG to the provided directory path.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        img_path = os.path.join(
            path,
            "%s.jpg" % self.archive_filename
        )
        if os.path.exists(img_path):
            os.remove(img_path)
        im = PILImage.new(
            "RGBA",
            (self.width, self.height),
            (221, 221, 221, 255)
        )
        draw = PILImageDraw.Draw(im)
        for a in self.hyperlinks:
            if a.is_story:
                fill = "purple"
            else:
                fill = "blue"
            draw.rectangle(a.bounding_box, fill=fill)
        for i in self.images:
            draw.rectangle(i.bounding_box, fill="red")
        im.save(img_path, 'JPEG')
        return img_path


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
    def __init__(
        self, href, string, index, images=[],
        x=None, y=None,
        width=None, height=None,
        cell=None, font_size=None
    ):
        self.href = href
        self.string = string
        self.index = index
        self.domain = urlparse(href).netloc
        self.images = images
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.cell = cell
        self.font_size = font_size

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
            self.is_story,
            self.width,
            self.height,
            self.x,
            self.y,
            self.cell,
            self.font_size,
        ]
        for img in self.images:
            row.append(img.src)
            row.append(img.width)
            row.append(img.height)
            row.append(img.orientation)
            row.append(img.area)
            row.append(img.x)
            row.append(img.y)
            row.append(img.cell)
        return list(map(six.text_type, row))

    @property
    def bounding_box(self):
        """
        Returns a bounding box for the image on the page.
        """
        return (
            (self.x, self.y),
            (self.x+self.width, self.y+self.height)
        )

    @property
    def is_story(self):
        """
        Returns a true or false estimate of whether the URL links to a news
        story.
        """
        try:
            return storysniffer.guess(self.href)
        except ValueError:
            return False


class Image(UnicodeMixin):
    """
    An image extracted from an archived URL.
    """
    def __init__(
        self, src, width=None, height=None, x=None, y=None, cell=None
    ):
        self.src = src
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.cell = cell

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

    @property
    def area(self):
        """
        Returns the area of the image
        """
        if not self.width or not self.height:
            return None
        return self.width * self.height

    @property
    def bounding_box(self):
        """
        Returns a bounding box for the image on the page.
        """
        return (
            (self.x, self.y),
            (self.x+self.width, self.y+self.height)
        )

    @property
    def orientation(self):
        """
        Returns a string describing the shape of the image.

            'square' means the width and height are equal
            'landscape' is a horizontal image with width greater than height
            'portrait' is a vertical image with height greater than width
            None means there are no size attributes to test
        """
        if not self.width or not self.height:
            return None
        elif self.width == self.height:
            return 'square'
        elif self.width > self.height:
            return 'landscape'
        elif self.height > self.width:
            return 'portrait'
