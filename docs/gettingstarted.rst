Getting started
===============

You can install storytracker from the `Python Package Index <https://github.com/pastpages/storytracker>`_ using the command-line tool pip. If you don't have
pip installed follow `these instructions <https://pip.pypa.io/en/latest/installing.html>`_. Here is all it takes.

.. code-block:: bash

    $ pip install storytracker

Once installed, you can start using storytracker's command-line tools immediately, like :py:func:`storytracker.archive`.

.. code-block:: bash

    $ storytracker-archive http://www.latimes.com

That should pour out a scary looking stream of data to your console. That is the content of the page you requested compressed using `gzip <http://en.wikipedia.org/wiki/Gzip>`_.
If you'd prefer to see the raw HTML, add the ``--do-not-compress`` option.

.. code-block:: bash

    $ storytracker-archive http://www.latimes.com --do-not-compress

You could save that yourself using `a standard UNIX pipeline <http://en.wikipedia.org/wiki/Pipeline_%28Unix%29>`_.

.. code-block:: bash

    $ storytracker-archive http://www.latimes.com --do-not-compress > archive.html

But why do that when :py:func:`storytracker.create_archive_filename` will work behind the scenes to automatically come
up with a tidy name that includes both the URL and a timestamp?

.. code-block:: bash

    $ storytracker-archive http://www.latimes.com --do-not-compress --output-dir="./"

Run that and you'll see the file right away in your current directory.

.. code-block:: bash

    # Try opening the file you spot here with your browser
    $ ls | grep .html


Scheduling archives with Python and cron
----------------------------------------

UNIX-like systems typically come equipped with a built in method for scheduling tasks known as `cron <http://en.wikipedia.org/wiki/Cron>`_.
To utilize it with storytracker, one approach is to write a Python script that retrieves a series of sites each time it is run.

.. code-block:: python

    import storytracker

    SITE_LIST = [
        # A list of the sites to archive
        'http://www.latimes.com',
        'http://www.nytimes.com',
        'http://www.kansascity.com',
        'http://www.knoxnews.com',
        'http://www.indiatimes.com',
    ]
    # The place on the filesystem where you want to save the files
    OUTPUT_DIR = "/path/to/my/directory/"

    # Runs when the script is called with the python interpreter
    # ala "$ python cron.py"
    if __name__ == "__main__":
        # Loop through the site list
        for s in SITE_LIST:
            # Spit out what you're doing
            print "Archiving %s" % s
            try:
                # Attempt to archive each site at the output directory
                # defined above
                storytracker.archive(s, output_dir=OUTPUT_DIR)
            except Exception as e:
                # And just move along and keep rolling if it fails.
                print e

Then edit the cron file from the command line.

.. code-block:: bash

    $ crontab -e

And use `cron's custom expressions <http://en.wikipedia.org/wiki/Cron#Examples>`_ to schedule the job however you'd like.
This example would schedule the script to run a file like the one above at the top of every hour. Though it assumes
that ``storytracker`` is available to your global Python installation at ``/usr/bin/python``. If you are using a virtualenv or different Python
configuration, you should begin the line with a path leading to that particular ``python`` executable.

.. code-block:: bash

    0 * * * *  /usr/bin/python /path/to/my/script/cron.py

Extracting hyperlinks from archived files
-----------------------------------------

The cron task above is regularly saving archived files to the ``OUTPUT_DIR``. Those files
can be accessed for analysis using tools like :py:func:`storytracker.open_archive_filepath` and
:py:func:`storytracker.open_archive_directory`.

.. code-block:: python

    >>> import storytracker

    >>> # This would import a single file and return a object we can play with
    >>> url = storytracker.open_archive_filepath("/path/to/my/directory/http!www.cnn.com!!!!@2014-07-22T04:18:21.751802+00:00.html")

    >>> # This returns a list of all the objects found in the directory
    >>> url_list = storytracker.open_archive_directory("/path/to/my/directory/")

Once you have an url archive imported you can loop through all the hyperlinks found in its ``body`` tag which are returned as :py:class:`ArchivedURL`
objects.

.. code-block:: python

    >>> url.hyperlinks
    [<Hyperlink: http://www.cnn.com/>, <Hyperlink: http://edition.cnn.com/?hpt=ed_Intl>, <Hyperlink: http://mexico.cnn.com/?hpt=ed_Mexico>, <Hyperlink: http://arabic.cnn.com/?hpt=ed_Arabic>, <Hyperlink: http://www.cnn.com/CNN/Programs>, <Hyperlink: http://www.cnn.com/cnn/programs/>, <Hyperlink: http://www.cnn.com/cnni/>, <Hyperlink: http://cnnespanol.cnn.com/>, <Hyperlink: http://www.hlntv.com>, <Hyperlink: javascript:void(0);>, <Hyperlink: javascript:void(0);>, <Hyperlink: http://www.cnn.com/>, <Hyperlink: http://www.cnn.com/video/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/US/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/WORLD/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/POLITICS/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/JUSTICE/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/SHOWBIZ/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/TECH/?hpt=sitenav>, <Hyperlink: http://www.cnn.com/HEALTH/?hpt=sitenav> ... ]

Those hyperlinks and all their attributes can be quickly printed out in comma-delimited format.

.. code-block:: python

    >>> f = open("./hyperlinks.csv", "wb")
    >>> f = url.write_hyperlinks_csv_to_file(f)

The same thing can be done with our command line tool ``storytracker-links2csv``.

.. code-block:: bash

    $ storytracker-links2csv /path/to/my/directory/http!www.cnn.com!!!!@2014-07-22T04:18:21.751802+00:00.html

Which also accepts a directory.

.. code-block:: bash

    $ storytracker-links2csv /path/to/my/directory/
