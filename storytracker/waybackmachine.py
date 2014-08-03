#!/usr/bin/env python
import storytracker
import dateutil.parser


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
    except Exception as e:
        raise storytracker.ArchiveFileNameError(
            "Archive file name could not be parsed from %s:" % url
        )
