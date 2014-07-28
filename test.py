import os
import sys
import six
import site
import glob
import tempfile
import unittest
import subprocess
import storytracker
from command import Command
from datetime import datetime
from bs4 import BeautifulSoup
from storytracker.analysis import ArchivedURL
from storytracker.analysis import ArchivedURLSet
from storytracker.analysis import Hyperlink, Image

#
# Base tests
#

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
        # An simple archive we can reuse to prevent having to rerequest it
        self.archive = storytracker.archive(self.url)


class MutedTest(BaseTest):

    def setUp(self):
        super(MutedTest, self).setUp()
        # Turning off stdout temporarily
        original_stdout = sys.stdout
        sys.stdout = NullDevice()

#
# Python tests
#

class ArchiveTest(MutedTest):

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
        obj1 = self.archive
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


class AnalysisTest(MutedTest):

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
        obj = self.archive
        self.assertEqual(self.url, obj.url)
        obj.timestamp
        obj.html
        obj.soup
        obj.gzip
        obj.__unicode__()
        obj.__str__()
        obj.__repr__()
        self.assertEqual(obj.archive_path, None)
        obj.write_gzip_to_directory(self.tmpdir)

    def test_url_hyperlinks(self):
        obj = self.archive
        self.assertEqual(obj._hyperlinks, [])
        self.assertTrue(isinstance(obj.hyperlinks, list))
        self.assertEqual(obj._hyperlinks, obj.hyperlinks)
        [self.assertTrue(isinstance(a, Hyperlink)) for a in obj.hyperlinks]
        a = obj.hyperlinks[0]
        a.href
        a.string
        a.domain
        a.index
        if a.images:
            for i in a.images:
                self.assertTrue(isinstance(i, Image))
                i.src
                i.__unicode__()
        a.__unicode__()
        a.__str__()
        a.__repr__()
        a.__csv__()

    def test_url_images(self):
        obj = self.archive
        self.assertEqual(obj._images, [])
        self.assertTrue(len(obj.images) > 0)
        self.assertTrue(isinstance(obj.images, list))
        self.assertEqual(obj._images, obj.images)
        [self.assertTrue(isinstance(i, Image)) for i in obj.images]
        img = obj.images[0]
        img.src
        img.__unicode__()
        img.__str__()
        img.__repr__()

    def test_urlset_creation(self):
        obj = ArchivedURL(self.url, datetime.now(), "foobar")
        obj2 = ArchivedURL(self.url, datetime.now(), "foobar")
        obj3 = ArchivedURL(self.url, datetime.now(), "foobar")
        urlset = ArchivedURLSet([obj, obj2])
        self.assertEqual(len(urlset), 2)
        with self.assertRaises(TypeError):
            urlset.append(1)
            urlset.append([1, 2, 3])
        with self.assertRaises(ValueError):
            urlset.append(obj)
        urlset.append(obj3)
        self.assertEqual(len(urlset), 3)
        with self.assertRaises(TypeError):
            ArchivedURLSet([1, 2, obj])
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

    def test_write_hyperlinks_csv_to_file(self):
        o = self.archive
        f = six.StringIO()
        f = o.write_hyperlinks_csv_to_file(f)
        p = os.path.join(self.tmpdir, 'links.csv')
        f2 = open(p, 'w+')
        f2 = o.write_hyperlinks_csv_to_file(f2)
        self.assertTrue(os.path.exists(p))
        os.remove(p)

#
# CLI tests
#

if six.PY2:
    class CLITest(BaseTest):

        def setUp(self):
            super(CLITest, self).setUp()
            self.this_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(self.this_dir)
            self.simple_url = "http://www.example.com"

        def test_get(self):
            path = os.path.join(self.this_dir, "bin/storytracker-get")
            cmd = '%s %s' % (path, self.simple_url)
            process = Command(cmd)
            code, out, err = process.run(timeout=3)
            python = storytracker.get(self.simple_url).encode("utf-8")
            self.assertEqual(type(out), type(python))
            self.assertEqual(out, python)

        def test_get_no_verify(self):
            path = os.path.join(self.this_dir, "bin/storytracker-get")
            cmd = '%s %s --do-not-verify' % (path, self.simple_url)
            process = Command(cmd)
            code, out, err = process.run(timeout=3)
            python = storytracker.get(self.simple_url).encode("utf-8")
            self.assertEqual(type(out), type(python))
            self.assertEqual(out, python)

        def test_archive(self):
            path = os.path.join(self.this_dir, "bin/storytracker-archive")
            cmd = '%s %s --do-not-compress' % (path, self.simple_url)
            process = Command(cmd)
            code, out, err = process.run(timeout=3)
            python = storytracker.archive(self.simple_url).html.encode("utf-8")
            self.assertEqual(type(out), type(python))
            self.assertEqual(out, python)

        def test_archive_gzipped(self):
            path = os.path.join(self.this_dir, "bin/storytracker-archive")
            cmd = '%s %s' % (path, self.simple_url)
            process = Command(cmd)
            code, out, err = process.run(timeout=3)
            python = storytracker.archive(self.simple_url).gzip
            self.assertEqual(type(out), type(python))
            self.assertEqual(out, python)

        def test_archive_output_dir(self):
            path = os.path.join(self.this_dir, "bin/storytracker-archive")
            cmd1 = "%s %s --output-dir=%s" % (
                path, self.simple_url, self.tmpdir
            )
            code1, path1, err1 = Command(cmd1).run(timeout=3)
            obj1 = storytracker.open_archive_filepath(path1)
            self.assertTrue(isinstance(obj1, storytracker.ArchivedURL))
            self.assertTrue(os.path.exists(path1))
            os.remove(path1)

        def test_archive_output_dir_html(self):
            path = os.path.join(self.this_dir, "bin/storytracker-archive")
            cmd2 = "%s %s --do-not-compress --output-dir=%s" % (
                path, self.simple_url, self.tmpdir
            )
            code2, path2, err2 = Command(cmd2).run(timeout=3)
            obj2 = storytracker.open_archive_filepath(path2)
            self.assertTrue(os.path.exists(path2))
            os.remove(path2)

        def test_links2csv_filepath(self):
            path = os.path.join(self.this_dir, "bin/storytracker-links2csv")
            obj = storytracker.archive(self.url, output_dir=self.tmpdir)
            cmd = "%s %s" % (path, obj.archive_path)
            code, out, err = Command(cmd).run(timeout=3)

        def test_links2csv_filedirectory(self):
            path = os.path.join(self.this_dir, "bin/storytracker-links2csv")
            obj = storytracker.archive(self.url, output_dir=self.tmpdir)
            obj2 = storytracker.archive(self.long_url, output_dir=self.tmpdir)
            cmd = "%s %s" % (path, self.tmpdir)
            code, out, err = Command(cmd).run(timeout=3)


if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
