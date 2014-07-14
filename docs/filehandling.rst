File handling
=============

Functions for naming, saving and retrieving archived URLs.

create_archive_filename
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

Accepts a file path and returns an ``ArchivedURL`` object

.. py:function:: storytracker.open_archive_filepath(path)

    :param str path: The path to the archived file. Its file name must conform to the conventions of :py:func:`storytracker.create_archive_filename`.
    :return: An :py:class:`ArchivedURL` object
    :rtype: :py:class:`ArchivedURL`

Example usage:

.. code-block:: python

    >>> import storytracker
    >>> obj = storytracker.open_archive_filepath('/home/ben/archive/http!www.latimes.com!!!!@2014-07-06T16:31:57.697250.gz')


reverse_archive_filename
~~~~~~~~~~~~~~~~~~~~~~~~

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
