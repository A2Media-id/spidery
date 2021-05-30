import html
import json
import logging
import re
import traceback
from urllib.parse import quote_plus, unquote

from spidery.spider.images import ImageEngine
from spidery.spider.resource import DataImage


class Engine(ImageEngine):
    """The resource quality of this engine is good, but the search is a bit slow (there are too many invalid resources)"""
    _regex = r"m=\"(\{\&quot\;cid[^\"]+\})\""
    _limit = 25
    _me = __file__

    def _loop_search(self, term: str, page: int):
        result = []
        api = 'https://www.bing.com/images/async'
        params = {'q': quote_plus(term), 'first': (page * self._limit + 1), 'count': self._limit,
                  'qft': '+filterui:imagesize-large', 'adlt': 'off',
                  'safeSearch': 'off'}
        ret = self.get(url=api, params=params)  # Both keywords and results must be gb2312 encoding
        if not ret:
            logging.error(f"Engine {self.me()} search failed: {term}")
            return False, result
        if not re.search(Engine._regex, ret.text, re.IGNORECASE | re.MULTILINE):
            logging.error(f"Engine {self.me()} search failed: {term} server did not return results")
            return False, result
        items = re.findall(self._regex, ret.text)
        if items:
            items = set(map(html.unescape, items))
            try:
                while items and True:
                    try:
                        item = json.loads(items.pop())
                        dat = DataImage(engine=self.me())
                        for k, v in item.items():
                            value = unquote(v).strip() if (v and type(v) == str) else v
                            if k == 't':
                                dat.title = value
                            elif k == 'desc':
                                dat.desc = value
                            elif k == 'murl':
                                dat.url = value
                            elif k == 'purl':
                                dat.source = value
                        if not dat.url:
                            continue
                        elif dat.url and self.blacklisted_domain(dat.url):
                            continue
                        else:
                            result.append(dat)
                    except KeyboardInterrupt:
                        return
                    except Exception as error:
                        logging.exception(
                            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                        raise
            except Exception as error:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        now_page, total_page = (page, self._limit)
        has_next = (int(now_page) < int(total_page) and len(result))  # Whether there is a next page
        logging.info(f"Engine {__class__.__module__} is searching: {term} ({now_page}/{total_page})")
        return has_next, result


if __name__ == '__main__':
    eng = Engine()
    for news in eng.search('Larissa Chou Gugat Cerai Alvin Faiz'):
        print(news)
