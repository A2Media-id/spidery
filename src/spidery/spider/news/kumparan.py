#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
import traceback
from typing import List

from bs4 import BeautifulSoup

from spidery.spider.news import NewsEngine
from spidery.spider.resource import DataNews, DataArticle, DataArticleImage


class Engine(NewsEngine):
    _me = __file__
    base = 'https://kumparan.com'

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)

    def get_detail(self, data: DataNews):
        result = None
        try:
            article = DataArticle(**data.__dict__)
            soup = self.get_soup(data.link)
            el_content = soup.find(id='content')

            def not_adunit(tag):
                if tag.find(class_='adunitContainer'):
                    return None
                elif tag.find('figure'):
                    return None
                return tag.text

            meta_author = soup.find(href=re.compile("organisation-info")) or soup.find(id='track_author_name')
            author = str(meta_author.text.strip()).capitalize() if meta_author else None
            news_content = el_content.find('div', class_=re.compile("StoryRenderer"))
            # print(news_content.prettify())
            el_setences = news_content.find_all(class_=re.compile("TextBoxweb__StyledTextBox"), string=True)
            el_images = news_content.find_all('figure', class_=re.compile("StyledFigure")) or news_content.find_all(
                'img')
            track_tags_items = el_content.select("[class~=track_tags_item]")
            tags = list(map(lambda x: x.text, track_tags_items))
            setences = list(map(lambda x: x.text.replace('\n', '').strip(), el_setences))
            # data_images = list(map(lambda x: x.text.replace('\n', '').strip(), el_images))
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

    def get_latest(self) -> List[DataNews]:
        try:
            soup = self.get_soup(f'{self.base}/trending')
            items: List[BeautifulSoup] = soup.find_all(attrs={"data-qa-id": "news-item"})
            for item in items:
                title = item.find(attrs={"data-qa-id": "title"}).text
                thumbnail = item.find('img', class_='no-script').get('src')
                link = item.find('a', class_=re.compile("LabelLinkweb")).get('href')
                tags = []
                yield DataNews(**{
                    'engine': self.me(),
                    'title': title.replace('\n', '').strip(),
                    'thumbnail': re.sub(r",(w_\d+|ar_\d+:\d+)", "", str(thumbnail).strip(), 0,
                                        re.IGNORECASE | re.VERBOSE),
                    'link': f'{self.base}/{str(link).lstrip("/")}',
                    'tags': tags,
                })
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))


if __name__ == '__main__':
    eng = Engine()
    for news in eng.get_latest():
        article = eng.get_detail(news)
        print(article.__dict__)
        break
