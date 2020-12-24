# -*- coding: utf-8 -*-
"""doc string"""

import os as _os
import json as _json
import datetime as _datetime

from .config import config as _cfg


class _Cache(object):
    __dt_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        self.__cache = {}

    def get(self, cache_key):
        if cache_key not in self.__cache:
            self.__load(cache_key)
        if cache_key not in self.__cache:
            return None
        return self.__validate(cache_key)

    def set(self, cache_key, cache_value):
        now = _datetime.datetime.now()
        self.__cache[cache_key] = dict(
            time=now.strftime(self.__dt_format),
            value=cache_value,
        )

    def save(self, cache_key=None):
        if cache_key is None:
            for key in self.__cache:
                self.__save(key)
        elif cache_key in self.__cache:
            self.__save(cache_key)

    @staticmethod
    def __file(cache_key):
        return _os.path.join(
            _os.path.dirname(__file__),
            fr'..\..\cache\{cache_key}.json',
        )

    def __load(self, cache_key):
        if _os.path.exists(self.__file(cache_key)):
            with open(self.__file(cache_key)) as f:
                self.__cache[cache_key] = _json.loads(f.read())

    def __save(self, cache_key):
        with open(self.__file(cache_key), 'w') as f:
            f.write(_json.dumps(self.__cache[cache_key]))

    def __validate(self, cache_key):
        cache_dict = self.__cache[cache_key]
        cache_time = _datetime.datetime.strptime(
            cache_dict['time'], self.__dt_format)
        time_delta = _datetime.datetime.now() - cache_time
        default_time_out = _cfg.get('cache', 'timeout')
        timeout = _cfg.get('cache', f'timeout_{cache_key}',
                           fallback=default_time_out)
        if time_delta < self.__timeout_to_timedelta(timeout):
            return cache_dict['value']
        return None

    @staticmethod
    def __timeout_to_timedelta(timeout):
        mapping = [('w', 'weeks'),
                   ('d', 'days'),
                   ('h', 'hours'),
                   ('m', 'minutes'),
                   ('s', 'seconds')]
        try:
            for s, k in mapping:
                if timeout.endswith(s):
                    num = float(timeout[:-len(s)])
                    return _datetime.timedelta(**{k: num})
        except Exception:
            raise ValueError(f"invalid timeout {timeout}")


cache = _Cache()


if __name__ == '__main__':
    pass
