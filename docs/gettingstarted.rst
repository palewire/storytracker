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
