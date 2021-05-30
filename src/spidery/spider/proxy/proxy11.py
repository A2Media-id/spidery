#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from spidery.spider.engine import ProxyEngine


class Engine(ProxyEngine):
    _me = __file__
    urls = ['https://proxy11.com/api/demoweb/proxy.json?google=1']

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)


if __name__ == '__main__':
    eng = Engine()
    for proxy in eng.search():
        print(proxy)
