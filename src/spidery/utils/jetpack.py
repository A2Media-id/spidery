#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import random
import re
import traceback
from urllib.parse import urlparse, ParseResult, urlencode


class Photon(object):
    """* Parameter    Description    Usage
		 * w    width (defaults to px, supports %)    w=50
		 * h    height (defaults to px, supports %)    h=50
		 * crop    crop x,y,w,h (defaults to %)    crop=5,10,20,40
		 * resize    resize and crop to given dimensions (px)    resize=250,300
		 * fit    keep aspect ratio, but fit to within given box (px)    fit=100,100
		 * lb    add letterboxing, color code is optional (it’s black by default)    lb=300,250,1A4E9F
		 * ulb    remove letterboxing (auto detects the letterbox color)    ulb=true
		 * filter    apply various imagefilter() filters    filter=grayscale
		 * brightness    adjusts brightness    brightness=100
		 * contrast    adjusts contrast    contrast=50
		 * colorize    applies a color hue    colorize=255,0,0
		 * smooth    smoothes out the image    smooth=2
		 * zoom    size images for high pixel ratio devices    zoom=2
		 * quality    sets the quality for JPEG images    quality=50
		 * strip    removes metadata from JPEG images    strip=all
		 *
		 * @link  https://developer.wordpress.com/docs/photon/api/"""

    EXCLUDES = [
        'deviantart.net'
    ]

    def __init__(self, url_original: str, **kwargs):
        self.query = {
            'w': kwargs.get('w'),
            'h': kwargs.get('h'),
            'crop': kwargs.get('crop'),
            'resize': kwargs.get('resize'),
            'lb': kwargs.get('lb'),
            'ulb': kwargs.get('ulb', True),
            'filter': kwargs.get('filter'),
            'brightness': kwargs.get('brightness'),
            'contrast': kwargs.get('contrast'),
            'colorize': kwargs.get('colorize'),
            'smooth': kwargs.get('smooth'),
            'zoom': kwargs.get('zoom'),
            'quality': kwargs.get('quality', 100),
            'strip': kwargs.get('strip', 'all'),
        }
        self.url_original = url_original
        self.url = url_original
        if not self._excludes(self.url_original):
            self._make()

    def _make(self):
        try:
            query = {k: v for k, v in self.query.items() if v is not None}
            parsed: ParseResult = urlparse(self.url_original)

            if re.search(r"i\d\.wp\.com", self.url_original, re.IGNORECASE | re.VERBOSE | re.MULTILINE):
                modified: ParseResult = parsed._replace(query=urlencode(query))
            else:
                modified: ParseResult = parsed._replace(netloc='i{0}.wp.com'.format(random.randint(0, 3)),
                                                        query=urlencode(query))
                modified = modified._replace(
                    path=str('/').join([str(parsed.netloc).rstrip('/'), str(parsed.path).lstrip('/')]))
            self.url = modified.geturl()
        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))

    def __repr__(self) -> str:
        return str(self.url).strip()

    def _excludes(self, target: str) -> bool:
        try:
            for blacklist in self.EXCLUDES:
                if target in str(blacklist):
                    return True
                else:
                    # noinspection PyBroadException
                    try:
                        if re.compile(re.escape(blacklist)).search(target):
                            return True
                    except Exception:
                        pass

        except Exception as error:
            logging.exception(
                ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
        return False


if __name__ == '__main__':
    # Actually run the application
    url = Photon(
        'https://obs.line-scdn.net/0hPAe7hIVaD25YThmjPNZwOWIYDAFrIhxtPHhecAggUVl0Lhg_bHoXWHtGUAslfkgwMSlIDH5JFF8gKk8wZXsX',
        strip='all')  # returns url sections as a dict
    print(str(url))
