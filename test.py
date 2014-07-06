import os
import sys
import six
import glob
import unittest
import storytracker
from datetime import datetime


class NullDevice():
    """
    A nothingburger to replace stdout with while running tests.
    """
    def write(self, s):
        pass

    def flush(self, *args, **kwargs):
        pass


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://www.cnn.com"
        self.long_url = "http://www.washingtonpost.com/investigations/us-intelligence-mining-data-from-nine-us-internet-companies-in-broad-secret-program/2013/06/06/3a0c0da8-cebf-11e2-8845-d970ccb04497_story.html"
        self.img = "http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9"
        # Turning off stdout temporarily
        original_stdout = sys.stdout
        sys.stdout = NullDevice()


class ArchiveTest(BaseTest):

    def test_get(self):
        storytracker.get(self.url)
        try:
            storytracker.get(self.img)
        except ValueError:
            pass
        storytracker.get(self.img, verify=False)

    def test_archive(self):
        now = datetime.now()
        filename = storytracker.create_archive_filename(self.url, now)
        url, then = storytracker.reverse_archive_filename(filename)
        self.assertEqual(self.url, url)
        self.assertEqual(now, then)
        for f in [storytracker.archive,]:
            f(self.url)
            f(self.url, minify=False)
            f(self.url, extend_urls=False)
            f(self.url, compress=False)
            f(self.url, output_dir="./")
            f(self.url, compress=False, output_dir="./")
            for fn in glob.glob("./http!www.cnn.com!!!*"):
                os.remove(fn)

    def test_long_url(self):
        now = datetime.now()
        filename = storytracker.create_archive_filename(self.long_url, now)
        url, then = storytracker.reverse_archive_filename(filename)
        storytracker.archive(self.long_url, output_dir="./")
        for fn in glob.glob("./http!www.washingtonpost.com*"):
            os.remove(fn)

if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
