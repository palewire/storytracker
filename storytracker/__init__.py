import htmlmin
import requests


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


def archive(html, minify=True):
    """
    Archive the provided HTML
    """
    # Minify the html (but option to skip)
    if minify:
        html = htmlmin.minify(html)
    # Replace all relative URLs with absolute URLs
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
