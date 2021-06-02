#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import traceback

import bs4

from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData
from spidery.utils.func import pad


class Engine(ProxyEngine):
    _me = __file__
    urls = [
        'https://adok2.io/free-proxy-list',
    ]

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _parse_raw(self, html):
        try:
            soup = bs4.BeautifulSoup(html, "html.parser")
            for tr in soup.find_all('tr'):
                try:
                    host, port, country_code, country, speed = pad(str(tr.text).strip().split(' '), 5, None)
                    yield ProxyData(**{
                        'host': str(host).strip(),
                        'port': str(port).strip(),
                        'country': str(country_code).strip(),
                        'type': 'https' if str(port).strip() == '8080' else 'http',
                    })
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))


if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
