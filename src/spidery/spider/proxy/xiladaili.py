#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import traceback

from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData


class Engine(ProxyEngine):
    _me = __file__
    urls = ['http://www.xiladaili.com/shareip/']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)
        for x in range(2, 5):
            self.urls.append(f'http://www.xiladaili.com/https/{x}')

    def _parse_raw(self, html):
        try:
            march_group = re.findall(r"((?:\d{1,3}\.){3}\d{1,3}):(\d{2,5})", str(html), re.IGNORECASE)
            for group in march_group:
                try:
                    host, port = group
                    yield ProxyData(**{
                        'host': host,
                        'port': port,
                        'type': 'https' if str(port) == '8080' else 'http',
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
