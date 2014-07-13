import os
import sys
import six
import glob
import tempfile
import unittest
import storytracker
from datetime import datetime
from bs4 import BeautifulSoup
from storytracker.analysis import ArchivedURL, Hyperlink


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
        self.long_url = "http://www.washingtonpost.com/investigations/us-\
intelligence-mining-data-from-nine-us-internet-companies-in-broad-secret-\
program/2013/06/06/3a0c0da8-cebf-11e2-8845-d970ccb04497_story.html"
        self.img = "http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9"
        self.tmpdir = tempfile.mkdtemp()
        # Turning off stdout temporarily
        original_stdout = sys.stdout
        sys.stdout = NullDevice()


class ArchiveTest(BaseTest):

    def test_get(self):
        storytracker.get(self.url)
        with self.assertRaises(ValueError):
            storytracker.get(self.img)
        storytracker.get(self.img, verify=False)

    def test_filenaming(self):
        now = datetime.now()
        filename = storytracker.create_archive_filename(self.url, now)
        url, then = storytracker.reverse_archive_filename(filename)
        self.assertEqual(self.url, url)
        self.assertEqual(now, then)

    def test_archive(self):
        storytracker.archive(self.url)
        storytracker.archive(self.url, minify=False)
        storytracker.archive(self.url, extend_urls=False)
        storytracker.archive(self.url, compress=False)
        storytracker.archive(self.url, output_dir=self.tmpdir)
        storytracker.archive(self.url, compress=False, output_dir=self.tmpdir)
        for fn in glob.glob("./http!www.cnn.com!!!*"):
            os.remove(fn)

    def test_long_url(self):
        now = datetime.now()
        filename = storytracker.create_archive_filename(self.long_url, now)
        url, then = storytracker.reverse_archive_filename(filename)
        path = storytracker.archive(self.long_url, output_dir=self.tmpdir)
        os.remove(path)


class AnalysisTest(BaseTest):

    def test_open_archive_gzip(self):
        path = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj = storytracker.open_archive_filepath(path)
        self.assertTrue(isinstance(obj, ArchivedURL))

    def test_open_archive_html(self):
        path = storytracker.archive(
            self.url,
            output_dir=self.tmpdir,
            compress=False
        )
        obj = storytracker.open_archive_filepath(path)
        self.assertTrue(isinstance(obj, ArchivedURL))

    def test_url_creation(self):
        html = storytracker.archive(self.url, compress=False)
        timestamp = datetime.now()
        obj = ArchivedURL(self.url, timestamp, html)
        self.assertEqual(self.url, obj.url)
        self.assertEqual(timestamp, obj.timestamp)
        self.assertEqual(html, obj.html)
        self.assertEqual(BeautifulSoup(html), obj.soup)

    def test_url_hyperlinks(self):
        path = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj = storytracker.open_archive_filepath(path)
        self.assertTrue(isinstance(obj.hyperlinks, list))
        [self.assertTrue(isinstance(a, Hyperlink)) for a in obj.hyperlinks]


if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
