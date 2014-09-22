How to use it
=============

Getting started
---------------

You can install storytracker from the `Python Package Index <https://github.com/pastpages/storytracker>`_ using the command-line tool pip. If you don't have
pip installed follow `these instructions <https://pip.pypa.io/en/latest/installing.html>`_. Here is all it takes.

.. code-block:: bash

    $ pip install storytracker

You won't need it for archival, but the analytical tools explained later one require that you
have a supported web browser installed. Firefox will work, but it's recommended that you `install
PhantomJS <http://phantomjs.org/>`_, a "headless" browser that runs behind the scenes. 

On Ubuntu Linux that's as easy as:

.. code-block:: bash

    $ sudo apt-get install phantomjs

In Apple's OSX you can use Homebrew to install it like so:

.. code-block:: bash

    $ brew update && brew install phantomjs

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

Analyzing data from the Wayback Machine
---------------------------------------

A page saved by the Internet Archive's excellent Wayback Machine can be integrated
by passing its URL to :py:func:`storytracker.open_wayback_machine_url`.

This pulls down the CNN homepage captured on Sept. 11, 2001.

.. code-block:: python

    >>> import storytracker
    >>> obj = storytracker.open_wayback_machine_url('https://web.archive.org/web/20010911213814/http://www.cnn.com/')

Now you have an :py:class:`ArchivedURL` object like any other in the storytracker system.

.. code-block:: python

    >>> obj
    <ArchivedURL: http://www.cnn.com/@2001-09-11 21:38:14>

So, if for instance you wanted to see all the images on the page you could do this.

.. code-block:: python

    >>> for i in obj.images:
    >>>     print i.src
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    https://web.archive.org/web/20010911213814id_/http://www.cnn.com/images/newmain/top.main.special.report.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    https://web.archive.org/web/20010911213814id_/http://www.cnn.com/images/newmain/header.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/0109/top.exclusive.jpg
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com//images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif
    http://a388.g.akamai.net/f/388/21/1d/www.cnn.com/images/hub2000/1.gif


Creating an illustration that visualizes stories on the page
------------------------------------------------------------

You can output a static image visualizing where headlines, stories and images are on
the page using the ``ArchivedURL.write_illustration_to_directory`` method available on
all :py:func:`ArchivedURL` objects. The following code will write a new image of the CNN homepage to my desktop.

.. code-block:: python

    obj = storytracker.archive("http://www.cnn.com")
    obj.write_illustration_to_directory("/home/ben/Desktop")

The resulting image is sized at the same width and height of the real page,
with images colored red. Hyperlinks are colored in too. If our system
thinks the link leads to a news story, it's filled in purple. Otherwise it's colored blue.

Here's a slimmed down version of the one I just made. Click on it to see it full sized.

.. image:: _static/http!www.cnn.com!!!!@2014-08-25T02:28:44.549851+00:00.jpg
    :width: 400px

Analyzing how a hyperlink shifted across a set of pages
-------------------------------------------------------

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


Creating an animation that tracks a hyperlink's movement across a set of pages
------------------------------------------------------------------------------

You can create an animated GIF that shows how a particular hyperlink's position
shifted across a series of pages with the following code. 

.. code-block:: python

    >>> urlset.write_href_gif_to_directory(
    >>>    # First give it your hyperlink
    >>>    "http://www.washingtonpost.com/investigations/us-intelligence-mining-data-from-nine-us-internet-companies-in-broad-secret-program/2013/06/06/3a0c0da8-cebf-11e2-8845-d970ccb04497_story.html",
    >>>    # Then give it the directory where you'd like the file to be saved
    >>>    "./"
    >>> )

.. image:: _static/href.gif
    :width: 400px
