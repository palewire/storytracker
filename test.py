#! /usr/bin/env python
import os
import sys
import six
import site
import glob
import shlex
import random
import tempfile
import unittest
import threading
import traceback
import subprocess
import storytracker
import multiprocessing
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from wsgiref.simple_server import make_server
from storytracker.analysis import ArchivedURL
from storytracker.analysis import ArchivedURLSet
from storytracker.analysis import Hyperlink, Image


class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    """
    command = None
    process = None
    status = None
    output, error = '', ''

    def __init__(self, command):
        if isinstance(command, six.string_types):
            command = shlex.split(command)
        self.command = command

    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.status = self.process.returncode
            except:
                self.error = traceback.format_exc()
                self.status = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE
        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.status, self.output, self.error

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


def hello_world_app(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    # The returned object is going to be printed
    return ["""<!DOCTYPE html>
<html>
<body>
    <a href="http://www.washingtonpost.com/investigations/us-intelligence-mining-data-from-nine-us-internet-companies-in-broad-secret-program/2013/06/06/3a0c0da8-cebf-11e2-8845-d970ccb04497_story.html">
        U.S., British intelligence mining data from nine U.S. Internet companies in broad secret program
    </a>
    <p>The National Security Agency and the FBI are tapping directly into the central servers of nine leading U.S. Internet companies, extracting audio and video chats, photographs, e-mails, documents, and connection logs that enable analysts to track foreign targets, according to a top-secret document obtained by The Washington Post.</p>
    <img src="http://www.washingtonpost.com/wp-srv/special/politics/prism-collection-documents/images/upstream-slide.jpg">
    <a href="http://www.washingtonpost.com/wp-srv/special/politics/prism-collection-documents/">
        <img src="http://www.washingtonpost.com/wp-srv/special/politics/prism-collection-documents/images/prism-slide-6.jpg">
    </a>
</body>
</html>"""]


class BaseTest(unittest.TestCase):

    def setUp(self):
        port = random.choice(range(9000, 9999))
        server = make_server('', port, hello_world_app)
        self.server_process = multiprocessing.Process(
            target=server.serve_forever
        )
        self.server_process.start()
        self.url = "http://localhost:%s/" % port
        self.img = "http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9"
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)


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
        self.archive = storytracker.archive(self.url)
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
        self.assertTrue(os.path.exists(obj4.gzip_archive_path))
        self.assertTrue(os.path.exists(obj5.html_archive_path))
        os.remove(obj4.gzip_archive_path)
        os.remove(obj5.html_archive_path)


class AnalysisTest(MutedTest):

    def test_open_archive_gzip(self):
        obj1 = storytracker.archive(self.url, output_dir=self.tmpdir)
        obj2 = storytracker.open_archive_filepath(obj1.gzip_archive_path)
        self.assertEqual(obj1, obj2)

    def test_open_archive_html(self):
        obj1 = storytracker.archive(
            self.url,
            output_dir=self.tmpdir,
            compress=False
        )
        obj2 = storytracker.open_archive_filepath(obj1.html_archive_path)
        self.assertEqual(obj1, obj2)

    def test_url(self):
        self.archive = storytracker.archive(self.url)
        obj = self.archive

        # Metadata
        self.assertEqual(self.url, obj.url)
        obj.timestamp
        obj.html
        obj.gzip
        obj.__unicode__()
        obj.__str__()
        obj.__repr__()

        # Browser
        self.assertEqual(self.archive._browser, None)
        self.archive.get_browser()
        self.assertTrue(isinstance(self.archive._browser, webdriver.PhantomJS))
        self.archive.close_browser()
        self.assertEqual(self.archive._browser, None)
        self.archive.close_browser()

        # Gzip
        self.assertEqual(obj.gzip_archive_path, None)
        obj.write_gzip_to_directory(self.tmpdir)

        # Hyperlinks
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

        # Hyperlinks to CSV
        f = six.StringIO()
        f = obj.write_hyperlinks_csv_to_file(f)
        p = os.path.join(self.tmpdir, 'links.csv')
        f2 = open(p, 'w+')
        f2 = obj.write_hyperlinks_csv_to_file(f2)
        self.assertTrue(os.path.exists(p))
        os.remove(p)

        # Images
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

    def test_analyze(self):
        self.archive = storytracker.archive(self.url)
        self.assertEqual(self.archive._hyperlinks, [])
        self.assertEqual(self.archive._images, [])
        self.archive.analyze()
        self.assertTrue(
            isinstance(self.archive._hyperlinks[0], storytracker.Hyperlink)
        )
        self.assertTrue(
            isinstance(self.archive._images[0], storytracker.Image)
        )

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


class WaybackMachineTest(MutedTest):

    def setUp(self):
        super(WaybackMachineTest, self).setUp()
        self.url = "https://web.archive.org/web/20010911213814/\
http://www.cnn.com/"

    def test_url_reverse(self):
        reverse = storytracker.reverse_wayback_machine_url(self.url)
        self.assertTrue(isinstance(reverse[0], str))
        self.assertTrue(isinstance(reverse[1], datetime))

    def test_url_open(self):
        obj = storytracker.open_wayback_machine_url(self.url)
        self.assertEqual("http://www.cnn.com/", obj.url)
        obj.timestamp
        obj.html
        obj.gzip
        obj.hyperlinks
        obj.__unicode__()
        obj.__str__()
        obj.__repr__()
        obj.write_gzip_to_directory(self.tmpdir)

#
# CLI tests
#

#if six.PY2:
#    class CLITest(BaseTest):

#        def setUp(self):
#            super(CLITest, self).setUp()
#            self.this_dir = os.path.dirname(os.path.abspath(__file__))
#            sys.path.append(self.this_dir)

#        def test_get(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-get")
#            cmd = '%s %s' % (path, self.url)
#            process = Command(cmd)
#            code, out, err = process.run(timeout=3)
#            python = storytracker.get(self.url).encode("utf-8")
#            self.assertEqual(type(out), type(python))
#            self.assertEqual(out, python)

#        def test_get_no_verify(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-get")
#            cmd = '%s %s --do-not-verify' % (path, self.url)
#            process = Command(cmd)
#            code, out, err = process.run(timeout=3)
#            python = storytracker.get(self.url).encode("utf-8")
#            self.assertEqual(type(out), type(python))
#            self.assertEqual(out, python)

#        def test_archive(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-archive")
#            cmd = '%s %s --do-not-compress' % (path, self.url)
#            process = Command(cmd)
#            code, out, err = process.run(timeout=3)
#            python = storytracker.archive(self.url).html.encode("utf-8")
#            self.assertEqual(type(out), type(python))
#            self.assertEqual(out, python)

#        def test_archive_gzipped(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-archive")
#            cmd = '%s %s' % (path, self.url)
#            process = Command(cmd)
#            code, out, err = process.run(timeout=3)
#            python = storytracker.archive(self.url).gzip
#            self.assertEqual(type(out), type(python))
#            self.assertEqual(out, python)

#        def test_archive_output_dir(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-archive")
#            cmd1 = "%s %s --output-dir=%s" % (
#                path, self.url, self.tmpdir
#            )
#            code1, path1, err1 = Command(cmd1).run(timeout=3)
#            obj1 = storytracker.open_archive_filepath(path1)
#            self.assertTrue(isinstance(obj1, storytracker.ArchivedURL))
#            self.assertTrue(os.path.exists(path1))
#            os.remove(path1)

#        def test_archive_output_dir_html(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-archive")
#            cmd2 = "%s %s --do-not-compress --output-dir=%s" % (
#                path, self.url, self.tmpdir
#            )
#            code2, path2, err2 = Command(cmd2).run(timeout=3)
#            obj2 = storytracker.open_archive_filepath(path2)
#            self.assertTrue(os.path.exists(path2))
#            os.remove(path2)

#        def test_links2csv_filepath(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-links2csv")
#            obj = storytracker.archive(self.url, output_dir=self.tmpdir)
#            cmd = "%s %s" % (path, obj.archive_path)
#            code, out, err = Command(cmd).run(timeout=3)

#        def test_links2csv_filedirectory(self):
#            path = os.path.join(self.this_dir, "bin/storytracker-links2csv")
#            obj = storytracker.archive(self.url, output_dir=self.tmpdir)
#            cmd = "%s %s" % (path, self.tmpdir)
#            code, out, err = Command(cmd).run(timeout=3)


if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
