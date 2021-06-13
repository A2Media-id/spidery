#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import pickle
import random
import traceback
from typing import List

from spidery.spider.engine import BaseCrawl

KEYS_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr_space.bin')


class Ocr(BaseCrawl):
    _me = __file__
    base = 'https://api.ocr.space'
    keys: List = pickle.load(open(KEYS_BIN, 'rb'))
    _key = None

    def __init__(self, apikey=None, **kwargs):
        super(Ocr, self).__init__(**kwargs)
        self.apikey = apikey

    @property
    def apikey(self):
        if not self._key:
            self._key = random.choice(self.keys)
        return self._key

    @apikey.setter
    def apikey(self, value: str):
        self._key = value.strip() if value else value

    def recognize(self, image_file: str, **kwargs):
        result = None
        try:
            params = {
                'isOverlayRequired': kwargs.get('overlay', False),
                'apikey': self.apikey,
                'language': kwargs.get('language', 'eng'),
            }
            if os.path.isfile(image_file):
                file_path, file_name = os.path.split(image_file)
                payload_files = {file_name: open(image_file, mode='rb').read()}
                req = self.request(method='POST', url=f'{self.base}/parse/image', data=params,
                                   files=payload_files)
            else:
                params.update(url=image_file)
                req = self.post(f'{self.base}/parse/image', data=params)
            if req and req.json() and 'ParsedResults' in req.json():
                parsed = req.json().get('ParsedResults', [])
                result = parsed.pop().get('ParsedText', None)
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return result


if __name__ == '__main__':
    with Ocr() as ocr:
        print(ocr.recognize('https://i.pinimg.com/564x/9c/50/be/9c50beb7ca0cfbf1b7229f4696242758.jpg'))
