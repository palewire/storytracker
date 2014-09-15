#!/usr/bin/env python
import storytracker
import dateutil.parser
from .analysis import ArchivedURL


def open_wayback_machine_url(url, **kwargs):
    """
    Accepts an URL from the Internet Archive's Wayback Machine
    and returns an ArchivedURL object
    """
    # Extract the URL and timestamp from the url
    archive_url, timestamp = storytracker.reverse_wayback_machine_url(url)
    # Modify the standard Wayback Machine URL to be one that returns the raw
    # HTML without any of the chrome and navigation tools inserted by
    # the archive
    if "id_" not in url:
        url = url.replace(
            "/%s" % archive_url,
            "id_/%s" % archive_url
        )
    # Retrieve the raw HTML
    html = storytracker.archive(url, **kwargs).html
    # Pass it all back
    return ArchivedURL(archive_url, timestamp, html)


def reverse_wayback_machine_url(url):
    """
    Accepts an url from the Internet Archive's Wayback Machine
    and returns a tuple with:

        (<The URL of the archived site>, <Timestamp of when it was archived>)
    """
    try:
        url = url.replace("https://web.archive.org/web/", "")
        timestamp_string, url_string = url.split("/", 1)
        return (
            url_string,
            dateutil.parser.parse(timestamp_string)
        )
    except:
        raise storytracker.ArchiveFileNameError(
            "Archive file name could not be parsed from %s:" % url
        )
