# -*- coding: utf-8 -*-
"""doc string"""

import os as _os
import operator as _operator
from concurrent.futures.thread import ThreadPoolExecutor as _Pool
from functools import partial as _partial, reduce as _reduce

from src.extensions import config as _cfg

_default_file_name_rule = '{user.id}-{image.id}'
_default_dst_dir_rule = r'download\{user.name}'


def default_file_name_rule():
    return _cfg.get('download', 'file_name_rule', fallback=_default_file_name_rule)


def default_dst_dir_rule():
    return _cfg.get('download', 'dst_dir_rule', fallback=_default_dst_dir_rule)


def file_name_from_rule(rule, user, image):
    r = rule or default_file_name_rule()
    file_name_str = f'f{repr(r)}'
    local = dict(user=user, image=image)
    return eval(file_name_str, dict(), local)


def dst_dir_from_rule(rule, user):
    r = rule or default_dst_dir_rule()
    dst_dir_str = f'f{repr(r)}'
    local = dict(user=user)
    dst_dir = eval(dst_dir_str, dict(), local)
    src_dir = _os.path.dirname(__file__)
    rel_dir = _os.path.join(src_dir, '..', dst_dir)
    full_dir = _os.path.abspath(rel_dir)
    if not _os.path.exists(full_dir):
        _os.makedirs(full_dir)
    return full_dir


def download_image(image_list, user, file_name_rule, dst_dir_rule, size, replace, mode):
    if mode == 'normal':
        download_func = _download_image_normal
    elif mode == 'thread':
        download_func = _download_image_thread
    else:
        raise ValueError(f'invalid download mode {mode}')
    param_tuple = (user, file_name_rule, dst_dir_rule, size, replace)
    res = download_func(image_list, param_tuple)
    return _reduce(_operator.and_, res, True)


def _download_image(image, param_tuple):
    user, file_name_rule, dst_dir_rule, size, replace = param_tuple
    return image.download(
        file_name=file_name_rule,
        dst_dir=dst_dir_rule,
        size=size,
        replace=replace,
    )


def _download_image_normal(image_list, param_tuple):
    return [_download_image(image, param_tuple) for image in image_list]


def _download_image_thread(image_list, param_tuple):
    # unpack to ensure dst dir (create if missing) before starting threads
    user, file_name_rule, dst_dir_rule, size, replace = param_tuple
    dst_dir = dst_dir_from_rule(dst_dir_rule, user)
    # after checking, pack params again and make thread pool
    param_tuple = (user, file_name_rule, dst_dir, size, replace)
    executor = _Pool(max_workers=_cfg.getint('download', 'max_thread'))
    download_func = _partial(_download_image, param_tuple=param_tuple)
    return [res for res in executor.map(download_func, image_list)]


def image_type_for_query(image_type):
    return 'illust' if image_type == 'ugoira' else image_type


def ugoira_meta_data(api, image_id):
    url = '%s/v1/ugoira/metadata' % api.hosts
    params = {
        'illust_id': image_id,
    }
    r = api.no_auth_requests_call('GET', url, params=params, req_auth=True)
    return api.parse_result(r)


if __name__ == '__main__':
    pass
