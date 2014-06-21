import htmlmin
import requests



def get(url):
    """
    Archive the HTML page at the provided URL.
    """
    # Request the URL
    response = requests.get(url)
    return htmlmin.minify(response.text)
    # Verify that the response is in fact HTML (but option to skip test)
    # Minify the html (but option to skip)
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
    return False
