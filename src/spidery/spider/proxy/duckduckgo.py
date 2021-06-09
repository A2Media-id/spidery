#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import random
import re
import traceback
from urllib.parse import quote_plus, unquote

import bs4
import requests

from spidery.spider.constants import REGEX_PROXY
from spidery.spider.engine import ProxyEngine
from spidery.spider.resource import ProxyData
from spidery.utils.func import strip_html


class Engine(ProxyEngine):
    _me = __file__
    keywords = [
        "proxy list",
        "proxy list :3128",
        "anonymous elite transparent 3128",
        "free http proxies",
        "free http proxy list",
        "ssl proxy pastebin",
        "ssl proxy list",
        "proxy api free",
        "IP Port Anonymity 3128",
        "free https proxies",
        "free https proxy list",
        "https proxies",
        "https proxy list",
        "proxy rotator free",
        "proxy rotator :3128",
        "proxies list",
        "USA https proxy",
        "proxy scrape list",
        "proxy sites",
        "free proxy list",
        "daily proxies",
        "instagram proxies",
        "facebook proxy list",
        "squid proxy list",
        "google ssl proxy list",
        "United States free proxy servers",
        "Indonesia elite 8080 3128",
        "MX elite 8080 3128",
        "Free Anonymous 3128 Proxy",
        "anonymous proxies list",
        "Proxy list for country: United States",
    ]

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _fetch_url(self, url, **kwargs):
        flag = None
        try:
            response = self.get(url, params={'q': quote_plus(self.keyword)})
            if response and response.ok:
                response.encoding = 'utf-8'
                flag = unquote(response.text)
        except requests.ConnectionError:
            pass
        finally:
            return str(flag)

    @property
    def keyword(self):
        return random.choice(self.keywords)

    @property
    def urls(self):
        return [f"https://html.duckduckgo.com/html"]

    def _parse_raw(self, html):
        try:
            soup = bs4.BeautifulSoup(html, "html.parser")
            archives = soup.find_all('a', class_='result__url', text=True)
            for i, a in enumerate(archives):
                try:
                    link = str(a.text).strip()
                    raw = self.get(f'http://{link}')
                    if raw:
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
