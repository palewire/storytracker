Archival tools
==============

Command-line interfaces you can use to download and save URLs.

storytracker-archive
--------------------

Archive the HTML from the provided URLs::

    Usage: storytracker-archive [URL]... [OPTIONS]

    Archive the HTML from the provided URLs

    Options:
      -h, --help            show this help message and exit
      -v, --do-not-verify   Skip verification that HTML is in the response's
                            content-type header
      -m, --do-not-minify   Skip minification of HTML response
      -e, --do-not-extend-urls
                            Do not extend relative urls discovered in the HTML
                            response
      -c, --do-not-compress
                            Skip compression of the HTML response
      -d OUTPUT_DIR, --output-dir=OUTPUT_DIR
                            Provide a directory for the archived data to be stored

Example usage:

.. code-block:: bash

    # This will pipe out gzipped content of the page to stdout
    $ storytracker-archive http://www.latimes.com

    # You can save it to an automatically named file a directory you provide
    $ storytracker-archive http://www.latimes.com -d ./

    # If you'd prefer to have the HTML without compress
    $ storytracker-archive http://www.latimes.com -c

    # Which of course can be piped into other commands like anything else
    $ storytracker-archive http://www.latimes.com -cm | grep lakers


storytracker-get
----------------

Retrieves HTML from the provided URLs::

    Usage: storytracker-get [URL]... [OPTIONS]

    Retrieves HTML from the provided URLs

    Options:
      -h, --help           show this help message and exit
      -v, --do-not-verify  Skip verification that HTML is in the response's
                           content-type header

It works like this

.. code-block:: bash

    # Download an url like this
    $ storytracker-get http://www.latimes.com

    # Or two like this
    $ storytracker-get http://www.latimes.com http://www.columbiamissourian.com

