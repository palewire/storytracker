#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import storytracker


class BaseTest(unittest.TestCase):

    def setUp(self):
        pass



class ArchiveTest(BaseTest):

    def test_nothing(self):
        html = storytracker.get("http://www.latimes.com")
        path = storytracker.archive(html)
        try:
            storytracker.get("http://www.trbimg.com/img-5359922b/turbine/la-me-lafd-budget-20140415-001/750/16x9")
        except ValueError:
            pass
        storytracker.get(
            "http://www.trbimg.com/img-5359922b/turbine/la-me-lafd-budget-20140415-001/750/16x9",
            verify=False
        )



if __name__ == '__main__':
    unittest.main()
