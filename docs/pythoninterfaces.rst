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

.. py:class:: ArchivedURL(url, timestamp, html, browser_width=1024, browser_height=768)

    **Initialization arguments**

    .. py:attribute:: url

        The url archived

    .. py:attribute:: timestamp

        The date and time when the url was archived

    .. py:attribute:: html

        The HTML archived

    **Optional initialization options**

    .. py:attribute:: browser_width

        The width of the browser that will be opened to inspect the URL's HTML

    .. py:attribute:: browser_height

        The height of the browser that will be opened to inspect the URL's HTML

    **Other attributes**

    .. py:attribute:: height

        The height of the page in pixels after the URL is opened in a web browser

    .. py:attribute:: width

        The width of the page in pixels after the URL is opened in a web browser

    .. py:attribute:: gzip

        Returns the archived HTML as a stream of gzipped data

    .. py:attribute:: archive_filename

        Returns a file name for this archive using the conventions of :py:func:`storytracker.create_archive_filename`.

    .. py:attribute:: hyperlinks

        A list of all the hyperlinks extracted from the HTML

    .. py:attribute:: images

        A list of all the images extracts from the HTML

    .. py:attribute:: largest_image

        The largest image extracted from the HTML

    **Analysis methods**

    .. py:attribute:: analyze()

        Opens the URL's HTML in a web browser and runs all of the analysis
        methods that use it.

    .. py:attribute:: get_cell(x, y, cell_size=256)

        Returns the grid cell where the provided x and y coordinates
        appear on the page. Cells are sized as squares, with 256 pixels as
        the default.

        The value is returned in the style of `algebraic notation
        used in a game of chess <http://en.wikipedia.org/wiki/Algebraic_notation_%28chess%29>`_.

        .. code-block:: python

            >>> obj.get_cell(1, 1)
            'a1'
            >>> obj.get_cell(257, 1)
            'b1'
            >>> obj.get_cell(1, 513)
            'a3'

    .. py:attribute:: open_browser()

        Opens the URL's HTML in an web browser so it can be analyzed.

    .. py:attribute:: close_browser()

        Closes the web browser opened to analyze the URL's HTML

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

.. py:class:: Hyperlink(href, string, index, images=[], x=None, y=None, width=None, height=None, cell=None, font_size=None)

    **Initialization arguments**

    .. py:attribute:: href

        The URL the hyperlink references

    .. py:attribute:: string

        The strings contents of the anchor tag

    .. py:attribute:: index

        The index value of the links order within its source HTML. Starts counting at zero.

    .. py:attribute:: images

        A list of the :py:class:`Image` objects extracted from the HTML.

    .. py:attribute:: x

        The x coordinate of the object's location on the page.

    .. py:attribute:: y

        The y coordinate of the object's location on the page.

    .. py:attribute:: width

        The width of the object's size on the page.

    .. py:attribute:: height

        The height of the object's size on the page.

    .. py:attribute:: cell

        The grid cell where the provided x and y coordinates
        appear on the page. Cells are sized as squares, with 256 pixels as
        the default.

        The value is returned in the style of `algebraic notation
        used in a game of chess <http://en.wikipedia.org/wiki/Algebraic_notation_%28chess%29>`_.

    .. py:attribute:: font_size

        The size of the font of the text inside the hyperlink.

    **Other attributes**

    .. py:attribute:: __csv__

        Returns a list of values ready to be written to a CSV file object

    .. py:attribute:: domain

        The domain of the href

    .. py:attribute:: is_story

        Returns a boolean estimate of whether the object's ``href`` attribute links to a
        news story. Guess provided by `storysniffer <https://github.com/pastpages/storysniffer>`_,
        a library developed as a companion to this project.

Image
-----

.. py:class:: Image(src)

    An image extracted from an archived URL.

    **Initialization arguments**

    .. py:attribute:: src

        The ``src`` attribute of the image tag

    .. py:attribute:: x

        The x coordinate of the object's location on the page.

    .. py:attribute:: y

        The y coordinate of the object's location on the page.

    .. py:attribute:: width

        The width of the object's size on the page.

    .. py:attribute:: height

        The height of the object's size on the page.

    .. py:attribute:: cell

        The grid cell where the provided x and y coordinates
        appear on the page. Cells are sized as squares, with 256 pixels as
        the default.

        The value is returned in the style of `algebraic notation
        used in a game of chess <http://en.wikipedia.org/wiki/Algebraic_notation_%28chess%29>`_.

    **Analysis methods**

    .. py:attribute:: area

        Returns the square area of the image

    .. py:attribute:: orientation

        Returns a string describing the shape of the image.

        'square' means the width and height are equal

        'landscape' is a horizontal image with width greater than height

        'portrait' is a vertical image with height greater than width
        None means there are no size attributes to test


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
    :raises ArchiveFileNameError: If the file's name cannot be parsed using the conventions of :py:func:`storytracker.create_archive_filename`.

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> obj = storytracker.open_archive_filepath('/home/ben/archive/http!www.latimes.com!!!!@2014-07-06T16:31:57.697250.gz')


open_wayback_machine_url
------------------------

Accepts a URL from the `Internet Archive's Wayback Machine <http://www.archive.org>`_ and returns an ``ArchivedURL`` object

.. py:function:: storytracker.open_wayback_machine_url(url)

    :param str url: A URL from the Wayback Machine that links directly to an archive. An example is `https://web.archive.org/web/20010911213814/http://www.cnn.com/ <https://web.archive.org/web/20010911213814/http://www.cnn.com/>`_.
    :return: An :py:class:`ArchivedURL` object
    :rtype: :py:class:`ArchivedURL`
    :raises ArchiveFileNameError: If the file's name cannot be parsed.

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> obj = storytracker.open_wayback_machine_url('https://web.archive.org/web/20010911213814/http://www.cnn.com/') 


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

reverse_wayback_machine_url
---------------------------

Accepts an url from the Internet Archive's Wayback Machine and returns a tuple  with the archived URL string and a
timestamp.

.. py:function:: storytracker.reverse_wayback_machine_url(url)

    :param str url: A URL from the Wayback Machine that links directly to an archive. An example is `https://web.archive.org/web/20010911213814/http://www.cnn.com/ <https://web.archive.org/web/20010911213814/http://www.cnn.com/>`_.
    :return: A tuple containing the URL of the archived page as a string and a datetime object of the archive's timestamp 
    :rtype: ``tuple``

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> storytracker.reverse_wayback_machine_url('https://web.archive.org/web/20010911213814/http://www.cnn.com/')
    ('http://www.cnn.com/', datetime.datetime(2001, 9, 11, 21, 38, 14))
