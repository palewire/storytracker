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

## URL images
obj = storytracker.archive("http://www.cnn.com/")
illo_path = obj.write_illustration_to_directory("./docs/_static/example/")
overlay_path = obj.write_overlay_to_directory("./docs/_static/example/")
os.rename(illo_path, "./docs/_static/example/illo.jpg")
os.rename(overlay_path, "./docs/_static/example/overlay.png")

# URL images
urlset2 = storytracker.ArchivedURLSet([
    storytracker.open_wayback_machine_url("https://web.archive.org/web/20140101005148/http://www.bbc.co.uk/news/"),
    storytracker.open_wayback_machine_url("https://web.archive.org/web/20140101080323/http://www.bbc.co.uk/news/"),
    storytracker.open_wayback_machine_url("https://web.archive.org/web/20140101094432/http://www.bbc.co.uk/news/"),
])
urlset2[0].write_overlay_to_directory("./")
gif_path = urlset2.write_href_overlay_animation_to_directory(
    "https://web.archive.org/news/world-africa-25561753",
    "./docs/_static/example/"
)
os.rename(gif_path, "./docs/_static/example/href.gif")

urlset[0].write_analysis_report_to_directory("./docs/_static/example/")
urlset.write_analysis_report_to_directory("./docs/_static/example/")
