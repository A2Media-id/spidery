#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import mimetypes
import os
import re
import traceback

from spidery.spider.constants import REGEX_CLEANER
from spidery.utils.func import pad
from spidery.utils.jetpack import Photon


class BaseData(object):
    def __init__(self, **kwargs):
        self.engine = kwargs.get('engine')

    @staticmethod
    def clean_string(value: str):
        default = value
        for rt, rx in REGEX_CLEANER.items():
            try:
                rr, rv = pad(rx, 2, None)
                default = re.sub(rr, rv, default, 0, re.IGNORECASE)
            except Exception as error:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                pass
        return str('').join(default.split('|')).strip()


class DataSnippet(BaseData):
    def __init__(self, **kwargs):
        super(DataSnippet, self).__init__(**kwargs)
        self.engine = kwargs.get('engine')
        self.title = self.clean_string(str(kwargs.get('title')).title())
        self.link = kwargs.get('link')
        self.snippet = self.clean_string(str(kwargs.get('snippet')))

    def __str__(self):
        return self.snippet

    def __repr__(self):
        return (
            '<{class_name}('
            'title="{self.title}",'
            'snippet="{self.snippet}",'
            'engine="{self.engine}"'
            ')>'.format(
                class_name=self.__class__.__name__,
                self=self
            )
        )


class DataNews(BaseData):
    def __init__(self, **kwargs):
        super(DataNews, self).__init__(**kwargs)
        self.engine = kwargs.get('engine')
        self.title = self.clean_string(str(kwargs.get('title')).title())
        self.link = kwargs.get('link')
        self.thumbnail = str(kwargs.get('thumbnail')).strip()

    def __str__(self):
        return self.title

    def __repr__(self):
        return (
            '<{class_name}('
            'title="{self.title}",'
            'snippet="{self.snippet}",'
            'engine="{self.engine}"'
            ')>'.format(
                class_name=self.__class__.__name__,
                self=self
            )
        )


class DataArticle(BaseData):
    _content = None

    def __init__(self, **kwargs):
        super(DataArticle, self).__init__(**kwargs)
        self.engine = kwargs.get('engine')
        self.title = self.clean_string(str(kwargs.get('title')).title())
        self.link = str(kwargs.get('link')).strip()
        self.author = self.clean_string(str(kwargs.get('author')))
        self._content = str(kwargs.get('content'))
        self.tags = kwargs.get('tags')
        self.thumbnail = str(kwargs.get('thumbnail')).strip()
        self.images = kwargs.get('images')
        self.videos = kwargs.get('videos')

    def __str__(self):
        return self.title

    @property
    def content(self):
        return self.clean_string(str(self._content))

    @content.setter
    def content(self, text):
        self._content = str(text)

    def __repr__(self):
        return (
            '<{class_name}('
            'title="{self.title}",'
            'author="{self.author}",'
            'engine="{self.engine}"'
            ')>'.format(
                class_name=self.__class__.__name__,
                self=self
            )
        )


class DataImage(BaseData):
    def __init__(self, **kwargs):
        super(DataImage, self).__init__(**kwargs)
        self.engine = kwargs.get('engine')
        self.title = self.clean_string(str(kwargs.get('title')).title())
        self.url = kwargs.get('url')
        self.source = kwargs.get('source')
        self.desc = self.clean_string(str(kwargs.get('desc')).capitalize())

    def __str__(self):
        return self.url

    def __repr__(self):
        return (
            '<{class_name}('
            'title="{self.title}",'
            'url="{self.url}",'
            'engine="{self.engine}"'
            ')>'.format(
                class_name=self.__class__.__name__,
                self=self
            )
        )

    @property
    def url_cdn(self, **kwargs) -> str:
        return Photon(self.url, **kwargs).url.strip()

    def save_to_file(self, output_file: str, overwrite=False):
        from spidery.spider.engine import BaseCrawl

        flag = None
        try:
            print(f'[!] check image {self.url}')
            if os.path.isfile(output_file) and not overwrite:
                flag = output_file
                return flag
            with BaseCrawl() as crawl:
                try:
                    req = crawl.get(self.url_cdn) or crawl.get(self.url)
                    mime = req.headers.get('Content-Type')
                    print(f'[!] Content-Type {mime}')
                    if req and 'image' in mime:
                        im_path = os.path.dirname(output_file)
                        im_name = os.path.basename(output_file)
                        if not re.search(r"([a-zA-Z0-9_-]\.[a-zA-Z0-9]{3,4})$", output_file, re.IGNORECASE):
                            ext = str(mimetypes.guess_extension(mime) or 'jpg').lstrip('.')
                            clean_name = re.sub(r'\W+', '', im_name)
                            output_file = os.path.realpath(os.path.join(im_path, f'{clean_name}.{ext}'))
                        print(f'[!] {output_file}')
                        with open(output_file, 'wb+') as w:
                            w.write(req.content)
                            w.close()
                        print(f'[+] {self.url} saved')
                        flag = output_file
                except AttributeError:
                    print(f'[x] {self.url} invalid')
                    pass
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return flag


class DataArticleImage(DataImage):
    def __init__(self, **kwargs):
        super(DataArticleImage, self).__init__(**kwargs)


class DataSnipet(BaseData):
    def __init__(self, **kwargs):
        super(DataSnipet, self).__init__(**kwargs)
        self.engine = kwargs.get('engine')
        self.title = self.clean_string(str(kwargs.get('title')).title())
        self.link = kwargs.get('link')
        self.snippet = self.clean_string(str(kwargs.get('snippet')))

    def __str__(self):
        return self.snippet

    def __repr__(self):
        return (
            '<{class_name}('
            'title="{self.title}",'
            'snippet="{self.snippet}",'
            'engine="{self.engine}"'
            ')>'.format(
                class_name=self.__class__.__name__,
                self=self
            )
        )


class ProxyData(object):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.type = kwargs.get('type', 'http')
        self.country = kwargs.get('country')

    @property
    def url(self):
        return str(f"{self.type.lower().rstrip('s')}://{self.host}:{self.port}").lower()

    @property
    def format(self):
        return {
            "http": str(f"{self.type.lower().rstrip('s')}://{self.host}:{self.port}").lower(),
            "https": str(f"{self.type.lower().rstrip('s')}://{self.host}:{self.port}").lower(),
        }

    def __str__(self):
        return '{host}:{port}'.format(**self.__dict__)

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
