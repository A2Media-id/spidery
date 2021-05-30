#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import json
import logging
import os
import re
import traceback
from string import ascii_lowercase
from typing import List

from lxml import html


def num_to_alpha(num):
    pairs = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
             '5': 'five', '6': 'six', '7': 'seven', '8': 'eight',
             '9': 'nine'}
    nums = []
    nums[:0] = str(num)
    return str(',').join(list(map(lambda x: pairs.get(x,x), nums)))


def strip_html(s):
    flag = s
    try:
        flag = html.fromstring(s.encode('utf-8')).text_content()
    except Exception as error:
        logging.error(
            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
    return str(flag)


def pad_infinite(iterable, padding=None):
    return itertools.chain(iterable, itertools.repeat(padding))


def pad(iterable, size, padding=None):
    return itertools.islice(pad_infinite(iterable, padding), size)


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(itertools.islice(it, size)), ())


def chunk_pad(it, size, padval=None):
    it = itertools.chain(iter(it), itertools.repeat(padval))
    return iter(lambda: tuple(itertools.islice(it, size)), (padval,) * size)


def write_file(out, data: str, mode='w+'):
    try:
        output_path = os.path.dirname(os.path.realpath(out))
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        with open(out, mode=mode, encoding='utf-8', errors='replace') as w:
            w.write('%s\n' % str(data), )
            w.close()
    except Exception as error:
        logging.error(
            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))


def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"

    return "".join(safe_char(c) for c in s).rstrip("_")


def get_tempfile_name(some_id):
    # noinspection PyUnresolvedReferences
    return os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + "_" + some_id)


def cap_sentence(s):
    return ''.join((c.upper() if prev == ' ' else c) for c, prev in zip(s, itertools.chain(' ', s)))


def sentence_caps(s):
    return re.sub(r"(\.\s+|^)(\w+)",
                  lambda m: m.group(1) + m.group(2).capitalize(),
                  s)


def sentence_cap(s):
    return str('').join(map(''.capitalize, re.split(r'(\s+)', s)))


def generate_random_alpha(length):
    import random
    return str(''.join([str(random.choice(list(ascii_lowercase))) for _ in range(length)]))


def generate_random_number(length=None):
    import random
    if not length:
        length = random.randint(1, 6)
    return int(''.join([str(random.randint(0, 10)) for _ in range(int(length))]))


def generate_random_dot():
    import random
    return random.choice(['.', ''])


def psrange(prefix, suffix, high):
    return ('%s%d%s' % (prefix, i, s) for i in range(1, 1 + high) for s in suffix)


def remove_all_char_before(string, prefix='.'):
    return '{}{}'.format(prefix, string.split(prefix).pop())


def dedup_dicts(items: List[dict]):
    dedupped = [json.loads(i) for i in set(json.dumps(item, sort_keys=True) for item in items)]
    return dedupped


def read_file_by_chunk(filename, chunk_size=1024):
    try:
        with open(filename, mode='r', encoding='utf-8', errors='replace') as fp:
            while True:
                buff = list(itertools.islice(fp, chunk_size))
                if buff:
                    yield [line.strip('\n') for line in buff if len(line)]
                else:
                    break
            fp.close()
    except Exception as error:
        logging.exception(
            ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        pass


def deemoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", re.UNICODE)
    return re.sub(emoji_pattern, '', text)
