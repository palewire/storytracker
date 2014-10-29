#!/usr/bin/env python
import gzip
import requests
import storytracker
from six import BytesIO
from .analysis import ArchivedURL


def open_pastpages_url(url, **kwargs):
    """
    Accepts an URL from PastPages and returns an ArchivedURL object if
    there is an HTML archive
    """
    # Break out the unique ID for the page from the URL
    id_ = url.split(
        "http://www.pastpages.org/screenshot/"
    )[1].replace("/", "")
    # Use that request the HTML archive url from the API
    html_url = requests.get(
        "http://www.pastpages.org/api/beta/screenshots/%s/" % id_
    ).json()['html']
    # Extract the URL and timestamp from the url
    html_filename = html_url.split("/html/")[1].replace(".gz", "")
    archive_url, timestamp = storytracker.reverse_archive_filename(
        html_filename
    )
    # Get the archived HTML data
    gzipped = requests.get(html_url).content
    html = gzip.GzipFile(fileobj=BytesIO(gzipped)).read().decode("utf-8")
    # Pass it all back
    return ArchivedURL(archive_url, timestamp, html)
