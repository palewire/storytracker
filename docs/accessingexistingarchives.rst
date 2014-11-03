Accessing existing archives
===========================


The Internet Archive's The Wayback Machine
------------------------------------------

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


PastPages.org
-------------

A screenshot with corresponding HTML archived by `pastpages.org <http://www.pastpages.org>`_ can
be pulled in by passing the URL from its screenshot detail page to :py:func:`storytracker.open_pastpages_url`.

.. code-block:: python

    >>> storytracker.open_pastpages_url("http://www.pastpages.org/screenshot/1879727/")
    <ArchivedURL: http://www.foxnews.com/@2014-10-29 05:05:50.761287>

