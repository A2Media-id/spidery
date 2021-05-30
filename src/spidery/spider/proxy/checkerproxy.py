#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import traceback

from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData
from spidery.utils.func import pad


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://checkerproxy.net/getAllProxy']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _parse_raw(self, html):
        try:
            archives = re.findall(r"(archive/\d{4}-\d{2}-\d{2})", html, re.IGNORECASE | re.MULTILINE)
            for archive in archives:
                headers = {
                    'authority': 'checkerproxy.net',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
                    'sec-ch-ua-mobile': '?0',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.49',
                    'accept': '*/*',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': f'https://checkerproxy.net/archive/{archive}',
                    'accept-language': 'en-US,en;q=0.9',
                }
                proxies = self._get_json(f'https://checkerproxy.net/api/{archive}', headers=headers)
                if proxies:
                    for _, proxy in enumerate(proxies):
                        try:
                            host, port = pad(str(proxy.get('addr')).split(':'), 2, None)
                            if not host:
                                continue
                            elif not port:
                                continue
                            yield ProxyData(**{
                                'host': host,
                                'port': port,
                                'country': proxy.get('ip_geo_iso'),
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
