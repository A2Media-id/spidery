#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import importlib
import ipaddress
import logging
import os
import pickle
import re
import traceback
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests import Session
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from urllib3.exceptions import InsecureRequestWarning

# noinspection PyUnresolvedReferences
from spidery.spider.constants import BLACKLIST_DOMAIN, REGEX_PROXY
from spidery.spider.resource import ProxyData
from spidery.ua.agent import Agent
from spidery.utils.func import strip_html

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # noqa


class BaseCrawl(object):
    _default_headers = CaseInsensitiveDict({
        'accept': '*/*',
        'upgrade-insecure-requests': '1',
        'User-Agent': Agent().get_random(),
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'cache-ttl': '10',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    })
    _session = requests.session()
    _proxies = None
    _debug = None
    _me = __file__

    def __init__(self, **kwargs):
        self.headers = kwargs.get('headers') or self._default_headers
        self.session = kwargs.get('session') or self._session
        self.proxies = kwargs.get('proxies') or self._proxies

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

    def request(self, method, url, params=None, data=None, files=None, extra_headers=None, timeout=10):
        headers = self.headers.copy()
        csrf_token = self.session.cookies.get('csrftoken', domain=urlparse(url).netloc)
        if csrf_token:
            headers.update([('X-CSRFToken', csrf_token)])
        if extra_headers is not None:
            for h in extra_headers:
                headers.update([(h, extra_headers[h])])
        proxies = None
        if self.proxies:
            if hasattr(self.proxies, 'get_format'):
                proxies = self.proxies.get_format
            elif hasattr(self.proxies, 'format'):
                proxies = self.proxies.format
            else:
                proxies = str(self.proxies)
        response = self.session.request(method, url, params=params, data=data, timeout=timeout, verify=False,
                                        headers=headers, files=files, proxies=proxies, allow_redirects=True)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response

    def get(self, url, params=None, headers=None, timeout=10):
        """Encapsulate the get request method and disable SSL verification"""
        headers = headers or self.headers
        try:
            return self.request(url=url, method='GET', params=params, extra_headers=headers, timeout=timeout)
        except requests.exceptions.ProxyError:
            return None
        except requests.RequestException as error:
            if self._debug:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            return None

    def get_soup(self, url, params=None, headers=None, timeout=10):
        """Encapsulate the get request method and disable SSL verification"""
        headers = headers or self.headers
        try:
            req = self.request(url=url, method='GET', params=params, extra_headers=headers, timeout=timeout)
            return BeautifulSoup(req.text, "html.parser")
        except requests.exceptions.ProxyError:
            return None
        except requests.RequestException as error:
            if self._debug:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            return None

    def post(self, url, data=None, headers=None, timeout=10):
        """"Encapsulate the post method"""
        try:
            return self.request(url=url, method='POST', data=data, extra_headers=headers, timeout=timeout)
        except requests.exceptions.ProxyError:
            return None
        except requests.RequestException as error:
            if self._debug:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            return None

    def head(self, url, params=None, headers=None, timeout=10):
        """Encapsulate the get request method and disable SSL verification"""
        headers = headers or self.headers
        try:
            r = self.request(url=url, method='HEAD', params=params, extra_headers=headers, timeout=timeout)
            return r.status_code < 403
        except requests.exceptions.ProxyError:
            return None
        except requests.RequestException as error:
            if self._debug:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            return None

    def valid_image_url(self, url, params=None, headers=None, timeout=10):
        """Encapsulate the get request method and disable SSL verification"""
        headers = headers or self.headers
        try:
            r = self.request(url=url, method='HEAD', params=params, extra_headers=headers, timeout=timeout)
            return 'image' in str(r.headers.get('Content-Type'))
        except requests.exceptions.ProxyError:
            return None
        except requests.RequestException as error:
            if self._debug:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            return None

    @staticmethod
    def xpath(raw, xpath):
        """Support xpath for easy processing of web pages"""
        if not raw:
            return None
        try:
            return etree.HTML(raw).xpath(xpath)
        except etree.XPathError:
            return None

    @staticmethod
    def export_cookies(cookie: RequestsCookieJar, filename):
        try:
            with open(filename, 'wb+') as f:
                pickle.dump(cookie, f)
                f.close()
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            pass

    @staticmethod
    def load_cookies(session: Session, filename):
        try:
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    cookies = pickle.load(f)
                    session.cookies = cookies
                    f.close()
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            pass

    @staticmethod
    def blacklisted_domain(target: str) -> bool:
        try:
            for blacklist in BLACKLIST_DOMAIN:
                if target in str(blacklist):
                    return blacklist
                else:
                    # noinspection PyBroadException
                    try:
                        if re.compile(re.escape(blacklist)).search(target):
                            return blacklist
                    except Exception:
                        pass

        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        return False

    def me(self) -> str:
        return os.path.basename(self._me)[:-3]


class Spider(object):
    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        self.crawl = BaseCrawl()
        self.engines = self._load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.engines:
            self.engines.clear()
            self.engines = None
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        return True

    @staticmethod
    def _load() -> Dict:
        result = {}
        try:
            path_scripts = os.path.dirname(os.path.abspath(__file__))
            for sc in glob.glob('{}/**/*.py'.format(path_scripts), recursive=True):
                try:
                    if os.path.isfile(sc) and sc.endswith(".py") and not sc.endswith("__init__.py"):
                        sc_module = os.path.realpath(sc)
                        sc_module = sc_module[sc_module.find('spidery'):]
                        sc_type = os.path.basename(os.path.dirname(sc_module)).lower()
                        sc_mod = sc_module.replace(os.path.sep, os.path.extsep)[:-3]
                        module = importlib.import_module(sc_mod)
                        if not hasattr(module, 'Engine'):
                            continue
                        if sc_type not in result.keys():
                            result[sc_type] = []
                        result[sc_type].append(module)
                except Exception as error:
                    print(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        except Exception as error:
            logging.info(f'Failed loading scripts : {error}')
        finally:
            return result


class ProxyEngine(BaseCrawl):
    urls = []

    def __init__(self, **kwargs):
        super(ProxyEngine, self).__init__(**kwargs)

    def _fetch_url(self, url, **kwargs):
        flag = None
        try:
            response = self.get(url, **kwargs)
            if response and response.ok:
                response.encoding = 'utf-8'
                flag = response.text
        except requests.ConnectionError:
            pass
        finally:
            return str(flag)

    def _get_json(self, url, **kwargs):
        try:
            response = self.get(url, **kwargs)
            if response and response.ok:
                return response.json()
        except requests.ConnectionError:
            pass
            return

    def _parse_raw(self, html):
        try:
            march_group = re.findall(REGEX_PROXY, strip_html(html), re.IGNORECASE)
            for group in march_group:
                try:
                    host, port = group
                    yield ProxyData(**{
                        'host': host,
                        'port': port,
                        'country': None,
                        'type': 'https' if str(port) == '8080' else 'http',
                    })
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))

    def search(self):
        """
        crawl main method
        """
        for url in self.urls:
            logging.info(f'fetching {url}')
            html = self._fetch_url(url)
            for _ in self._parse_raw(html):
                try:
                    if not ipaddress.IPv4Address(_.host).is_private:
                        yield _
                except ValueError:
                    continue
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        logging.info(f'fetching complete')


class ProxyGrabber(object):
    _sources: Dict[str, ProxyEngine] = {}

    def __init__(self):
        self._load_modules()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

    def search(self, validate=None):
        result = []
        executor = ThreadPoolExecutor(max_workers=5)
        if self._sources:
            # noinspection PyUnresolvedReferences
            all_task = [executor.submit(source.search, ) for s, source in self._sources.items()]
            for task in as_completed(all_task):
                for _ in task.result():
                    if _ not in result:
                        result.append(_)
        if validate:
            validated = []
            try:
                validate = [executor.submit(self.check_proxy, p) for p in result]
                for task in as_completed(validate):
                    success, x = task.result()
                    if success:
                        validated.append(x)
            except Exception as error:
                logging.exception(
                    ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            finally:
                result = validated
        return result

    @property
    def scripts(self):
        return self._sources

    @staticmethod
    def check_proxy(proxy, **kwargs):
        flag = False
        default_type = proxy.type
        try:
            proxy_types = [
                'https',
                'socks4',
                'socks5',
            ]
            for typed in proxy_types:
                try:
                    proxy.type = typed
                    with BaseCrawl(proxies=proxy, **kwargs) as http:
                        req = http.get(url='https://get.geojs.io/v1/ip/geo.json', timeout=8)
                        data = req.json() if req and (req.json() and proxy.host in req.text) else None
                        if data:
                            data.update(proxy_type=proxy.type.upper())
                            flag = data
                            break
                except ValueError:
                    pass
                except Exception as error:
                    logging.error(error)
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            if not flag:
                proxy.type = default_type.upper()
            return flag

    def _load_modules(self):
        try:
            path_scripts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy")
            errors = []
            for sc in glob.glob('{}/*.py'.format(path_scripts)):
                if os.path.isfile(sc) and sc.endswith(".py") and not sc.endswith("__init__.py"):
                    sc_module = os.path.realpath(sc)
                    sc_module = sc_module[sc_module.find('spidery'):]
                    try:
                        sc_mod = sc_module.replace(os.path.sep, os.path.extsep)[:-3]
                        module = importlib.import_module(sc_mod)
                        if hasattr(module, 'Engine'):
                            mod = module.Engine()
                            self._sources.update({mod.me(): mod})
                    except Exception as error:
                        print(
                            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                        errors.append(sc_module)
                        logging.info(f'Failed loading script {sc_module} : {error}')
            if errors:
                raise KeyboardInterrupt('Cancelled.')
        except Exception as error:
            logging.info(f'Failed loading scripts : {error}')
