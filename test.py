import os
import sys
import six
import unittest
import storytracker


class NullDevice():
    """
    A nothingburger to replace stdout with while running tests.
    """
    def write(self, s):
        pass


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://www.latimes.com"
        self.img = "http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9"
        # Turning off stdout temporarily
        original_stdout = sys.stdout
        sys.stdout = NullDevice()


class ArchiveTest(BaseTest):

    def test_get(self):
        from storytracker.get import main
        storytracker.get(self.url)
        main(self.url)
        try:
            storytracker.get(self.img)
        except ValueError:
            pass
        storytracker.get(self.img, verify=False)
        main(self.img, verify=False)

    def test_archive(self):
        from storytracker.archive import main
        for f in [storytracker.archive, main]:
            f(self.url)
            f(self.url, minify=False)
            f(self.url, extend_urls=False)
            f(self.url, compress=False)
            f(self.url, output_path="./foo.gz")
            os.remove("./foo.gz")
            f(
                self.url,
                compress=False,
                output_path="./foo.html"
            )
            os.remove("./foo.html")


if __name__ == '__main__':
    if six.PY3:
        unittest.main(warnings='ignore')
    else:
        unittest.main()
