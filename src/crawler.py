# -*- coding: utf-8 -*-
"""doc string"""

from .user import User as _User
from . import utils as _utils


class Crawler:
    pass


def download_user(
        user_id,
        image_type='illust',
        file_name_rule=None,
        dst_dir_rule=None,
        size='original',
        replace=False,
        download_mode='thread',
):
    """
    download all images of the given user
    :param user_id: pixiv user ID [int]
    :param image_type: type or types of images to be downloaded [str]
        valid values:
            illust
            manga
            ugoira
        default: illust
        for multiple types, input one string with single comma between each type
        e.x. illust,manga
        ugoira downloading is slow (one ugoira can only be downloaded in one thread)
        when multiple types required, it is suggested to put ugoira at first
    :param file_name_rule: rule to generate file name for each image [str]
        use {} to add properties of user or image to file name
        useful properties: user.id, user.name, image.id, image.title
        default: [download]
    :param dst_dir_rule: rule to generate destination directory for image files [str]
        use {} to add properties of user to directory relative path
        default: [download] dst_dir_rule in config.ini
    :param size: size of images to be downloaded [str]
        valid values:
            square_medium
            medium
            large
            original
        default: original
    :param download_mode: mode to download image files [str]
        valid values:
            normal: sequential downloading
            thread: multi-thread downloading
                maximum thread is set in [download] max_thread in config.ini
        default: thread
    :param replace: override existing file or not (same file name) [bool]
        default: False
    :return: all success or not [bool]
    """
    user = _User.get(user_id=user_id)
    image_types = image_type.split(',')
    image_list = []
    for each_type in image_types:
        clean_type = each_type.strip()
        image_list.extend(
            user.images(image_type=clean_type)
        )
    res = _utils.download_image(
        image_list=image_list,
        user=user,
        file_name_rule=file_name_rule,
        dst_dir_rule=dst_dir_rule,
        size=size,
        replace=replace,
        mode=download_mode,
    )
    return res


if __name__ == '__main__':
    pass
