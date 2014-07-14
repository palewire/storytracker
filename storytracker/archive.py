#!/usr/bin/env python
import os
import six
import gzip
import pytz
import logging
import htmlmin
import storytracker
from six import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup
from .analysis import ArchivedURL
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
    # If a custom output dir is provided put everything in there
    if output_dir:
        logger.debug("Writing file to %s" % output_dir)
        output_filename = storytracker.create_archive_filename(url, now)
        output_path = os.path.join(output_dir, output_filename)
        if compress:
            fileobj = open("%s.gz" % output_path, 'wb')
            with gzip.GzipFile(fileobj=fileobj, mode="wb") as f:
                f.write(html.encode("utf-8"))
            return "%s.gz" % output_path
        else:
            with open("%s.html" % output_path, 'wb') as f:
                f.write(html.encode("utf-8"))
            return "%s.html" % output_path
    # If not, return the  data so it can be passed on
    else:
        if compress:
            out = BytesIO()
            with gzip.GzipFile(fileobj=out, mode="wb") as f:
                f.write(html.encode("utf-8"))
            return out.getvalue()
        else:
            return html.encode("utf-8")
