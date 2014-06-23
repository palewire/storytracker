import htmlmin
import requests
from urlparse import urljoin
from bs4 import BeautifulSoup


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


def archive(url, verify=True, minify=True, extend_urls=True):
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
        # A list of all the other resources in the page we need to pull out
        target_list = (
            # images
            {"tag": ("img", {"src": True}), "attr": "src"},
            # css
            {"tag": ("link", {"rel": "stylesheet"}), "attr": "href"},
            # css
            {
                "tag": ("link", {
                    "rel": "alternate stylesheet",
                    "type": "text/css"
                }),
                "attr": "href"
            },
            # javascript
            {"tag": ("script", {"src": True}), "attr": "src"},
            # hyperlinks
            {"tag": ("a", {"href": True}), "attr": "href"},
        )
        soup = BeautifulSoup(html)
        for target in target_list:
            for hit in soup.findAll(*target['tag']):
                link = hit.get(target['attr'])
                # Here's where they actually get replaced
                archive_link = urljoin(url, link)
                if link != archive_link:
                    html.replace(str(link), str(archive_link))
    # If opt-in download all third-party assets
    # Compress the data somehow to zlib or gzip or whatever
    # Pass it back

    # Save it via Django storages?
    # (But not if you're using the CLI)
    # (And maybe this should be a custom Django field? models.HTMLArchiveField())
    ## It would save the contents of an URL as a media upload to your storage
    ## Before it wrote the file it would verify that it is in fact HTML
    ## And when you pull it out Python it would return some kind of object
    ##   rather than just raw HTML (But do we want that?)
    ## What should be the default way to save the upload? url + timestamp?
    return html
