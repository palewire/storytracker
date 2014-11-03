Analyzing archived URLs
=======================

Extracting hyperlinks
---------------------

The cron task above is regularly saving archived files to the ``OUTPUT_DIR``. Those files
can be accessed for analysis using tools like :py:func:`storytracker.open_archive_filepath` and
:py:func:`storytracker.open_archive_directory`.

.. code-block:: python

    >>> import storytracker

    >>> # This would import a single file and return a object we can play with
    >>> url = storytracker.open_archive_filepath("/path/to/my/directory/http!www.cnn.com!!!!@2014-07-22T04:18:21.751802+00:00.html")

    >>> # This returns a list of all the objects found in the directory
    >>> url_list = storytracker.open_archive_directory("/path/to/my/directory/")

    >>> # And remember you can still always do it on the fly
    >>> url = storytracker.archive("http://www.cnn.com")

Once you have an url archive imported you can loop through all the hyperlinks found in its ``body`` tag which are returned as :py:class:`ArchivedURL`
objects.

.. code-block:: python

    >>> url.hyperlinks
    [<Hyperlink: http://www.cnn.com/>, <Hyperlink: http://edition.cnn.com/?hpt=ed_Intl>, <Hyperlink: http://mexico.cnn.com/?hpt=ed_Mexico>, <Hyperlink: http://arabic.cnn.com/?hpt=ed_Arabic>, <Hyperlink: http://www.cnn.com/CNN/Programs>, <Hyperlink: http://www.cnn.com/cnn/programs/>, <Hyperlink: http://www.cnn.com/cnni/>, <Hyperlink: http://cnnespanol.cnn.com/>, <Hyperlink: http://www.hlntv.com>, <Hyperlink: javascript:void(0);>, <Hyperlink: javascript:void(0);>, <Hyperlink: http://www.cnn.com/>, <Hyperlink: http://www.cnn.com/video/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/US/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/WORLD/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/POLITICS/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/JUSTICE/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/SHOWBIZ/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/TECH/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/HEALTH/?hpt=sitenav> ... ]

You could filter that list to just those estimated to be news stories like so.

.. code-block:: python

    >>> [h for h in url.hyperlinks if h.is_story]
    [<Hyperlink: http://politicalticker.blogs.cnn.com/201...>, <Hyperlink: http://www.cnn.com/interactive/2014/06/u...>, <Hyperlink: http://www.cnn.com/interactive/2014/07/l...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/2014/07/27/us/florida...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, <Hyperlink: http://www.cnn.com/video/data/2.0/video/...>, ...]

A complete list of hyperlinks and all their attributes can be quickly printed out in comma-delimited format.

.. code-block:: python

    >>> f = open("./hyperlinks.csv", "wb")
    >>> f = url.write_hyperlinks_csv_to_file(f)

The same thing can be done with our command line tool ``storytracker-links2csv``.

.. code-block:: bash

    $ storytracker-links2csv /path/to/my/directory/http!www.cnn.com!!!!@2014-07-22T04:18:21.751802+00:00.html

Which also accepts a directory.

.. code-block:: bash

    $ storytracker-links2csv /path/to/my/directory/


Tracking hyperlinks across a set of URLs
----------------------------------------

You can analyze how a particular hyperlink moved across a set of archived URLs
like so:

.. code-block:: python

    >>> urlset = storytracker.ArchivedURLSet([
    >>>     "http!www.nytimes.com!!!!@2014-08-25T01:15:02.464296+00:00.html"
    >>>     "http!www.nytimes.com!!!!@2014-08-25T01:00:02.455702+00:00.html"
    >>> ])
    >>> urlset.sort()
    >>> urlset.print_href_analysis("http://www.nytimes.com/2014/08/24/world/europe/russian-convoy-ukraine.html")
    http://www.nytimes.com/2014/08/24/world/europe/russian-convoy-ukraine.html

    | Statistic            | Value                            |
    -----------------------------------------------------------
    | Archived URL total   | 2                                |
    | Observations of href | 2                                |
    | First timestamp      | 2014-08-25 01:00:02.455702+00:00 |
    | Last timestamp       | 2014-08-25 01:15:02.464296+00:00 |
    | Timedelta            | 0:15:00.008594                   |
    | Maximum y position   | 2568                             |
    | Minimum y position   | 2546                             |
    | Range of y positions | 22.0                             |
    | Average y position   | 2557.0                           |
    | Median y position    | 2557.0                           |

    | Headline                                                           |
    ----------------------------------------------------------------------
    | Germany Pledges Aid for Ukraine as Russia Hails a Returning Convoy |
