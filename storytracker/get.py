#!/usr/bin/env python
import logging
import requests
logger = logging.getLogger(__name__)


def get(url, verify=True, user_agent="PhantomJS"):
    """
    Retrieves HTML from the provided URL.
    """
    # Request the URL
    logger.debug("Requesting %s" % url)
    response = requests.get(url)

    # If the reqest returns a 4XX or 5XX response, try again with a user agent
    if not response.status_code == requests.codes.ok:
        logger.debug("Request returned a %d error, trying again with %s user-agent" % (response.status_code, user_agent))
        response = requests.get(url, headers={'User-Agent': user_agent})
        logger.debug("Second Request returned a %d" % response.status_code)

    html = response.text
    # Verify that the response is in fact HTML (but option to skip test)
    if verify and 'html' not in response.headers['content-type']:
        raise ValueError("Response does not have an HTML content-type")
    return html
