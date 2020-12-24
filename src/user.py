# -*- coding: utf-8 -*-
"""doc string"""

from .extensions import api as _api
from .error import PixivFetcherError as _Err, ErrorCode as _Ec
from . import utils as _utils


class User(object):
    id = property(lambda self: self.__id)
    name = property(lambda self: self.__name)
    comment = property(lambda self: self.__comment)

    def __init__(self, user_id=None, user_name=None, comment=None):
        self.__id = user_id
        self.__name = user_name
        self.__comment = comment

    @classmethod
    def from_info(cls, user_info):
        return cls(
            user_id=user_info.id,
            user_name=user_info.name,
            comment=user_info.comment,
        )

    @classmethod
    def get(cls, user_id=None, user_name=None):
        if user_id is not None:
            res = _api.user_detail(user_id=user_id)
            if res.error:
                raise _Err(_Ec.UserNotFound, f'ID={user_id}')
            return cls.from_info(res.user)
        elif user_name is not None:
            res = _api.search_user(word=user_name)
            if not res.user_previews:
                raise _Err(_Ec.UserNotFound, f'Name={user_name}')
            return cls.from_info(res.user_previews[0].user)
        else:
            raise _Err(_Ec.MissingArgument, "'user_id or 'user_name'")

    def images(self, image_type='illust'):
        from .image import Image
        kwargs = {'user_id': self.id, 'type': _utils.image_type_for_query(image_type)}
        res = []
        while True:
            response = _api.user_illusts(**kwargs)
            res.extend([Image.from_info(image_info, user=self)
                        for image_info in response.illusts])
            if response.next_url is None:
                break
            kwargs = _api.parse_qs(response.next_url)
        filtered = [img for img in res if img.type == image_type]  # filter ugoira from illust
        return filtered

    def __str__(self):
        return f'<User:id={self.id},name={self.name}>'


if __name__ == '__main__':
    pass
