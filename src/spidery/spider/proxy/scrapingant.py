#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

import requests

from spidery.spider.engine import ProxyEngine


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://scrapingant.com/free-proxies/']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _fetch_url(self, url, **kwargs):
        flag = None
        try:

            response = self.get(url)
            if response and response.ok:
                response.encoding = 'utf-8'
                flag = re.sub("</t[hd]><td>", ":", re.sub(r"\s{2,}", "", response.text), 0,
                              re.IGNORECASE | re.MULTILINE)
        except requests.ConnectionError:
            pass
        finally:
            return str(flag)


if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
