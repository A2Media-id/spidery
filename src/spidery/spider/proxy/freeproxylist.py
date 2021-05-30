#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import traceback

from pyquery import PyQuery

from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://free-proxy-list.net']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _parse_raw(self, html):
        try:
            doc = PyQuery(html)
            table = doc.find('table#proxylisttable')
            tbody = table.find('tbody')
            for html_tr in tbody.items('tr'):
                try:
                    host, port, country_code, country_name, anonymity, support_google, support_https, last_check = [
                        i.text()
                        for i in
                        html_tr.items(
                            'td')]
                    yield ProxyData(**{
                        'host': host,
                        'port': port,
                        'country': country_code,
                        'type': 'https' if str(support_https).lower() != 'no' else 'http',
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
