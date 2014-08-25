Changelog
=========

0.0.9
-----

* Created a new method to write out an visualization of the page as an image file.

0.0.8
-----

* Refactored analysis tools to use Selenium and PhantomJS rather than BeautifulSoup, which allowed for a whole of size and location attributes to be parsed from the fully rendered HTML document.

0.0.7
-----

* Added ``open_wayback_machine_url`` and ``reverse_wayback_machine_url`` functions
to introduce support for files saved by the Internet Archive's Wayback Machine.

0.0.6
-----

* ``is_story`` estimate added to each ``Hyperlink`` object as an attribute

0.0.5
-----

* ``Hyperlink`` and ``Image`` classes
* ``hyperlink`` and ``images`` methods that extract them from ``ArchivedURL``
* ``write_hyperlinks_csv_to_file`` method on ``ArchivedURL for outputs
* ``storytracker-links2csv`` command-line interface

0.0.4
-----

* Timestamping of ``archive`` method now includes timezone, set to UTC by default

0.0.3
-----

* More forgiving ``urlparse`` imports that work in both Python 2 and Python 3

0.0.2
-----

* Changed automatic file naming process to work better with long file names
* Added basic logging to the archival functions

0.0.1
-----

* Python functions for retrieving and saving URLs
* Command line tools for interactive with those function
