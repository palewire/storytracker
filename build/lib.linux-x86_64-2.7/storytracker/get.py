#!/usr/bin/env python
import logging
import requests
logger = logging.getLogger(__name__)


def get(url, verify=True):
    """
    Retrieves HTML from the provided URL.
    """
    # Request the URL
    logger.debug("Requesting %s" % url)
    response = requests.get(url)
    html = response.text
    # Verify that the response is in fact HTML (but option to skip test)
    if verify and 'html' not in response.headers['content-type']:
        raise ValueError("Response does not have an HTML content-type")
    return html
