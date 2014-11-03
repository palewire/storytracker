import os
import six
import math
import copy
import gzip
import base64
import shutil
import socket
import logging
import tempfile
import calculate
import images2gif
import collections
import storytracker
import storysniffer
from six import BytesIO
from datetime import timedelta
from selenium import webdriver
from PIL import Image as PILImage
from PIL import ImageFont as PILImageFont
from PIL import ImageDraw as PILImageDraw
from .toolbox import UnicodeMixin, indent
from jinja2 import Environment, PackageLoader
if six.PY2:
    import unicodecsv as csv
else:
    import csv
try:
    from urlparse import urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
jinja = Environment(loader=PackageLoader('storytracker', 'templates'))


class ArchivedURL(UnicodeMixin):
    """
    An URL's archived HTML with tools for analysis
    """
    def __init__(
        self,
        url, timestamp, html,
        html_archive_path=None,
        gzip_archive_path=None,
        browser_width=1366,
        browser_height=768,
        browser_driver="PhantomJS",
        browser_timeout=15,
    ):
        self.url = url
        self.timestamp = timestamp
        self.html = html
        # Attributes that come in handy below
        self.html_archive_path = html_archive_path
        self.gzip_archive_path = gzip_archive_path
        self._browser = None
        self._height = None
        self._width = None
        self._hyperlinks = []
        self._images = []
        self._summary_statistics = {}
        self._screenshot = None
        self.this_directory = os.path.dirname(os.path.realpath(__file__))
        self.font = PILImageFont.truetype(
            os.path.join(self.this_directory, "fonts/OpenSans-Regular.ttf"),
            35
        )
        # Configuration for our web browser
        self.browser_width = browser_width
        self.browser_height = browser_height
        self.browser_driver = browser_driver
        self.browser_timeout = browser_timeout

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

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

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

    def get_browser(self, force=False):
        """
        Returns a Selenium web browser ready to use.

        Cached when it is opened the first time so we can avoid repeating
        outselves.
        """
        if self._browser and not force:
            return self._browser
        b = self.open_browser()
        self._browser = b
        return b
    browser = property(get_browser)

    def open_browser(self):
        """
        Open the web browser we will use to simulate the website for analysis.
        """
        # Open the browser
        logger.debug("Opening browser")
        browser = getattr(webdriver, self.browser_driver)()

        # Size the browser
        browser.set_window_size(self.browser_width, self.browser_height)

        # If there is no HTML file to read in, make it now
        if not self.html_archive_path:
            tmpdir = tempfile.mkdtemp()
            self.write_html_to_directory(tmpdir)

        # Open the HTML file in the driver
        socket.setdefaulttimeout(self.browser_timeout)
        try:
            logger.debug("Retrieving %s in browser" % self.html_archive_path)
            browser.get("file://%s" % self.html_archive_path)
        except socket.timeout:
            logger.debug("Browser timeout")
            browser.execute_script("window.stop()")

        # Pass it back
        return browser

    def close_browser(self):
        """
        Close the web browser we use to simulate the website.
        """
        # Just stop now if it doesn't exist
        if not self._browser:
            return
        # Close it
        logger.debug("Closing browser")
        self._browser.close()
        # Null out the value
        self._browser = None

    def analyze(self, force=False):
        """
        Force all of the normally lazy-loading analysis methods to run
        and cache the results.
        """
        self.get_browser()
        self.get_height(force=force)
        self.get_width(force=force)
        self.get_hyperlinks(force=force)
        self.get_images(force=force)
        self.get_summary_statistics(force=force)
        self.get_screenshot(force=force)
        self.close_browser()

    def get_cell(self, x, y, cell_size=256):
        """
        Returns the grid cell where the provided x and y coordinates
        appear on the page.
        """
        try:
            xgroup = int(math.floor(float(x) / cell_size))
            # Convert the x value to a letter ala chess notation
            xgroup = chr(xgroup + ord('a'))
            ygroup = int(math.ceil(float(y) / cell_size))
            return '%s%s' % (xgroup, ygroup)
        except ValueError:
            return ''

    def get_height(self, force=False):
        # If we already have it return it
        if self._height and not force:
            return self._height

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

        # Loop through all <a> tags with href attributes
        # and convert them to Hyperlink objects
        logger.debug("Extracting hyperlinks from HTML")
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

    def get_story_links(self):
        """
        Return only hyperlinks estimated to be stories.
        """
        return [h for h in self.hyperlinks if h.is_story]
    story_links = property(get_story_links)

    def get_hyperlink_by_href(self, href, fails_silently=True):
        """
        Returns the Hyperlink object that matches the submitted href,
        if it exists.
        """
        # If hyperlinks have already been harvested, just loop through
        # those and see if you find a match.
        if self._hyperlinks:
            for this_hyperlink in self.hyperlinks:
                if this_hyperlink.href == href:
                    return this_hyperlink
            if fails_silently:
                return None
            else:
                raise ValueError("href could not be found")

        # If the hyperlinks haven't been pulled use XPATH to fetch
        # the ones we care about here a little more efficiently
        else:
            try:
                a = self.browser.find_element_by_xpath(
                    "//a[contains(@href,'%s')]" % href
                )
            except:
                if fails_silently:
                    return None
                else:
                    raise
            # Create the Hyperlink object
            alocation = a.location
            asize = a.size
            return Hyperlink(
                a.get_attribute("href"),
                a.text,
                None,
                images=None,
                width=asize['width'],
                height=asize['height'],
                x=alocation['x'],
                y=alocation['y'],
                cell=self.get_cell(alocation['x'], alocation['y']),
                font_size=a.value_of_css_property("font-size"),
            )

    def get_images(self, force=False):
        """
        Parse the archived HTML for images and returns them as a list
        of Image objects.

        The list is cached after it is first accessed.

        Set the `force` kwarg to True to regenerate it from scratch.
        """
        # If we already have the list, return it
        if self._images and not force:
            return self._images

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

    def get_screenshot(self, force=False):
        """
        Generate a screenshot of the page and return it as a PIL file object.

        The object is cached after it is first accessed.

        Set the `force` kwarg to True to regenerate it from scratch.
        """
        # If we already have it, return it
        if self._screenshot and not force:
            self._screenshot.seek(0)
            return self._screenshot

        # Take a screenshot and convert it to bytes
        bytes = BytesIO(
            base64.b64decode(
                self.browser.get_screenshot_as_base64()
            )
        )

        # Reopen it and paste it on a white background
        sshot = PILImage.open(bytes)
        sshot_width, sshot_height = sshot.size
        im = PILImage.new(
            "RGBA",
            (sshot_width, sshot_height),
            (255, 255, 255, 255)
        )
        im.paste(sshot, sshot)

        # Set the variable and pass that out
        self._screenshot = im
        return im
    screenshot = property(get_screenshot)

    @property
    def largest_headline(self):
        """
        Returns the story hyperlink with the largest area on the page.

        If there is a tie, returns the one that appears first on the page.
        """
        story_hyperlinks = [h for h in self.hyperlinks if h.is_story]
        try:
            return sorted(
                story_hyperlinks,
                key=lambda x: (-x.area, x.index)
            )[0]
        except IndexError:
            return None

    @property
    def largest_image(self):
        """
        Returns the Image with the greatest area in size
        """
        try:
            return sorted(self.images, key=lambda x: x.area, reverse=True)[0]
        except IndexError:
            return None

    def get_summary_statistics(self, force=False):
        """
        Returns a dictionary with basic summary statistics about hyperlinks
        and images on the page.
        """
        # If we already have them, return them
        if self._summary_statistics and not force:
            return self._summary_statistics

        # all the biz adding stuff to the dict here
        self._summary_statistics = {
            'hyperlink_count': len(self.hyperlinks),
            'image_count': len(self.images),
            'story_link_count': len([
                h for h in self.hyperlinks if h.is_story
            ])
        }

        # Pass it back out
        return self._summary_statistics
    summary_statistics = property(get_summary_statistics)

    def write_analysis_report_to_directory(self, path):
        """
        Create an analysis report that summarizes our outputs
        as an HTML package.
        """
        # Run the numbers
        self.analyze(force=False)

        # Set up the directory where we will output the data
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        output_path = os.path.join(
            path,
            "urlanalysis-report-%s" % self.archive_filename
        )
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)

        # Write out the overlay png
        self.write_overlay_to_directory(output_path)
        overlay_png_name = "overlay-%s.png" % self.archive_filename

        # Write out the illo jpg
        self.write_illustration_to_directory(output_path)
        illo_jpg_name = "illustration-%s.jpg" % self.archive_filename

        # Write out a copy of the HTML archive
        html_archive_name = "%s.html" % self.archive_filename
        self.write_html_to_directory(output_path)

        # Write out hyperlinks csv
        hyperlinks_csv_name = "hyperlinks-%s.csv" % self.archive_filename
        hyperlinks_csv_path = os.path.join(output_path, hyperlinks_csv_name)
        self.write_hyperlinks_csv_to_path(hyperlinks_csv_path)

        # Render report template
        context = {
            'object': self,
            'html_archive_name': html_archive_name,
            'hyperlinks_csv_name': hyperlinks_csv_name,
            'overlay_png_name': overlay_png_name,
            'illo_jpg_name': illo_jpg_name,
        }
        template = jinja.get_template('archivedurl.html')
        html = template.render(**context)

        # Write out to file
        file = open(os.path.join(output_path, "index.html"), "wb")
        file.write(html)
        file.close()

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

    def write_hyperlinks_csv_to_path(self, path):
        """
        Writes out a CSV of the hyperlinks extracted from the page to the
        provided file path.
        """
        f = open(path, "wb")
        self.write_hyperlinks_csv_to_file(f)

    def write_gzip_to_file(self, file):
        """
        Writes gzipped HTML data to provided file object.
        """
        with gzip.GzipFile(fileobj=file, mode="wb") as f:
            f.write(self.html.encode("utf-8"))

    def write_gzip_to_directory(self, path):
        """
        Writes gzipped HTML data to a file in the provided directory path
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        self.gzip_archive_path = os.path.join(
            path,
            "%s.gz" % self.archive_filename
        )
        fileobj = open(self.gzip_archive_path, 'wb')
        self.write_gzip_to_file(fileobj)
        return self.gzip_archive_path

    def write_gzip_to_path(self, path):
        """
        Writes gzipped HTML data to the provided path.
        """
        fileobj = open(path, 'wb')
        self.write_gzip_to_file(fileobj)

    def write_html_to_directory(self, path):
        """
        Writes HTML data to a file in the provided directory path
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        self.html_archive_path = os.path.join(
            path,
            "%s.html" % self.archive_filename
        )
        self.write_html_to_path(self.html_archive_path)
        return self.html_archive_path

    def write_html_to_path(self, path):
        """
        Writes HTML data to the provided path.
        """
        with open(path, 'wb') as f:
            f.write(self.html.encode("utf-8"))

    def timestamp_image(self, image, width=460, height=50):
        textlayer = PILImage.new(
            "RGBA",
            (width, height),
            (255, 255, 255, 255)
        )
        textdraw = PILImageDraw.Draw(textlayer)
        textdraw.text(
            (5, 0),
            self.timestamp.isoformat(),
            font=self.font,
            fill=(0, 0, 0)
        )
        image.paste(textlayer, (image.size[0]-width, 0))
        return image

    def write_illustration_to_directory(self, path):
        """
        Writes out a visualization of the hyperlinks and images on the page
        as a JPG to the provided directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        img_path = os.path.join(
            path,
            "illustration-%s.jpg" % self.archive_filename
        )
        self.write_illustration_to_path(img_path)
        return img_path

    def write_illustration_to_path(self, path):
        """
        Writes out a visualization of the hyperlinks and images on the page
        as a JPG to the provided path.
        """
        if os.path.exists(path):
            os.remove(path)
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
        im = self.timestamp_image(im)
        im.save(path, 'JPEG')

    def write_overlay_to_directory(
        self,
        path,
        stroke_width=4,
        stroke_padding=2
    ):
        """
        Writes out a screenshot of the page with overlays that emphasize
        the location of hyperlinks on the page as a JPG to the provided
        directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        overlay_path = os.path.join(
            path,
            "overlay-%s.png" % self.archive_filename
        )
        self.write_overlay_to_path(
            overlay_path,
            stroke_width=stroke_width,
            stroke_padding=stroke_padding
        )
        return overlay_path

    def write_overlay_to_path(
        self,
        path,
        stroke_width=4,
        stroke_padding=2
    ):
        """
        Writes out a screenshot of the page with overlays that emphasize
        the location of hyperlinks on the page as a JPG to the provided path.
        """
        if os.path.exists(path):
            os.remove(path)

        im = self.get_screenshot()

        # Cut out the boxes we'll want to highlight in the final image
        box_list = []
        for a in self.hyperlinks:
            if a.is_story:
                fill = "purple"
            else:
                fill = "blue"
            box = a.bounding_box
            stroke = (
                box[0][0] - stroke_padding,
                box[0][1] - stroke_padding,
                box[1][0] + stroke_padding,
                box[1][1] + stroke_padding
            )
            stroke = map(int, stroke)
            box_list.append(
                dict(
                    region=im.crop(stroke),
                    stroke=stroke,
                    fill=None,
                    outline=fill
                )
            )
        for i in self.images:
            box = i.bounding_box
            stroke = (
                box[0][0],
                box[0][1],
                box[1][0],
                box[1][1]
            )
            stroke = map(int, stroke)
            box_list.append(dict(
                region=im.crop(stroke),
                stroke=stroke,
                fill=None,
                outline="red"
            ))

        # Draw a transparent overlay and put it on the page
        overlay = PILImage.new(
            "RGBA",
            (self.screenshot.size[0], self.screenshot.size[1]),
            (0, 0, 0, 125)
        )
        im = PILImage.composite(overlay, im, overlay)

        # Now paste the story boxes back on top of the overlay
        draw = PILImageDraw.Draw(im)
        for box in box_list:
            im.paste(
                box['region'],
                (box['stroke'][0], box['stroke'][1])
            )
            for i in range(0, stroke_width+1):
                stroke = (
                    box['stroke'][0] - i,
                    box['stroke'][1] - i,
                    box['stroke'][2] + i,
                    box['stroke'][3] + i
                )
                draw.rectangle(
                    stroke,
                    fill=box['fill'],
                    outline=box['outline']
                )

        # Timestamp
        im = self.timestamp_image(im)

        # Save the image and pass out the path
        im.save(path, 'PNG')

    def write_href_overlay_to_directory(
        self,
        href,
        path,
        stroke_width=4,
        stroke_padding=2
    ):
        """
        Writes out a screenshot of the page with overlay that emphasize
        the location of a provide hyperlink as a PNG to the provided
        directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        overlay_path = os.path.join(
            path,
            "overlay-%s.png" % self.archive_filename
        )
        self.write_href_overlay_to_path(
            href,
            overlay_path,
            stroke_width=stroke_width,
            stroke_padding=stroke_padding
        )
        return overlay_path

    def write_href_overlay_to_path(
        self,
        href,
        path,
        duration=1,
        stroke_width=4,
        stroke_padding=2
    ):
        """
        Writes out overlay of a hyperlink's position on the page
        to the provided path.
        """
        if os.path.exists(path):
            os.remove(path)

        im = self.get_screenshot()

        # Cut out the box we'll want to highlight in the final image
        a = self.get_hyperlink_by_href(href)
        if a:
            if a.is_story:
                fill = "purple"
            else:
                fill = "blue"
            box = a.bounding_box
            stroke = (
                box[0][0] - stroke_padding,
                box[0][1] - stroke_padding,
                box[1][0] + stroke_padding,
                box[1][1] + stroke_padding
            )
            stroke = map(int, stroke)
            data = dict(
                region=im.crop(stroke),
                stroke=stroke,
                fill=None,
                outline=fill
            )

        # Draw a transparent overlay and put it on the page
        overlay = PILImage.new(
            "RGBA",
            (self.screenshot.size[0], self.screenshot.size[1]),
            (0, 0, 0, 125)
        )
        im = PILImage.composite(overlay, im, overlay)

        if a:
            # Now paste the story boxes back on top of the overlay
            draw = PILImageDraw.Draw(im)
            im.paste(
                data['region'],
                (data['stroke'][0], data['stroke'][1])
            )
            for i in range(0, stroke_width+1):
                stroke = (
                    data['stroke'][0] - i,
                    data['stroke'][1] - i,
                    data['stroke'][2] + i,
                    data['stroke'][3] + i
                )
                draw.rectangle(
                    stroke,
                    fill=data['fill'],
                    outline=data['outline']
                )

        # Timestamp
        im = self.timestamp_image(im)

        # Save the image and pass out the path
        im.save(path, 'PNG')


class ArchivedURLSet(collections.MutableSequence):
    """
    A list of archived URLs
    """
    def __init__(self, object_list):
        self._list = list()
        [self.append(o) for o in object_list]
        self._hyperlinks = list()

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __delitem__(self, ii):
        """Delete an item"""
        del self._list[ii]

    def __setitem__(self, ii, val):
        self._acl_check(val)
        return self._list[ii]

    def _url_check(self, obj):
        # Verify that the user is trying to add an ArchivedURL object
        if not isinstance(obj, ArchivedURL):
            raise TypeError("Only ArchivedURL objects can be added")

        # Check if the object is already in the list
        if obj in [o for o in list(self.__iter__())]:
            raise ValueError("This object is already in the list")

    def insert(self, ii, obj):
        self._url_check(obj)
        self._list.insert(ii, obj)

    def append(self, obj):
        self._url_check(obj)
        self._list.append(copy.copy(obj))

    def uniquify(self, seq):
        keys = {}
        for e in seq:
            keys[e] = 1
        return keys.keys()

    def analyze(self, force=False):
        """
        Force all of the normally lazy-loading analysis methods to run
        and cache the results.
        """
        [u.analyze(force=force) for u in self]

    #
    # Extract and analyze hyperlinks
    #

    def get_hyperlinks(self, force=False):
        """
        Parses all of the hyperlinks from the HTML of all the archived URLs
        and returns a list of the distinct href hyperlinks with a series
        of statistics attached that describe how they are
        positioned.
        """
        # If we already have the list, return it
        if self._hyperlinks and not force:
            return self._hyperlinks

        # Analyze hyperlinks for all of the URLs in the set
        [obj.analyze(force=False) for obj in self]

        # Create a list of all the unique href attributes
        all_hrefs = []
        for url in self:
            all_hrefs.extend([a.href for a in url.hyperlinks])
        unique_hrefs = self.uniquify(all_hrefs)

        # Loop through them all and run the numbers
        analyzed_list = []
        for href in unique_hrefs:
            # Find all the times it occurs
            url_hits, a_hits = [], []
            for url in self:
                this_a = url.get_hyperlink_by_href(href)
                if this_a:
                    url_hits.append(url)
                    a_hits.append(this_a)

            # Some basic stats
            archived_url_count = len(self)
            archived_urls_with_href = len(url_hits)

            # The earliest timestamp the link appeared
            earliest_timestamp = min([url.timestamp for url in url_hits])

            # The last timestamp the link appeared
            latest_timestamp = max([url.timestamp for url in url_hits])

            # The time delta between those two times
            timedelta = latest_timestamp - earliest_timestamp

            # Headlines
            headline_list = self.uniquify([a.string for a in a_hits])

            # Vertical position on the page
            y_list = [a.y for a in a_hits]
            maximum_y = max(y_list)
            minimum_y = min(y_list)
            if len(y_list) > 1:
                range_y = calculate.range(y_list)
                average_y = calculate.mean(y_list)
                median_y = calculate.median(y_list)
            else:
                range_y, average_y, median_y = None, None, None

            # Stuff it in the dict and pass it out
            d = dict(
                href=href,
                is_story=a_hits[0].is_story,
                archived_url_count=archived_url_count,
                archived_urls_with_href=archived_urls_with_href,
                earliest_timestamp=earliest_timestamp,
                latest_timestamp=latest_timestamp,
                timedelta=timedelta,
                headline_list=headline_list,
                maximum_y=maximum_y,
                minimum_y=minimum_y,
                range_y=range_y,
                average_y=average_y,
                median_y=median_y,
            )
            analyzed_list.append(d)
        self._hyperlinks = analyzed_list
        return analyzed_list
    hyperlinks = property(get_hyperlinks)

    @property
    def summary_statistics(self):
        """
        Returns a dictionary of summary statistics about the whole set
        of archived URLs.
        """
        # Analyze hyperlinks for all of the URLs in the set
        [obj.analyze(force=False) for obj in self]
        hyperlink_sets = [u.hyperlinks for u in self]
        story_link_sets = [u.story_links for u in self]
        image_sets = [u.images for u in self]
        unique_hyperlinks = self.hyperlinks
        unique_story_links = [h for h in self.hyperlinks if h['is_story']]
        summary_statistics = {
            'hyperlink_count_average': calculate.mean(
                [len(s) for s in hyperlink_sets]
            ),
            'hyperlink_count_median': calculate.median(
                [len(s) for s in hyperlink_sets]
            ),
            'hyperlink_count_min': min(
                [len(s) for s in hyperlink_sets]
            ),
            'hyperlink_count_max': max(
                [len(s) for s in hyperlink_sets]
            ),
            'hyperlink_count_range': calculate.range(
                [len(s) for s in hyperlink_sets]
            ),
            'hyperlink_timedelta_average': sum(
                [h['timedelta'] for h in unique_hyperlinks],
                timedelta()
            ) / len([h['timedelta'] for h in unique_hyperlinks]),
            'story_link_count_average': calculate.mean(
                [len(s) for s in story_link_sets]
            ),
            'story_link_count_median': calculate.median(
                [len(s) for s in story_link_sets]
            ),
            'story_link_count_min': min(
                [len(s) for s in story_link_sets]
            ),
            'story_link_count_max': max(
                [len(s) for s in story_link_sets]
            ),
            'story_link_count_range': calculate.range(
                [len(s) for s in story_link_sets]
            ),
            'story_link_timedelta_average': sum(
                [h['timedelta'] for h in unique_story_links],
                timedelta()
            ) / len([h['timedelta'] for h in unique_story_links]),
            'image_count_average': calculate.mean(
                [len(s) for s in image_sets]
            ),
            'image_count_median': calculate.median(
                [len(s) for s in image_sets]
            ),
            'image_count_min': min(
                [len(s) for s in hyperlink_sets]
            ),
            'image_count_max': max(
                [len(s) for s in image_sets]
            ),
            'image_count_range': calculate.range(
                [len(s) for s in image_sets]
            ),
        }
        return summary_statistics

    def write_hyperlinks_csv_to_file(self, file):
        """
        Returns the provided file object with a ready-to-serve CSV list of
        all hyperlinks extracted from the HTML.
        """
        # Create a CSV writer object out of the file
        writer = csv.writer(file)

        # Create the headers, which will change depending on how many
        # images are found in the urls
        headers = [
            "href",
            "is_story",
            "archived_url_count",
            "archived_urls_with_href",
            "earliest_timestamp",
            "latest_timestamp",
            "timedelta",
            "maximum_y",
            "minimum_y",
            "range_y",
            "average_y",
            "median_y",
        ]

        hyperlinks = self.hyperlinks
        max_headlines = max([h['headline_list'] for h in hyperlinks])
        for i in range(1, len(max_headlines) + 1):
            headers.append("headline_%s" % i)

        # Write it out to the file
        writer.writerow(headers)
        for h in hyperlinks:
            headline_list = h.pop("headline_list")
            row = list(
                map(six.text_type, [
                    h['href'],
                    h['is_story'],
                    h['archived_url_count'],
                    h['archived_urls_with_href'],
                    h['earliest_timestamp'],
                    h['latest_timestamp'],
                    h['timedelta'],
                    h['maximum_y'],
                    h['minimum_y'],
                    h['range_y'],
                    h['average_y'],
                    h['median_y'],
                ])
            )
            for hed in headline_list:
                row.append(six.text_type(hed))
            writer.writerow(row)

        # Reboot the file and pass it back out
        file.seek(0)
        return file

    def write_hyperlinks_csv_to_path(self, path):
        """
        Writes out a CSV of the hyperlinks extracted from the page to the
        provided file path.
        """
        f = open(path, "wb")
        self.write_hyperlinks_csv_to_file(f)

    def write_analysis_report_to_directory(self, path):
        """
        Create an analysis report that summarizes our outputs
        as an HTML package.
        """
        # Set up the directory where we will output the data
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        output_path = os.path.join(path, "urlsetanalysis-report")
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)

        # Write out the animation gifs
        self.write_overlay_animation_to_directory(output_path)
        self.write_illustration_animation_to_directory(output_path)

        # Write out reports for each item in the urlset
        for url in self:
            url.write_analysis_report_to_directory(output_path)

        # Write out hyperlinks csv
        hyperlinks_csv_path = os.path.join(output_path, "hyperlinks.csv")
        self.write_hyperlinks_csv_to_path(hyperlinks_csv_path)

        # Render report template
        context = {
            'object_list': self,
        }
        template = jinja.get_template('archivedurlset.html')
        html = template.render(**context)

        # Write out to file
        file = open(os.path.join(output_path, "index.html"), "wb")
        file.write(html)
        file.close()

    def print_href_analysis(self, href):
        """
        Outputs a human-readable analysis of the submitted href's position
        across the set of archived URLs.
        """
        hyperlink_dict = dict((h['href'], h) for h in self.get_hyperlinks())
        try:
            stats = hyperlink_dict[href]
        except KeyError:
            raise ValueError("href could not be found in archived URL set")

        print href
        print ""

        table = indent(
            [
                ['Statistic', 'Value'],
                ['Archived URL count', str(stats['archived_url_count'])],
                [
                    'Archived URLs with href',
                    str(stats['archived_urls_with_href'])
                ],
                ['First timestamp', str(stats['earliest_timestamp'])],
                ['Last timestamp', str(stats['latest_timestamp'])],
                ['Timedelta', str(stats['timedelta'])],
                ['Maximum y position', str(stats['maximum_y'])],
                ['Minimum y position', str(stats['minimum_y'])],
                ['Range of y positions', str(stats['range_y'])],
                ['Average y position', str(stats['average_y'])],
                ['Median y position', str(stats['median_y'])],
            ],
            hasHeader=True,
            separateRows=False,
            prefix="| ", postfix=" |",
        )
        print table

        headline_table = [['Headline']]
        for hed in stats['headline_list']:
            headline_table.append([hed])
        table = indent(
            headline_table,
            hasHeader=True,
            separateRows=False,
            prefix="| ", postfix=" |",
        )
        print table

    #
    # Overlays and illustractions
    #

    def fit_image_list(self, img_list):
        """
        Accepts a list of PIL image objects and pastes them
        onto a backgrounds of an identical size.

        Intended to prep images to be combined into an animated GIF.
        """
        # Figure out the biggest one
        max_width = max([i.size[0] for i in img_list])
        max_height = max([i.size[1] for i in img_list])

        # Loop through the images
        paste_list = []
        for img in img_list:
            # Paste them onto a background of the same size as the largest
            # one in the set
            paste = PILImage.new(
                "RGBA",
                (max_width, max_height),
                (255, 255, 255, 255)
            )
            paste.paste(img, (0, 0))
            paste_list.append(paste)

        # Pass the list back
        return paste_list

    def write_overlay_animation_to_directory(self, path, duration=1):
        """
        Writes out animation of the pages
        as a GIF to the provided directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        gif_path = os.path.join(path, "urlset-overlay.gif")
        self.write_overlay_animation_to_path(gif_path, duration=duration)
        return gif_path

    def write_overlay_animation_to_path(self, path, duration=1):
        """
        Writes out animation of the pages
        as a GIF to the provided path.
        """
        jpg_paths = []
        tmpdir = tempfile.mkdtemp()
        for page in self:
            jpg_path = page.write_overlay_to_directory(tmpdir)
            jpg_paths.append(jpg_path)

        img_list = []
        for jpg in jpg_paths:
            this_img = PILImage.open(jpg)
            img_list.append(this_img)

        img_list = self.fit_image_list(img_list)

        # Create the GIF animation
        if os.path.exists(path):
            os.remove(path)
        images2gif.writeGif(path, img_list, duration=duration)

        # Delete all the jpgs
        for jpg in jpg_paths:
            os.remove(jpg)

    def write_illustration_animation_to_directory(self, path, duration=1):
        """
        Writes out animation of the pages as a GIF to the provided directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        gif_path = os.path.join(path, "urlset-illustration.gif")
        self.write_illustration_animation_to_path(gif_path, duration=duration)
        return gif_path

    def write_illustration_animation_to_path(self, path, duration=1):
        """
        Writes out animation of the pages as a GIF to the provided path.
        """
        jpg_paths = []
        tmpdir = tempfile.mkdtemp()
        for page in self:
            jpg_path = page.write_illustration_to_directory(tmpdir)
            jpg_paths.append(jpg_path)

        img_list = []
        for jpg in jpg_paths:
            img_list.append(PILImage.open(jpg))

        img_list = self.fit_image_list(img_list)

        # Create the GIF animation
        if os.path.exists(path):
            os.remove(path)
        images2gif.writeGif(path, img_list, duration=duration)

        # Delete all the jpgs
        for jpg in jpg_paths:
            os.remove(jpg)

    def write_href_illustration_animation_to_directory(
        self,
        href,
        path,
        duration=1
    ):
        """
        Writes out animation of a hyperlinks on the page
        as a GIF to the provided directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        gif_path = os.path.join(path, "urlset-href-illustration.gif")
        self.write_href_illustration_animation_to_path(
            href,
            gif_path,
            duration=duration
        )
        return gif_path

    def write_href_illustration_animation_to_path(
        self,
        href,
        path,
        duration=1
    ):
        """
        Writes out animation of a hyperlinks on the page
        as a GIF to the provided path.
        """
        jpg_paths = []
        tmpdir = tempfile.mkdtemp()
        for page in self:
            jpg_path = os.path.join(
                tmpdir,
                "%s.jpg" % page.archive_filename
            )
            if os.path.exists(jpg_path):
                os.remove(jpg_path)
            im = PILImage.new(
                "RGBA",
                (page.width, page.height),
                (221, 221, 221, 255)
            )
            draw = PILImageDraw.Draw(im)
            a = page.get_hyperlink_by_href(href)
            if a:
                if a.is_story:
                    fill = "purple"
                else:
                    fill = "blue"
                draw.rectangle(a.bounding_box, fill=fill)
            im.save(jpg_path, 'JPEG')
            jpg_paths.append(jpg_path)

        img_list = []
        for jpg in jpg_paths:
            img_list.append(PILImage.open(jpg))

        img_list = self.fit_image_list(img_list)

        # Create the GIF animation
        if os.path.exists(path):
            os.remove(path)
        images2gif.writeGif(path, img_list, duration=duration)

        # Delete all the jpgs
        for jpg in jpg_paths:
            os.remove(jpg)

    def write_href_overlay_animation_to_directory(
        self,
        href,
        path,
        duration=1
    ):
        """
        Writes out animation of a hyperlink's position on the page
        as a GIF to the provided directory.
        """
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        gif_path = os.path.join(path, "urlset-href-overlay.gif")
        self.write_href_overlay_animation_to_path(
            href,
            gif_path,
            duration=duration
        )
        return gif_path

    def write_href_overlay_animation_to_path(
        self,
        href,
        path,
        duration=1,
        stroke_width=4,
        stroke_padding=2
    ):
        """
        Writes out animation of a hyperlink's position on the page
        as a GIF to the provided path.
        """
        if os.path.exists(path):
            os.remove(path)

        png_paths = []
        tmpdir = tempfile.mkdtemp()
        for page in self:
            png_path = page.write_href_overlay_to_directory(href, tmpdir)
            png_paths.append(png_path)

        img_list = []
        for png in png_paths:
            this_img = PILImage.open(png)
            img_list.append(this_img)

        # Fit them all onto backgrounds of the same size
        img_list = self.fit_image_list(img_list)

        # Create the GIF animation
        if os.path.exists(path):
            os.remove(path)
        images2gif.writeGif(path, img_list, duration=duration)

        # Delete all the jpgs
        for png in png_paths:
            os.remove(png)


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

    @property
    def area(self):
        """
        Returns the area of the image
        """
        if not self.width or not self.height:
            return None
        return self.width * self.height


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
