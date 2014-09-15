import os
import sys
import logging
sys.path.append('/home/ben/Code/palewire/storytracker/repo/')
import storytracker
from pprint import pprint
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

archive_dir = "/home/ben/Dropbox/Work outside work/PastPages/storytracker/archive-test/"

path_list = [
    os.path.join(
        archive_dir,
        "http!www.nytimes.com!!!!@2014-08-25T01:15:02.464296+00:00.html"
    ),
#   os.path.join(
#        archive_dir,
#        "http!www.nytimes.com!!!!@2014-08-25T01:00:02.455702+00:00.html"
#    ),
]

urlset = storytracker.ArchivedURLSet([])

for path in path_list:
    obj = storytracker.open_archive_filepath(path)
    urlset.append(obj)

urlset.sort()
for url in urlset:
    url.analyze()
#urlset.write_href_gif_to_directory(
#    "http://www.nytimes.com/2014/08/24/world/europe/russian-convoy-ukraine.html",
#    '/home/ben/Desktop'
#)
