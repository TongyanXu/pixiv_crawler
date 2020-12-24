# -*- coding: utf-8 -*-
"""doc string"""

import imageio as _imageio
import math as _math
import os as _os
import shutil as _shutil

from .extensions import api as _api, config as _cfg
from .error import PixivFetcherError as _Err, ErrorCode as _Ec
from . import utils as _utils


class ImageUrl(object):
    square_medium = property(lambda self: self.__square_medium)
    medium = property(lambda self: self.__medium)
    large = property(lambda self: self.__large)
    original = property(lambda self: self.__original)

    def __init__(self, square_medium=None, medium=None, large=None, original=None):
        self.__square_medium = square_medium
        self.__medium = medium
        self.__large = large
        self.__original = original

    @classmethod
    def from_info(cls, image_url):
        return cls(
            square_medium=image_url['square_medium'],
            medium=image_url['medium'],
            large=image_url['large'],
            original=image_url['original'],
        )

    def get_url(self, size):
        if not hasattr(self, size):
            raise _Err(_Ec.InvalidImageSize, size)
        return getattr(self, size)

    def get_file_name(self, size):
        url = self.get_url(size)
        return _os.path.basename(url)

    def get_file_extension(self, size):
        url = self.get_url(size)
        return _os.path.splitext(url)[1]

    def get_ugoira_template(self, size):
        url = self.get_url(size)
        split_url = _os.path.splitext(url)
        inner_str = '{i}'
        return f'{split_url[0][:-1]}{inner_str}{split_url[1]}'


class Image(object):
    id = property(lambda self: self.__id)
    title = property(lambda self: self.__title)
    type = property(lambda self: self.__type)
    urls = property(lambda self: self.__urls)
    user = property(lambda self: self.__user)
    caption = property(lambda self: self.__caption)
    tags = property(lambda self: self.__tags)
    create_date = property(lambda self: self.__create_date)
    page_count = property(lambda self: self.__page_count)
    width = property(lambda self: self.__width)
    height = property(lambda self: self.__height)
    total_view = property(lambda self: self.__total_view)
    total_bookmarks = property(lambda self: self.__total_bookmarks)
    total_comments = property(lambda self: self.__total_comments)

    def __init__(self, image_id=None, image_title=None, image_type='illust', image_urls=None,
                 user=None, caption=None, tags=None, create_date=None, page_count=None,
                 width=None, height=None, total_view=None, total_bookmarks=None, total_comments=None):
        self.__id = image_id
        self.__title = image_title
        self.__type = image_type
        self.__urls = image_urls
        self.__user = user
        self.__caption = caption
        self.__tags = tags
        self.__create_date = create_date
        self.__page_count = page_count
        self.__width = width
        self.__height = height
        self.__total_view = total_view
        self.__total_bookmarks = total_bookmarks
        self.__total_comments = total_comments

    @staticmethod
    def __extract_image_urls(image_info):
        if image_info.page_count == 1:
            image_url = image_info.image_urls.copy()
            image_url['original'] = image_info.meta_single_page['original_image_url']
            image_urls = [ImageUrl.from_info(image_url)]
        else:
            image_urls = [ImageUrl.from_info(each['image_urls']) for each in image_info.meta_pages]
        return image_urls

    @classmethod
    def from_info(cls, image_info, user=None):
        if user is None:
            from .user import User
            user = User.from_info(image_info.user)
        return cls(
            image_id=image_info.id,
            image_title=image_info.title,
            image_type=image_info.type,
            image_urls=cls.__extract_image_urls(image_info),
            user=user,
            caption=image_info.caption,
            tags=image_info.type,
            create_date=image_info.create_date,
            page_count=image_info.page_count,
            width=image_info.width,
            height=image_info.height,
            total_view=image_info.total_view,
            total_bookmarks=image_info.total_bookmarks,
            total_comments=image_info.total_comments,
        )

    @classmethod
    def get(cls, image_id=None, image_title=None):
        if image_id is not None:
            res = _api.illust_detail(illust_id=image_id)
            if res.error:
                raise _Err(_Ec.ImageNotFound, f'ID={image_id}')
            return cls.from_info(res.illust)
        elif image_title is not None:
            res = _api.search_illust(word=image_title)
            if not res.illusts:
                raise _Err(_Ec.ImageNotFound, f'Title={image_title}')
            return cls.from_info(res.illusts[0])
        else:
            raise _Err(_Ec.MissingArgument, "'image_id or 'image_title'")

    def download(self, file_name=None, dst_dir=None, size='original', replace=False):
        file_name = _utils.file_name_from_rule(file_name, self.user, self)
        dst_dir = _utils.dst_dir_from_rule(dst_dir, self.user)
        if self.type in ['illust', 'manga']:
            return self._normal_download(file_name, dst_dir, size, replace)
        elif self.type in ['ugoira']:
            return self._ugoira_download(file_name, dst_dir, size, replace)
        raise _Err(_Ec.ImageTypeNotSupported, str(self))

    def _normal_download(self, file_name, dst_dir, size, replace):
        succeed = True
        for idx, url in enumerate(self.urls):
            suffix = f'(p{self.__page_index_str(idx)})' if self.page_count > 1 else ''
            full_name = f'{file_name}{suffix}{url.get_file_extension(size)}'
            file_path = _os.path.join(dst_dir, full_name)
            succeed &= self.__download(url.get_url(size), file_path, replace)
        return succeed

    def _ugoira_download(self, file_name, dst_dir, size, replace):
        if len(self.urls) != 1:
            raise _Err(_Ec.ImageUrlNotSupported, 'multiple url for ugoira')
        gif_path = _os.path.join(dst_dir, f'{file_name}.gif')
        if not _os.path.exists(gif_path) or replace:
            url = self.urls[0]
            extension = url.get_file_extension(size)
            url_template = self.urls[0].get_ugoira_template(size)
            sub_dir = fr'{dst_dir}\{file_name}'
            if not _os.path.exists(sub_dir):
                _os.mkdir(sub_dir)
            meta_data = _utils.ugoira_meta_data(_api, self.id).ugoira_metadata
            pic_count = len(meta_data.frames)
            duration = meta_data.frames[0].delay / 1000
            frames = []
            for i in range(pic_count):
                full_name = f'{file_name}{i}{extension}'
                file_path = _os.path.join(sub_dir, full_name)
                self.__download(url_template.format(i=i), file_path, replace)
                frames.append(_imageio.imread(file_path))
            _imageio.mimsave(gif_path, frames, 'GIF', duration=duration)
            _shutil.rmtree(sub_dir)
        return True

    @staticmethod
    def __download(url, path, replace):
        if _os.path.exists(path) and not replace:
            return True
        print(path)
        retry = _cfg.getint('download', 'retry', fallback=0)
        for i in range(retry + 1):
            try:
                referer = 'https://app-api.pixiv.net/'
                response = _api.requests_call('GET', url, headers={'Referer': referer}, stream=True)
                if response.status_code != 200:
                    continue
                with open(path, 'wb') as out_file:
                    _shutil.copyfileobj(response.raw, out_file)
                del response
            except Exception as e:
                _ = e
            else:
                return True
        return False

    def __page_index_str(self, page_index):
        num = int(_math.log10(self.page_count - 1)) + 1
        return ('0' * num + str(page_index))[-num:]

    def __str__(self):
        return f'<Image:id={self.id},title={self.title},' \
               f'type={self.type},count={self.page_count}>'


if __name__ == '__main__':
    pass
