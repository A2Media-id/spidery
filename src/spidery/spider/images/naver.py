import json
import logging
import traceback
from typing import List, Dict
from urllib.parse import unquote

from spidery.spider.images import ImageEngine
from spidery.spider.resource import DataImage


class Engine(ImageEngine):
    """The resource quality of this engine is good, but the search is a bit slow (there are too many invalid resources)"""
    _regex = r"controller\.start\((\[.*\])\);\skeep\.on\("
    _limit = 25
    _me = __file__

    def _loop_search(self, term: str, page: int):
        result = []
        api = 'https://s.search.naver.com/p/c/image/search.naver'
        params = {
            'where': 'image',
            # 'rev': '43',
            'section': 'image',
            'query': term,
            'ac': '0',
            'aq': '0',
            'spq': '0',
            'nx_search_query': term,
            'nx_and_query': '',
            'nx_sub_query': '',
            'nx_search_hlquery': '',
            'nx_search_fasquery': '',
            'res_fr': '0',
            'res_to': '0',
            'color': '',
            'datetype': '0',
            'startdate': '0',
            'enddate': '0',
            'nso': 'so:r,a:all,p:all',
            'json_type': '6',
            'nlu_query': json.dumps({"timelineQuery": term}),
            'nqx_theme': '{"theme":{"main":{"name":"dictionary_en"},"sub":[{"name":"webtoon"},{"name":"language"}]}}',
            'gif': '0',
            'optStr': '',
            'ccl': '0',
            'nq': '',
            'dq': '',
            'tq': '',
            'x_image': '',
            'display': '100',
            'start': '/{',
        }
        ret = self.get(url=api, params=params)  # Both keywords and results must be gb2312 encoding
        if not ret:
            logging.error(f"Engine {self.me()} search failed: {term}")
            return False, result
        if 'itemCount' not in ret.text:
            logging.error(f"Engine {self.me()} search failed: {term} server did not return results")
            return False, result
        json_raw = ret.text.replace("({", "{").replace("})", "}")
        data = json.loads(json_raw)
        items: List[Dict] = data.get('items')
        try:
            while items and True:
                try:
                    item = items.pop()
                    dat = DataImage(engine=self.me())
                    for k, v in item.items():
                        value = unquote(v).strip() if (v and type(v) == str) else v
                        if k == 'title':
                            dat.title = value
                            dat.desc = value
                        elif k == 'originalUrl':
                            dat.url = value
                        elif k == 'link':
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
    for news in eng.search('cicak'):
        print(news)
