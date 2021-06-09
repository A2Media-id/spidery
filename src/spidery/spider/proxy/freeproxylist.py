#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import traceback

from bs4 import BeautifulSoup

from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData
from spidery.utils.func import pad


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://free-proxy-list.net']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _parse_raw(self, html):
        try:

            soup = BeautifulSoup(html, "html.parser")
            table = soup.find('table', id='proxylisttable')
            rows = table.tbody.find_all('tr')
            for tr in rows:
                try:
                    host, port, country_code, country_name, anonymity, support_google, support_https, last_check = pad(
                        list(map(lambda x: x.text, tr.find_all('td'))), 8, None)
                    yield ProxyData(**{
                        'host': host,
                        'port': port,
                        'country': country_code,
                        'type': 'https' if str(support_https).lower() != 'no' else 'http',
                    })
                    yield None
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
