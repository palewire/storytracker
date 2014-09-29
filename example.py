"""
Generate example materials for the documentation in ./docs/
"""
import storytracker
from pprint import pprint
from datetime import datetime


urlset = storytracker.ArchivedURLSet([
    storytracker.ArchivedURL(
        'http://example.com',
        datetime(2014, 1, 1, 0, 0, 0),
        open("./example/a.html", "rb").read()
    ),
    storytracker.ArchivedURL(
        'http://example.com',
        datetime(2014, 1, 1, 1, 0, 0),
        open("./example/b.html", "rb").read()
    ),
    storytracker.ArchivedURL(
        'http://example.com',
        datetime(2014, 1, 1, 2, 0, 0),
        open("./example/c.html", "rb").read()
    ),
    storytracker.ArchivedURL(
        'http://example.com',
        datetime(2014, 1, 1, 3, 0, 0),
        open("./example/d.html", "rb").read()
    ),
])

urlset[0].write_analysis_report_to_directory("./docs/_static/example/")
