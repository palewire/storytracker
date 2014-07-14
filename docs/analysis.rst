Analysis
========


ArchivedURL
-----------

An URL's archived HTML with tools for analysis.

.. py:class:: ArchivedURL(url, timestamp, html)

    .. py:attribute:: url

        The url archived

    .. py:attribute:: timestamp

        The date and time when the url was archived

    .. py:attribute:: html

        The HTML archived

    .. py:attribute:: gzip

        Returns the archived HTML as a stream of gzipped data

    .. py:attribute:: archive_filename

        Returns a file name for this archive using the conventions of :py:func:`storytracker.create_archive_filename`.

    .. py:attribute:: soup

        The archived HTML passed into a `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/bs4/doc/#>`_ parser

    .. py:attribute:: hyperlinks

        A list of all the hyperlinks extracted from the HTML

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

.. py:class:: Hyperlink

    .. py:attribute:: href

        The URL the hyperlink references
