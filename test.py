import unittest
import storytracker


class BaseTest(unittest.TestCase):

    def setUp(self):
        pass


class ArchiveTest(BaseTest):

    def test_nothing(self):
        url = "http://www.latimes.com"
        html = storytracker.get(url)
        storytracker.archive(url)
        try:
            storytracker.get("http://www.trbimg.com/img-5359922b/turbine/\
la-me-lafd-budget-20140415-001/750/16x9")
        except ValueError:
            pass
        storytracker.get(
            "http://www.trbimg.com/img-5359922b/turbine/la-me-lafd-budget-\
20140415-001/750/16x9",
            verify=False
        )


if __name__ == '__main__':
    unittest.main()
