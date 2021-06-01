#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os
import pickle
import random
import traceback
from datetime import datetime, timedelta

import requests

from spidery.spider.engine import BaseCrawl

AUTH_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zoomeye.bin')


class Engine(BaseCrawl):
    base_url = 'https://api.zoomeye.org'
    auths = pickle.load(open(AUTH_BIN, 'rb'))

    def __init__(self, **kwargs):
        super(Engine, self).__init__(**kwargs)
        self.access_token = kwargs.get('access_token', None)
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self._prepare()

    def _prepare(self):
        try:
            if not self.access_token and (self.username and self.password):
                new_token = self.auth(self.username, self.password)
                if new_token:
                    self.access_token = new_token
            else:
                auths = random.sample(self.auths, k=len(self.auths))
                for aux in auths:
                    u, p = aux
                    new_token = self.auth(u, p)
                    print(u, new_token)
                    if new_token:
                        self.access_token = new_token
                        break

        except requests.ConnectionError:
            pass

    def auth(self, username, password):
        flag = False
        try:
            headers = {'Content-type': 'application/json; charset=UTF-8', 'Accept': 'application/json'}
            response = self.post(f'{self.base_url}/user/login', headers=headers,
                                 data=json.dumps({'username': username, 'password': password}))
            data = response.json() if response and response.json() else {}
            flag = data.get('access_token')
        except requests.ConnectionError:
            pass
        finally:
            return flag

    @property
    def info(self):
        flag = False
        try:
            if self.access_token:
                headers = {
                    'Authorization': 'JWT %s' % self.access_token
                }
                response = self.get(f'{self.base_url}/resources-info', headers=headers)
                data = response.json() if response and response.json() else None
                flag = data
        except requests.ConnectionError:
            pass
        finally:
            return flag

    def search(self, **kwargs):
        results = []
        try:
            query = kwargs.get('query', None)
            query_type = kwargs.get('type', 'host')
            info = self.info
            if query and info and info.get('resources'):
                print("Plan {0}".format(info.get('plan')))
                print("Search limit {0}".format(info.get('resources').get('search')))
                headers = {
                    'Accept': 'application/json',
                    'Authorization': 'JWT %s' % self.access_token
                }
                for i in range(1, kwargs.get('page', 10) + 1):
                    try:
                        params = {'query': query, 'page': i, 't': 'v4'}
                        print(f'Search on page : {i}')
                        response = self.get(f'{self.base_url}/{query_type}/search', headers=headers, params=params)
                        data = json.loads(response.text) if response and response.ok else {}
                        for item in data.get('matches', []):
                            results.append(item)
                    except (KeyboardInterrupt, requests.ConnectionError):
                        break
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return results


if __name__ == '__main__':
    with Engine() as engine:
        print(engine.info)
        now = datetime.now()
        before_date = now.strftime('%Y-%m-%d')
        after_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        results = engine.search(
            query=f'+service:"https-proxy" +app:"MikroTik" +title:"Gateway Timeout" +after:"{after_date}" +before:"{before_date}"')
        print(json.dumps(results, indent=4))
