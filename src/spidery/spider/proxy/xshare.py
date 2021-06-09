#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import traceback

import bs4

from spidery.spider.constants import REGEX_PROXY
from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData
from spidery.utils.func import strip_html


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://www.xshare.pro/category/mmo/share-proxy']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _parse_raw(self, html):
        try:
            soup = bs4.BeautifulSoup(html, "html.parser")
            archives = soup.find_all('a', {'href': re.compile(".txt")})
            for i, a in enumerate(archives):
                try:
                    raw = self.get(a.get('href'))
                    march_group = re.findall(REGEX_PROXY, strip_html(raw.text), re.IGNORECASE)
                    for group in march_group:
                        host, port = group
                        yield ProxyData(**{
                            'host': host,
                            'port': port,
                            'country': None,
                            'type': 'https' if str(port) == '8080' else 'http',
                        })
                except Exception as error:
                    logging.exception(
                        ''.join(
                            traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))

        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))


if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
