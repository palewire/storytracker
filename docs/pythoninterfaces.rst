=================
Python interfaces
=================

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

Analysis
========

ArchivedURL
-----------

An URL's archived HTML with tools for analysis.

.. py:class:: ArchivedURL(url, timestamp, html)

    **Initialization arguments**

    .. py:attribute:: url

        The url archived

    .. py:attribute:: timestamp

        The date and time when the url was archived

    .. py:attribute:: html

        The HTML archived

    **Other attributes**

    .. py:attribute:: gzip

        Returns the archived HTML as a stream of gzipped data

    .. py:attribute:: archive_filename

        Returns a file name for this archive using the conventions of :py:func:`storytracker.create_archive_filename`.

    .. py:attribute:: soup

        The archived HTML passed into a `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/bs4/doc/#>`_ parser

    .. py:attribute:: hyperlinks

        A list of all the hyperlinks extracted from the HTML

    .. py:attribute:: images

        A list of all the images extracts from the HTML

    **Output methods**

    .. py:attribute:: write_hyperlinks_csv_to_file(file, encoding="utf-8")

        Returns the provided file object with a ready-to-serve CSV list of
        all hyperlinks extracted from the HTML.

    .. py:method:: write_gzip_to_directory(path)

        Writes gzipped HTML data to a file in the provided directory path

    .. py:method:: write_html_to_directory(path)

        Writes HTML data to a file in the provided directory path

Example usage:

.. code-block:: python

    >>> import storytracker

    >>> obj = storytracker.open_archive_filepath('/home/ben/archive/http!www.latimes.com!!!!@2014-07-06T16:31:57.697250.gz')
    >>> obj.url
    'http://www.latimes.com'

    >>> obj.timestamp
    datetime.datetime(2014, 7, 6, 16, 31, 57, 697250)

ArchivedURLSet
--------------

A list of :py:class:`ArchivedURL` objects.

.. py:class:: ArchivedURLSet(list)

    List items added to the set must be unique :py:class:`ArchivedURL` objects.

Example usage:

.. code-block:: python

    >>> import storytracker

    >>> obj_list = storytracker.open_archive_directory('/home/ben/archive/')

    >>> obj_list[0].url
    'http://www.latimes.com'

    >>> obj_list[1].timestamp
    datetime.datetime(2014, 7, 6, 16, 31, 57, 697250)

Hyperlink
---------

A hyperlink extracted from an :py:class:`ArchivedURL` object.

.. py:class:: Hyperlink(href, string, index, images=[])

    **Initialization arguments**

    .. py:attribute:: href

        The URL the hyperlink references

    .. py:attribute:: string

        The strings contents of the anchor tag

    .. py:attribute:: index

        The index value of the links order within its source HTML. Starts counting at zero.

    .. py:attribute:: images

        A list of the :py:class:`Image` objects extracted from the HTML

    **Other attributes**

    .. py:attribute:: __csv__

        Returns a list of values ready to be written to a CSV file object

    .. py:attribute:: domain

        The domain of the href

Image
-----

.. py:class:: Image(src)

    An image extracted from an archived URL.

    **Initialization arguments**

    .. py:attribute:: src

        The ``src`` attribute of the image tag

File handling
=============

Functions for naming, saving and retrieving archived URLs.

create_archive_filename
-----------------------

Returns a string that combines a URL and a timestamp of for naming archives saved to the filesystem.

.. py:function:: storytracker.create_archive_filename(url, timestamp)

    :param str url: The URL of the page that is being archived
    :param datetime timestamp: A timestamp recording approximately when the URL was archive
    :return: A string that combines the two arguments into a structure can be reversed back into Python
    :rtype: ``str``

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> from datetime import datetime
    >>> storytracker.create_archive_filename("http://www.latimes.com", datetime.now())
    'http!www.latimes.com!!!!@2014-07-06T16:31:57.697250'


open_archive_directory
----------------------

Accepts a directory path and returns an :py:class:`ArchivedURLSet` list filled with an :py:class:`ArchivedURL`
object that corresponds to every archived file it finds.


.. py:function:: storytracker.open_archive_directory(path)

    :param str path: The path to directory containing archived files.
    :return: An  :py:class:`ArchivedURLSet` list
    :rtype:  :py:class:`ArchivedURLSet`

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> obj_list = storytracker.open_archive_directory('/home/ben/archive/')


open_archive_filepath
---------------------

Accepts a file path and returns an ``ArchivedURL`` object

.. py:function:: storytracker.open_archive_filepath(path)

    :param str path: The path to the archived file. Its file name must conform to the conventions of :py:func:`storytracker.create_archive_filename`.
    :return: An :py:class:`ArchivedURL` object
    :rtype: :py:class:`ArchivedURL`
    :raises ArchiveFileNameError: If the file's name cannot not be parsed using the conventions of :py:func:`storytracker.create_archive_filename`.

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> obj = storytracker.open_archive_filepath('/home/ben/archive/http!www.latimes.com!!!!@2014-07-06T16:31:57.697250.gz')


reverse_archive_filename
------------------------

Accepts a filename created using the rules of :py:func:`storytracker.create_archive_filename`
and converts it back to Python. Returns a tuple: The URL string and a
timestamp. Do not include the file extension when providing a string.

.. py:function:: storytracker.reverse_archive_filename(filename)

    :param str filename: A filename structured using the style of the :py:func:`storytracker.create_archive_filename` function
    :return: A tuple containing the URL of the archived page as a string and a datetime object of the archive's timestamp 
    :rtype: ``tuple``

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> storytracker.reverse_archive_filename('http!www.latimes.com!!!!@2014-07-06T16:31:57.697250')
    ('http://www.latimes.com', datetime.datetime(2014, 7, 6, 16, 31, 57, 697250))
