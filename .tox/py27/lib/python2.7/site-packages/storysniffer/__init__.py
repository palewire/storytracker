#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import tldextract
try:
    from urlparse import urlparse
except ImportError:
    from six.moves.urllib.parse import urlparse

# A regular expression that can validate URLs
# Drawn from Django source code:
# https://github.com/django/django/blob/master/django/core/validators.py
URL_REGEX = re.compile(
    r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|\
[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

# A list of URL parts that probably won't link to new stories
DOMAIN_BLACKLIST = (
    'google',
    'twitter',
    'facebook',
    'doubleclick',
)

SUBDOMAIN_BLACKLIST = (
    'careers',
    'mail',
    'account',
)

TLD_BLACKLIST = (
    'xxx',
)

PATH_BLACKLIST = (
    '',
    '/',
)

EXT_BLACKLIST = (
    '.js',
    '.css',
    '.jpg',
    '.gif',
    '.png',
)

# A list of URL parts we think will link to stories
PATHPART_WHITELIST = [
    'story', 'article', 'feature', 'featured', 'blog', 'interactive',
    'graphic', 'video',
]


def guess(url):
    """
    Returns a boolean estimating the likelihood that
    the provided URL links to a news story.
    """
    # Throw an error if the URL doesn't match acceptable patterns
    if not URL_REGEX.search(url):
        raise ValueError("Provided url does not match acceptable URL patterns")

    # Parse the url into parts so we can inspect them
    urlparts = urlparse(url)
    tldparts = tldextract.extract(url)

    # Kill anything in one of our blacklists
    if urlparts.path in PATH_BLACKLIST:
        return False

    if tldparts.domain in DOMAIN_BLACKLIST:
        return False

    if tldparts.subdomain in SUBDOMAIN_BLACKLIST:
        return False

    if tldparts.suffix in TLD_BLACKLIST:
        return False

    if os.path.splitext(urlparts.path)[1] in EXT_BLACKLIST:
        return False

    # We don't like things with very few slashes in the urls URL paths
    pathparts = [x for x in urlparts.path.split('/') if x.strip()]
    if len(pathparts) < 2:
        return False

    # Bless anything that matches one of our patterns
    # ... like lots of dashes or underscores in a path part
    if max(p.count('-') for p in pathparts) > 3:
        return True

    if max(p.count('_') for p in pathparts) > 3:
        return True

    if any(p in PATHPART_WHITELIST for p in pathparts):
        return True

    # If you've made it this far without clicking, we give up
    return False
