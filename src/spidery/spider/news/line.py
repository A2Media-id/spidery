#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import traceback
from typing import List

import unicodedata
from bs4 import BeautifulSoup

from spidery.spider.news import NewsEngine
from spidery.spider.resource import DataNews, DataArticle, DataArticleImage


class Engine(NewsEngine):
    _me = __file__
    base = 'https://today.line.me'

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def get_detail(self, data: DataNews):
        result = None
        try:
            article = DataArticle(**data.__dict__)
            soup = self.get_soup(data.link)
            el_content = soup.find(class_='articleContent')
            meta_author = soup.find(class_=re.compile("entityPublishInfo-publisher"))
            author = str(meta_author.text.strip()).capitalize() if meta_author else None
            news_content = el_content.find('article', class_=re.compile("news-content"))
            el_setences = news_content.find_all(string=True)
            track_tags_items = soup.select("[class~=chipButton-text]")
            tags = list(map(lambda x: x.text, track_tags_items))
            setences = list(
                map(lambda x: unicodedata.normalize("NFKD", x.string.replace('\n', '').strip()), el_setences))
            data_images = self._get_all_images(news_content)
            images = []
            for i, img in enumerate(data_images):
                img_url, img_caption = img
                article_image = DataArticleImage(engine=self.me(), title=data.title)
                article_image.url = img_url
                article_image.desc = img_caption
                images.append(article_image)
            article.author = author
            article.images = images
            article.content = str("\n").join(setences)
            article.tags = tags
            result = article
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return result

    def _get_latest(self) -> List[DataNews]:
        try:
            soup = self.get_soup(f'{self.base}/id/v2/tab/recommendation')
            march_group = re.findall(r'hash:\"([^\"]+)"},url:{hash:"([^\"]+)', str(soup), re.IGNORECASE)
            thumbs = []
            for group in march_group:
                try:
                    thumb, key = group
                    thumbs.append({'key': key, 'thumb': f'https://obs.line-scdn.net/{thumb}'})
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            items: List[BeautifulSoup] = soup.find_all('a', class_={"articleCard"})
            for item in items:
                title = item.find('span', class_=re.compile("articleCard-title")).text
                thumbnail = item.find('figure', class_=re.compile("articleCard-image")).get('data-src')
                link = item.get('href')
                item_key = str(link).split('/').pop()
                if not thumbnail:
                    for x in thumbs:
                        if x.get('key') == item_key and x.get('thumb'):
                            thumbnail = x.get('thumb')
                            break
                tags = []
                yield DataNews(**{
                    'engine': self.me(),
                    'title': title.replace('\n', '').strip(),
                    'thumbnail': str(thumbnail).replace(',w_160,ar_1:1', '').strip(),
                    'link': str('/').join([self.base.rstrip('/'), str(link).lstrip('/')]),
                    'tags': tags,
                })
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))

    def get_latest(self) -> List[DataNews]:
        try:
            headers = {
                'authority': 'today.line.me',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
                'accept': 'application/json, text/plain, */*',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://today.line.me/id/v2/tab/recommendation',
                'accept-language': 'en-US,en;q=0.9',
                'cookie': 'region=id',
            }

            params = (
                ('offset', '0'),
                ('length', '10'),
                ('country', 'id'),
                ('gender', ''),
                ('age', ''),
                ('excludeNoThumbnail', '1'),
                ('containMainSnapshot', '1'),
            )
            req = self.get(f'{self.base}/webapi/api/v6/recommendation/articles/listings/mytoday_rec:id',
                           headers=headers, params=params)
            items = req.json().get('items', []) if req and req.json() else []

            for item in items:
                tumb = item.get('thumbnail')
                urls = item.get('url')
                yield DataNews(**{
                    'engine': self.me(),
                    'title': item.get('title').replace('\n', '').strip(),
                    'thumbnail': str('/').join(
                        ['https://obs.line-scdn.net', str(tumb.get('hash')).lstrip('/')]) if tumb else None,
                    'link': urls.get('url').replace('\n', '').strip() if urls else None,
                    'tags': [item.get('categoryName')],
                })
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))


if __name__ == '__main__':
    eng = Engine()
    for news in eng.get_latest():
        article = eng.get_detail(news)
        print(article.__dict__)
