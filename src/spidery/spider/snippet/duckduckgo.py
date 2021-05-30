#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import traceback
from urllib.parse import quote_plus

from spidery.spider.engine import BaseCrawl
from spidery.spider.resource import DataSnipet


class Engine(BaseCrawl):
    _me = __file__

    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__( **kwargs)

    def search(self, term: str):
        results = []
        params = {'q': quote_plus(term)}
        url = "https://html.duckduckgo.com/html/"
        response = self.get(url, params=params)
        if not response:
            return results
        elif not response.text:
            return results
        try:
            raw = response.text
            for result_element in self.xpath(raw, "//div[contains(@class, 'result__body')]"):
                try:
                    item = {
                        'engine': self.me(),
                        'title':
                            ''.join(result_element.xpath(".//h2[@class='result__title']//text()")).strip(),
                        'link':
                            result_element.xpath(".//a[@class='result__a']/@href")[0],
                        'snippet':
                            ''.join(result_element.xpath(".//a[@class='result__snippet']//text()"))
                    }
                    if item.get('link') and 'duckduckgo.com' in item.get('link'):
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
    except Exception as error:
        logging.exception(
            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        raise


if __name__ == '__main__':
    test('https proxy')
