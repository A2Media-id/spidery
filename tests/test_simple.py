# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from spidery.spider.engine import ProxyGrabber


class TestSimple(unittest.TestCase):

    def test(self):
        mods=ProxyGrabber().scripts.keys()
        print(mods)
        self.assertTrue(len(mods) > 0)


if __name__ == '__main__':
    unittest.main()
