import os
import unittest
import storytracker


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://www.latimes.com"
        self.img = "http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9"


class ArchiveTest(BaseTest):

    def test_get(self):
        html = storytracker.get(self.url)
        try:
            storytracker.get(self.img)
        except ValueError:
            pass
        storytracker.get(self.img, verify=False)

    def test_archive(self):
        storytracker.archive(self.url)
        storytracker.archive(self.url, compress=False)
        storytracker.archive(self.url, output_path="./foo.gz")
        os.remove("./foo.gz")
        storytracker.archive(
            self.url,
            compress=False,
            output_path="./foo.html"
        )
        os.remove("./foo.html")


if __name__ == '__main__':
    unittest.main()  
