Getting started
===============

You can install storytracker from the `Python Package Index <https://github.com/pastpages/storytracker>`_ using the command-line tool pip. If you don't have pip installed follow `these instructions <https://pip.pypa.io/en/latest/installing.html>`_. Here is all it takes.

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
