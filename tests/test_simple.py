# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from spidery.spider.engine import ProxyGrabber


class TestSimple(unittest.TestCase):

    def test(self):
        with ProxyGrabber() as sp:
            proxies = sp.search(limit=100,workers=3)
            self.assertTrue(len(proxies) >= 100)


if __name__ == '__main__':
    unittest.main()
