#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List

from spidery.spider.engine import BaseCrawl
from spidery.spider.resource import DataImage


class ImageEngine(BaseCrawl, ABC):

    def __init__(self, **kwargs):
        super(ImageEngine, self).__init__(**kwargs)
        self.max_page = kwargs.get('max_page', 2)

    def search(self, term) -> List[DataImage]:
        result = []
        page = 1
        while page <= self.max_page:
            has_next, ret = self._loop_search(term, page)
            result += ret
            if not has_next:
                break
            page += 1
        return result

    @abstractmethod
    def _loop_search(self, term: str, page: int) -> [bool, List]:
        pass
