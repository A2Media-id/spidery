# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from spidery.spider.engine import Spider


class TestSimple(unittest.TestCase):

    def test(self):
        with Spider() as sp:
            self.assertTrue(isinstance(sp.engines,dict))


if __name__ == '__main__':
    unittest.main()
