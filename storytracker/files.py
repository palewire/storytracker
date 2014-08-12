#!/usr/bin/env python
import os
import gzip
import storytracker
import dateutil.parser
from .analysis import ArchivedURL, ArchivedURLSet
try:
    from urlparse import urlunparse, urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse, urlunparse


def create_archive_filename(url, timestamp):
    """
    Returns a string that combines a URL and the timestamp of when it was
    harvested for use when naming archives that are saved to disk.
    """
    # Pull apart the URL into parts
    urlparts = urlparse(url)
    # Replace any slashes with a rare character like the "|" pipe.
    urlparts = [p.replace("/", "|") for p in urlparts]
    # Join the parts together into one string with a bang "!" as the seperator
    urlparts = "!".join(urlparts)
    # Now join it with the timestamp with an at "@" sign seperator
    return "%s@%s" % (
        urlparts,
        timestamp.isoformat()
    )


def open_archive_directory(path):
    """
    Accepts a directory path and returns an ArchivedURLSet object
    """
    # Make sure it's a directory
    if not os.path.isdir(path):
        raise ValueError("Path must be a directory")

    # Loop through the directory and pull the data
    urlset = ArchivedURLSet([])
    for root, dirs, files in os.walk(path):
        for name in files:
            path = os.path.join(root, name)
            try:
                obj = open_archive_filepath(path)
            except storytracker.ArchiveFileNameError:
                continue
            urlset.append(obj)

    # Pass it back out
    return urlset


def open_archive_filepath(path):
    """
    Accepts a file path and returns an ArchivedURL object
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
    return ArchivedURL(
        url,
        timestamp,
        obj.read().decode("utf-8"),
        archive_path=path
    )


def reverse_archive_filename(filename):
    """
    Accepts a filename created using the rules of ``create_archive_filename``
    and converts it back to Python. Returns a tuple: The URL string and a
    timestamp. Do not include the file extension when providing a string.
    """
    try:
        url_string, timestamp_string = filename.split("@")
        urlparts = url_string.split("!")
        urlparts = [p.replace("|", "/") for p in urlparts]
        return (
            urlunparse(urlparts),
            dateutil.parser.parse(timestamp_string)
        )
    except:
        raise storytracker.ArchiveFileNameError(
            "Archive file name could not be parsed from %s:" % filename
        )
