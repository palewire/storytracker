import os
import gzip


def open_archive_filepath(path):
    """
    Accepts a file path and returns a file object ready for analysis
    """
    # Split the file extension from the name
    name, ext = os.path.splitext(path)
    # If it is gzipped, then open it that way
    if ext == '.gz':
        obj = gzip.open(path)
    # Otherwise handle it normally
    else:
        obj = open(path, "rb")
    return obj
