#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import random
import traceback
from urllib.parse import quote_plus

from spidery.spider.engine import BaseCrawl
from spidery.spider.resource import DataSnipet


class Engine(BaseCrawl):
    _me = __file__

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def search(self, term: str):
        results = []
        params = {
            'q': quote_plus(term),
            'form': random.choice(['QBLH', 'ANNNB1']),
            'qs': 'EP',
            'pq': term,
            'sk': None,
            'first': 1,
            'count': 50,
            'sc': '8-1',
            'cvid': None,
            'refig': None,
        }

        url = "https://global.bing.com/search"
        response = self.get(url, params=params)
        if not response:
            return results
        elif not response.text:
            return results
        try:
            raw = response.text
            for result_element in self.xpath(raw, "//li[@class='b_algo']"):
                try:
                    item = {
                        'engine': self.me(),
                        'title':
                            ''.join(result_element.xpath(".//h2/a/text()")).strip(),
                        'link':
                            result_element.xpath(".//h2/a/@href")[0],
                        'snippet':
                            ''.join(result_element.xpath(".//div/p/text()"))
                    }
                    if not item.get('snippet'):
                        continue
                    elif item.get('link') and self.blacklisted_domain(item.get('link')):
                        continue
                    results.append(DataSnipet(**item))
                except (KeyError, IndexError):
                    continue
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                    continue
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return results


def test(query):
    try:
        with Engine() as bek:
            suggests = bek.search(query)

            print(json.dumps(suggests, ensure_ascii=False, indent=4, default=lambda x: x.__dict__))
            print(len(suggests))
    except Exception as error:
        logging.exception(
            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        raise


if __name__ == '__main__':
    test('Sandal murah')
