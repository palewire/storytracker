Archival tools
==============

Command-line interfaces you can use to download and save URLs.

archive
-------

Archive the HTML from the provided URLs

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

Python interface
~~~~~~~~~~~~~~~~

.. py:function:: storytracker.archive(url, verify=True, minify=True, extend_urls=True, compress=True, output_dir=None)

   :param str url: The URL of the page to archive
   :param bool verify: Verify that HTML is in the response's content-type header
   :param bool minify: Minify the HTML response to reduce its size
   :param bool extend_urls: Extend relative URLs discovered in the HTML response to be absolute3
   :param bool compress: Compress the HTML response using gzip
   :param output_dir: Provide a directory for the archived data to be stored
   :type output_dir: str or None
   :return: The content of the HTML response, unless an output directory is provided.
   :rtype: str or None
   :raises ValueError: If the response is not verified as HTML

Example usage:

.. code-block:: python

    >>> import storytracker

    >>> # This will return gzipped content of the page to the variable
    >>> data = storytracker.archive("http://www.latimes.com")

    >>> # You can save it to an automatically named file a directory you provide
    >>> storytracker.archive(http://www.latimes.com, output_dir="./")

    >>> # If you'd prefer to have the HTML without compression
    >>> data = storytracker.archive("http://www.latimes.com", compress=False)


create_archive_filename
-----------------------

Returns a string that combines a URL and a timestamp of for naming archives saved to the filesystem.

.. py:function:: storytracker.create_archive_filename(url, timestamp)

    :param str url: The URL of the page that is being archived
    :param datetime timestamp: A timestamp recording approximately when the URL was archive
    :return: A string that combines the two arguments into a structure can be reversed back into Python
    :rtype: str

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> from datetime import datetime
    >>> storytracker.create_archive_filename("http://www.latimes.com", datetime.now())
    'http-www.latimes.com----@2014-06-30T21:43:15.775071'

get
---

Retrieves HTML from the provided URLs

Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

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


Python interface
~~~~~~~~~~~~~~~~

.. py:function:: storytracker.get(url, verify=True)

   :param str url: The URL of the page to archive
   :param bool verify: Verify that HTML is in the response's content-type header
   :return: The content of the HTML response
   :rtype: str
   :raises ValueError: If the response is not verified as HTML


reverse_archive_filename
------------------------

Returns a string that combines a URL and a timestamp of for naming archives saved to the filesystem.

.. py:function:: storytracker.reverse_archive_filename(filename)

    :param str filename: A filename structured using the style of the :py:func:`storytracker.create_archive_filename` function
    :return: A tuple containing the URL of the archived page as a string and a datetime object of the archive's timestamp 
    :rtype: tuple

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> storytracker.reverse_archive_filename('http-www.latimes.com----@2014-06-30T21:43:15.775071')
    ('http://www.latimes.com', datetime.datetime(2014, 6, 30, 21, 43, 15, 775071))
