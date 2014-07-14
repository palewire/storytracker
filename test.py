import os
import sys
import six
import glob
import tempfile
import unittest
import storytracker
from datetime import datetime
from bs4 import BeautifulSoup
from storytracker.analysis import ArchivedURL
from storytracker.analysis import ArchivedURLSet
from storytracker.analysis import Hyperlink


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
        with self.assertRaises(storytracker.ArchiveFileNameError):
            storytracker.reverse_archive_filename("foo.bar")

    def test_archive(self):
        obj1 = storytracker.archive(self.url)
        obj2 = storytracker.archive(self.url, minify=False)
        obj3 = storytracker.archive(self.url, extend_urls=False)
        obj4 = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj5 = storytracker.archive(
            self.url,
            compress=False,
            output_dir=self.tmpdir
        )
        for obj in [obj1, obj2, obj3, obj4, obj5]:
            self.assertTrue(isinstance(obj, storytracker.ArchivedURL))
        self.assertTrue(os.path.exists(obj4.archive_path))
        self.assertTrue(os.path.exists(obj5.archive_path))
        os.remove(obj4.archive_path)
        os.remove(obj5.archive_path)

    def test_long_url(self):
        now = datetime.now()
        filename = storytracker.create_archive_filename(self.long_url, now)
        url, then = storytracker.reverse_archive_filename(filename)
        obj = storytracker.archive(self.long_url, output_dir=self.tmpdir)
        self.assertTrue(os.path.exists(obj.archive_path))
        os.remove(obj.archive_path)


class AnalysisTest(BaseTest):

    def test_open_archive_gzip(self):
        obj1 = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj2 = storytracker.open_archive_filepath(obj1.archive_path)
        self.assertEqual(obj1, obj2)

    def test_open_archive_html(self):
        obj1 = storytracker.archive(
            self.url,
            output_dir=self.tmpdir,
            compress=False
        )
        obj2 = storytracker.open_archive_filepath(obj1.archive_path)
        self.assertEqual(obj1, obj2)

    def test_url_creation(self):
        obj = storytracker.archive(self.url)
        self.assertEqual(self.url, obj.url)
        obj.timestamp
        obj.html
        obj.soup
        obj.gzip
        self.assertEqual(obj.archive_path, None)
        obj.write_gzip_to_directory(self.tmpdir)

    def test_url_hyperlinks(self):
        obj1 = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj2 = storytracker.open_archive_filepath(obj1.archive_path)
        self.assertTrue(isinstance(obj2.hyperlinks, list))
        [self.assertTrue(isinstance(a, Hyperlink)) for a in obj2.hyperlinks]

    def test_urlset_creation(self):
        obj = ArchivedURL(self.url, datetime.now(), "foobar")
        obj2 = ArchivedURL(self.url, datetime.now(), "foobar")
        obj3 = ArchivedURL(self.url, datetime.now(), "foobar")
        urlset = ArchivedURLSet([obj, obj2])
        self.assertEqual(len(urlset), 2)
        with self.assertRaises(TypeError):
            urlset.append(1)
            urlset.append([1,2,3])
        with self.assertRaises(ValueError):
            urlset.append(obj)
        urlset.append(obj3)
        self.assertEqual(len(urlset), 3)
        with self.assertRaises(TypeError):
            ArchivedURLSet([1,2, obj])
        with self.assertRaises(ValueError):
            ArchivedURLSet([obj, obj])

    def test_open_archive_directory(self):
        with self.assertRaises(ValueError):
            storytracker.open_archive_directory("./foo.bar")
        storytracker.archive(
            self.url,
            compress=False,
            output_dir=self.tmpdir
        )
        storytracker.archive(
            self.url,
            compress=False,
            output_dir=self.tmpdir
        )
        urlset = storytracker.open_archive_directory(self.tmpdir)
        self.assertTrue(len(urlset), 2)
        [self.assertTrue(isinstance(o, ArchivedURL)) for o in urlset]


if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
