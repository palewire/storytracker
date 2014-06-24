import sys
import requests
import optparse


def get(url, verify=True):
    """
    Retrieves HTML from the provided URL.
    """
    # Request the URL
    response = requests.get(url)
    html = response.text
    # Verify that the response is in fact HTML (but option to skip test)
    if verify and 'html' not in response.headers['content-type']:
        raise ValueError("Response does not have an HTML content-type")
    return html



def main():
    """
    A command-line interface to this method.
    """
    p = optparse.OptionParser(
        description="Retrieves HTML from the provided URL.",
        usage="storytracker-get [URL]... [OPTIONS]",
    )
    p.add_option(
        "--do-not-verify",
        "-v",
        action="store_false",
        dest="verify",
        default=True,
        help="Skip verification that HTML is in the response's \
content-type header"
    )
    options, arguments = p.parse_args()
    for a in arguments:
        html = get(a, verify=options.verify)
        sys.stdout.write(html.encode("utf-8"))


if __name__ == '__main__':
    main()
