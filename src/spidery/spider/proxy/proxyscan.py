#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

import requests

from spidery.spider.engine import ProxyEngine


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://www.proxyscan.io']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def _fetch_url(self, url, **kwargs):
        flag=None
        try:
            headers = {
                'Connection': 'keep-alive',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.proxyscan.io',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://www.proxyscan.io/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            data = {
                'status': '1',
                'ping': '',
                'selectedType': 'HTTPS',
                'sortPing': 'true',
                'sortTime': 'true',
                'sortUptime': 'true'
            }
            response = self.post(f'{url}/Home/FilterResult', headers=headers,data=data)
            if response and response.ok:
                response.encoding = 'utf-8'
                flag = re.sub("</th><td>", ":", re.sub(r"\s{2,}","",response.text), 0, re.IGNORECASE | re.MULTILINE)
        except requests.ConnectionError:
            pass
        finally:
            return str(flag)



if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
