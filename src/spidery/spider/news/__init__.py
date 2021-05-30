#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import traceback
from abc import abstractmethod, ABC
from typing import List

from .spider import BaseCrawl
from .spider.resource import DataNews, DataArticle
from bs4 import BeautifulSoup


class NewsEngine(BaseCrawl, ABC):
    _me = __file__

    def __init__(self, **kwargs):
        super(NewsEngine, self).__init__(**kwargs)

    @staticmethod
    def _get_all_images(soup: BeautifulSoup) -> List:
        results = []
        try:
            attrs = ['src', 'data-src', 'data-srcset']
            datas = soup.find_all('img') or []
            added=set()
            for i, im in enumerate(datas):
                default_text = im.get('alt') or im.text
                parent = im.parent
                if not default_text and parent:
                    default_text = parent.string
                text = str(default_text).replace('\n', '').strip()
                for atr in attrs:
                    if not im.get(atr):
                        continue
                    ims = str(im.get(atr)).split()
                    for img in ims:
                        if re.search(r"https?://([A-Za-z_0-9.-]+)(\/[^\s]+)?", img, re.IGNORECASE) and img not in added:
                            image = re.sub(r"(,(w_\d+|ar_\d+:\d+)|\/w\d+$)", "", str(img).strip(), 0, re.IGNORECASE | re.VERBOSE)
                            added.add(img)
                            results.append((image, text))
        except Exception as error:
            logging.error(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return results

    @abstractmethod
    def get_detail(self, data: DataNews) -> DataArticle:
        pass

    @abstractmethod
    def get_latest(self) -> List[DataNews]:
        pass
