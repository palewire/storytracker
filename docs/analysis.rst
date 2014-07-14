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

    .. py:attribute:: soup

        The archived HTML passed into a `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/bs4/doc/#>`_ parser

    .. py:attribute:: hyperlinks

        A list of all the hyperlinks extracted from the HTML

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
