#!/usr/bin/env python
import os
import six
import gzip
import htmlmin
import storytracker
import dateutil.parser
from six import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup
from six.moves.urllib.parse import urlparse, urlunparse, urljoin


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
    # Get the html
    now = datetime.now()
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
        output_filename = create_archive_filename(url, now)
        output_path = os.path.join(output_dir, output_filename)
        if compress:
            fileobj = open("%s.gz" % output_path, 'wb')
            with gzip.GzipFile(fileobj=fileobj, mode="wb") as f:
                f.write(html.encode("utf-8"))
            return
        else:
            with open("%s.html" % output_path, 'wb') as f:
                f.write(html.encode("utf-8"))
            return
    # If not, return the data so it can be passed on
    else:
        if compress:
            out = BytesIO()
            with gzip.GzipFile(fileobj=out, mode="wb") as f:
                f.write(html.encode("utf-8"))
            return out.getvalue()
        else:
            return html.encode("utf-8")


def create_archive_filename(url, timestamp):
    """
    Returns a string that combines a URL and the timestamp of when it was
    harvested for use when naming archives that are saved to disk.
    """
    urlparts = "-".join(urlparse(url))
    return "%s@%s" % (
        urlparts,
        timestamp.isoformat()
    )


def reverse_archive_filename(filename):
    """
    Accepts a filename created using the rules of ``create_archive_filename``
    and converts it back to Python. Returns a tuple: The URL string and a
    timestamp. Do not include the file extension when providing a string.
    """
    url_string, timestamp_string = filename.split("@")
    return (
        urlunparse(url_string.split("-")),
        dateutil.parser.parse(timestamp_string)
    )
