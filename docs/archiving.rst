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
