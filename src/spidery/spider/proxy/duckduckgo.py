#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ipaddress
import logging
import random
import traceback

from spidery.spider.engine import ProxyEngine
from spidery.spider.snippet.duckduckgo import Engine as Duck
from spidery.utils.func import strip_html


class Engine(ProxyEngine):
    _me = __file__
    _keywords = [
        "proxy list",
        "proxy list :3128",
        "anonymous elite transparent 3128",
        "free http proxies",
        "free http proxy list",
        "ssl proxy pastebin",
        "ssl proxy list",
        "free https proxies",
        "free https proxy list",
        "https proxies",
        "https proxy list",
        "proxies list",
        "USA https proxy",
        "proxy scrape",
        "proxy sites",
        "free proxy list",
        "daily proxies",
        "instagram proxies",
        "facebook proxy list",
        "squid proxy list",
        "google ssl proxy",
        "Indonesia elite 8080 3128",
        "MX elite 8080 3128",
        "anonymous proxies",
    ]
    urls = ['https://free-proxy-list.net']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    @property
    def keywords(self):
        return random.sample(self._keywords, k=5)

    def search(self):
        processed = []
        result = []
        for keyword in self.keywords:
            logging.info(f'[!]Dorking for keyword {keyword}')
            # if len(result) >= 1000:
            #     break
            with Duck() as duck:
                snipets = duck.search(keyword)
                for snipet in snipets:
                    if snipet.link in processed:
                        continue
                    logging.info(f'fetching {snipet.link}')
                    html = self._fetch_url(snipet.link)
                    parsed = self._parse_raw(strip_html(html))
                    if parsed:
                        for _ in parsed:
                            try:
                                if not ipaddress.IPv4Address(_.host).is_private and _.host not in result:
                                    result.append(_)
                                    yield _
                            except ValueError:
                                continue
                            except Exception as error:
                                logging.exception(''.join(
                                    traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                    processed.append(snipet.link)
        logging.info(f'fetching complete')


if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
