#!/usr/bin/env python
import six
import pytz
import logging
import htmlmin
import storytracker
from datetime import datetime
from bs4 import BeautifulSoup
try:
    from urlparse import urljoin
except ImportError:
    from six.moves.urllib.parse import urljoin
logger = logging.getLogger(__name__)


# A list of all the other resources in the page we need to pull out
# in a format the BeautifulSoup is ready to work with.
COMMON_HYPERLINK_LOCATIONS = (
    # images
    {"tag": ("img", {"src": True}), "attr": "src"},
    # css
    {"tag": ("link", {"rel": "stylesheet"}), "attr": "href"},
    # css
    {"tag": ("link", {"type": "text/css"}), "attr": "href"},
    # javascript
    {"tag": ("script", {"src": True}), "attr": "src"},
    # hyperlinks
    {"tag": ("a", {"href": True}), "attr": "href"},
)


def archive(
    url, verify=True, minify=True, extend_urls=True, compress=True,
    output_dir=None
        ):
    """
    Archive the HTML from the provided URL
    """
    logger.debug("Archiving URL: %s" % url)

    # Get the html
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    html = storytracker.get(url, verify=verify)

    # Minify the html (but option to skip)
    if minify:
        html = htmlmin.minify(html)

    # Replace all relative URLs with absolute URLs, if called for
    if extend_urls:
        soup = BeautifulSoup(html)
        for target in COMMON_HYPERLINK_LOCATIONS:
            for hit in soup.findAll(*target['tag']):
                hit[target['attr']] = urljoin(url, hit[target['attr']])
        html = six.text_type(soup)

    # Create an URLArchive object
    obj = storytracker.ArchivedURL(url, now, html)

    # If a custom output dir is provided put everything in there
    if output_dir:
        logger.debug("Writing file to %s" % output_dir)
        if compress:
            obj.write_gzip_to_directory(output_dir)
        else:
            obj.write_html_to_directory(output_dir)

    # Return ArchivedURL object
    return obj
