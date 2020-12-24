# -*- coding: utf-8 -*-
"""doc string"""

from pixivpy3 import AppPixivAPI as _Api

from .cache import cache as _cache
from .config import config as _cfg
from ..error import PixivFetcherError as _Err, ErrorCode as _Ec


class _LazyLoginAPI:
    def __init__(self):
        pass


def _make_api():
    ins = _Api()
    auth = _cache.get('auth')
    if auth is None:
        username = _cfg.get('account', 'username', fallback=None)
        password = _cfg.get('account', 'password', fallback=None)
        if username is None or password is None:
            raise _Err(_Ec.LoginError, 'missing USERNAME or PASSWORD in config')
        ins.login(
            username=username,
            password=password,
        )
        auth = {'user_id': ins.user_id,
                'access_token': ins.access_token,
                'refresh_token': ins.refresh_token}
        _cache.set('auth', auth)
        _cache.save('auth')
    else:
        ins.set_auth(
            access_token=auth['access_token'],
            refresh_token=auth['refresh_token'],
        )
    return ins


api = _make_api()


if __name__ == '__main__':
    pass
