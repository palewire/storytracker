Archiving
=========

Tools to download and save URLs.

archive
-------

Archive the HTML from the provided URLs

.. py:function:: storytracker.archive(url, verify=True, minify=True, extend_urls=True, compress=True, output_dir=None)

   :param str url: The URL of the page to archive
   :param bool verify: Verify that HTML is in the response's content-type header
   :param bool minify: Minify the HTML response to reduce its size
   :param bool extend_urls: Extend relative URLs discovered in the HTML response to be absolute
   :param bool compress: Compress the HTML response using gzip if an ``output_dir`` is provided
   :param output_dir: Provide a directory for the archived data to be stored
   :type output_dir: str or None
   :return: An :py:class:`ArchivedURL` object 
   :rtype: :py:class:`ArchivedURL`
   :raises ValueError: If the response is not verified as HTML

Example usage:

.. code-block:: python

    >>> import storytracker

    >>> # This will return gzipped content of the page to the variable
    >>> obj = storytracker.archive("http://www.latimes.com")
    <ArchivedURL: http://www.latimes.com@2014-07-17 04:08:32.169810+00:00>

    >>> # You can save it to an automatically named file a directory you provide
    >>> obj = storytracker.archive("http://www.latimes.com", output_dir="./")
    >>> obj.archive_path
    './http!www.latimes.com!!!!@2014-07-17T04:09:21.835271+00:00.gz'

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

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

    # If you'd prefer to have the HTML without compression
    $ storytracker-archive http://www.latimes.com -c

    # Which of course can be piped into other commands like anything else
    $ storytracker-archive http://www.latimes.com -cm | grep lakers

get
---

Retrieves HTML from the provided URLs

.. py:function:: storytracker.get(url, verify=True)

   :param str url: The URL of the page to archive
   :param bool verify: Verify that HTML is in the response's content-type header
   :return: The content of the HTML response
   :rtype: ``str``
   :raises ValueError: If the response is not verified as HTML

Example usage:

.. code-block:: python

    >>> import storytracker

    >>> html = storytracker.get("http://www.latimes.com")

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    Usage: storytracker-get [URL]... [OPTIONS]

    Retrieves HTML from the provided URLs

    Options:
      -h, --help           show this help message and exit
      -v, --do-not-verify  Skip verification that HTML is in the response's
                           content-type header

It works like this:

.. code-block:: bash

    # Download an url like this
    $ storytracker-get http://www.latimes.com

    # Or two like this
    $ storytracker-get http://www.latimes.com http://www.columbiamissourian.com
