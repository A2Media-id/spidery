#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os.path
import pickle
import random
import re
import traceback

from spidery.utils.func import write_file, cap_sentence, num_to_alpha
from .device_type import DeviceType

UA_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ua.bin')


class Agent:
    user_agents = pickle.load(open(UA_BIN, 'rb'))

    def __init__(self, **kwargs):
        params = {
            'name': kwargs.get('name', None),
            'brand': kwargs.get('brand', None),
            'brand_code': kwargs.get('brand_code', None),
            'code': kwargs.get('code', None),
            'type': kwargs.get('type', DeviceType.BROWSER),
            'category': kwargs.get('category', None),
            'engine': kwargs.get('engine', None),
            'family': kwargs.get('family', None),
            'family_code': kwargs.get('family_code', None),
            'family_vendor': kwargs.get('family_vendor', None),
            'is_crawler': kwargs.get('is_crawler', False),
        }

        self._filtered = self._parse_kwargs(**params)

    def get_random(self):
        return random.choice(self._filtered) if len(self._filtered) else None

    def __gen_class__(self):
        C_K = {}
        C_C = {}
        for i, x in enumerate(self.user_agents):
            for kk, kv in x.items():
                print({type(kv): kv})
                C_K[kk] = C_K.get(kk) if kk in C_K.keys() else set()
                if type(kv) == str and kv:
                    C_K[kk].add(kv)
                if type(kv) == dict:
                    for ck, cv in kv.items():
                        C_C[ck] = C_C.get(ck) if ck in C_C.keys() else set()
                        if type(cv) == str and cv:
                            C_C[ck].add(cv)
        print(C_C.keys())
        write_file('A.txt', str('\n').join(C_K.keys()))
        for k, v in C_K.items():
            if len(v):
                write_file(f'A-{k}.txt', str('\n').join(list(v)))

        write_file('B.txt', str('\n').join(C_C.keys()))
        for k, v in C_C.items():
            if len(v):
                write_file(f'B-{k}.txt', str('\n').join(list(v)))

        al = ['A.txt', 'B.txt']
        for x in al:
            print(x)
            if os.path.isfile(x):
                ls = open(x).read().splitlines()
                h = x.rstrip('.txt')
                for c in ls:
                    cx = f'{h}-{c}.txt'
                    print({cx: os.path.isfile(cx)})
                    if os.path.isfile(cx):
                        ad = str(re.sub("[^0-9a-zA-Z]", " ", c, 0, re.IGNORECASE)).capitalize()
                        ad = str(re.sub("[^0-9a-zA-Z]", "", cap_sentence(ad.strip()), 0, re.IGNORECASE))
                        an = str(re.sub("[^0-9a-zA-Z]", "_", c, 0, re.IGNORECASE))
                        fn = f'{str(an).lower()}.py'
                        ss = open(cx).read().splitlines()
                        aa = f"""from enum import Enum\n\nclass {ad}(Enum):"""
                        cuks = set()
                        for ln in ss:
                            cuk = str(re.sub("[^0-9a-zA-Z]", "_", ln, 0, re.IGNORECASE)).upper()
                            if cuk in cuks:
                                continue
                            match = re.search(r"^(\d+)([^\n]+)?", cuk, re.IGNORECASE)
                            if match:
                                c_a, c_b = match.groups()
                                mod = str('_').join(num_to_alpha(c_a).split(','))
                                mods = [mod,
                                        str(re.sub("[^0-9a-zA-Z]", "_", c_b, 0, re.IGNORECASE)).upper()] if c_b else [
                                    mod]
                                cuk = str('_').join(mods).upper()
                            cuk = re.sub("(_){1,}", r"\1", cuk, 0, re.IGNORECASE)
                            aa += f"""\n\t{cuk}='{ln}'"""
                            cuks.add(cuk)
                        write_file(fn, aa)

    def _parse_kwargs(self, **kwargs):
        flag = []
        try:
            current = self.user_agents
            for k, v in kwargs.items():
                try:
                    v = v.value if hasattr(v, 'value') else v
                    if v is None:
                        continue
                    if type(v) == bool:
                        filtered = []
                        for x in current:
                            for vv in x.values():
                                if type(vv) == dict and k in vv.keys():
                                    if vv[k] == v:
                                        filtered.append(x)

                    else:
                        filtered = [x for x in current if
                                    k in x.keys() and x[k] and (
                                        v in x[k].values() if type(x[k]) == dict else x[k] == v)]
                    current = filtered
                except Exception as error:
                    logging.exception(
                        ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            flag = [x.get('ua') for x in current]
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        finally:
            return flag


if __name__ == '__main__':
    ag = Agent()
    print(ag.get_random())
    print(ag.get_random())
