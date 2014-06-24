import six
import gzip
import htmlmin
import requests
from bs4 import BeautifulSoup
from six import BytesIO
from six.moves.urllib_parse import urljoin, urlparse

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


def get(url, verify=True):
    """
    Get the HTML at the provided URL
    """
    # Request the URL
    response = requests.get(url)
    html = response.text
    # Verify that the response is in fact HTML (but option to skip test)
    if verify and 'html' not in response.headers['content-type']:
        raise ValueError("Response does not have an HTML content-type")
    return html


def archive(
    url, verify=True, minify=True, extend_urls=True, compress=True,
    output_path=None
        ):
    """
    Archive the provided HTML
    """
    # Get the html
    html = get(url, verify=verify)
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
    # Compress the data somehow to zlib or gzip or whatever
    if compress:
        if output_path:
            with gzip.GzipFile(fileobj=open(output_path, 'wb'), mode="w") as f:
                f.write(html.encode("utf-8"))
        else:
            # If no output path then pass out gzipped raw data
            out = BytesIO()
            with gzip.GzipFile(fileobj=out, mode="wb") as f:
                f.write(html.encode("utf-8"))
            return out.getvalue()
    else:
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(html.encode("utf-8"))
        else:
            return html
