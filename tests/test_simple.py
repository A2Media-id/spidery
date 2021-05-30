# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from spidery.spider.engine import BaseCrawl


class TestSimple(unittest.TestCase):

    def test_add_one(self):
        self.assertTrue(isinstance(BaseCrawl(),BaseCrawl))


if __name__ == '__main__':
    unittest.main()
