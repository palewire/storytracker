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


if __name__ == '__main__':
    unittest.main()
