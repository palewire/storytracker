"""
Generate example materials for the documentation in ./docs/
"""
import os
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

# URL images
obj = storytracker.archive("http://www.cnn.com/")
illo_path = obj.write_illustration_to_directory("./docs/_static/example/")
overlay_path = obj.write_overlay_to_directory("./docs/_static/example/")
os.rename(illo_path, "./docs/_static/example/illo.jpg")
os.rename(overlay_path, "./docs/_static/example/overlay.png")

# URL images
gif_path = urlset.write_href_illustration_animation_to_directory(
    "http://www.washingtonpost.com/investigations/us-intelligence-mining-data-from-nine-us-internet-companies-in-broad-secret-program/2013/06/06/3a0c0da8-cebf-11e2-8845-d970ccb04497_story.html",
    "./docs/_static/example/"
)
os.rename(gif_path, "./docs/_static/example/href.gif")

urlset[0].write_analysis_report_to_directory("./docs/_static/example/")
urlset.write_analysis_report_to_directory("./docs/_static/example/")

